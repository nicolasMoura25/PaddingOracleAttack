import urllib2
import time

TARGET = 'http://crypto-class.appspot.com/po?er='
CYPHER = "f20bdba6ff29eed7b046d1df9fb7000058b1ffb4210a580f748b4ac714c001bd4a61044426fb515dad3f21f18aa577c0bdf302936266926ff37dbf7035d5eeb4".decode("hex").strip()
BLOCK_SIZE = 16 # size of decrypted block: len(CYPHER) / 4
NR_OF_ITERATIONS = 3

#--------------------------------------------------------------
# padding oracle
#--------------------------------------------------------------
class PaddingOracle(object):
    def query(self, q):
        target = TARGET + urllib2.quote(q)    # Create query URL
        req = urllib2.Request(target)         # Send HTTP request to server
        try:
            f = urllib2.urlopen(req)          # Wait for response
        except urllib2.HTTPError as e:
            #print "We got: %d" % e.code       # Print response code
            if e.code == 404:
                return True # good padding

            return False # bad padding

def strxor(a, b, c = None):
	if c:
		return strxor(strxor(a, b), c)
	assert len(a) == len(b)
	return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b)])

def PaddingGenerate(index):
    padding = list("00000000000000000000000000000000".strip())

    pos = 32 - (index * 2)
    for i in range (index):
        indexToHex = list(IntToFormattedHexString(index).strip())
        padding[pos] = indexToHex[0]
        padding[pos + 1] = indexToHex[1]
        pos = pos + 2

    return "".join(padding)

def GetCypherQuadrant(quadrant):
    # split CYPHER (which has 64 bits) into 4 quadrants, of 16 bits each, and return the requested quadrant
    return CYPHER[BLOCK_SIZE * quadrant : BLOCK_SIZE * quadrant + BLOCK_SIZE]

def IntToFormattedHexString(i):
    return str(hex(i))[2:].zfill(2)

if __name__ == "__main__":
    blockDecodeList = ["00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00"]
    asciiList = [IntToFormattedHexString(x) for x in range(2, 256)]
    currentCypherQuadrant = 3
    paddingOracle = PaddingOracle()
    blockPlainText = ""

    start_time = time.time()
    print("total duration: %s seconds" % (time.time() - start_time))
    for iteration in range(NR_OF_ITERATIONS):
        previousCipher = GetCypherQuadrant(currentCypherQuadrant - 1)
        cipher = GetCypherQuadrant(currentCypherQuadrant)

        for blockPos in range(1, len(blockDecodeList) + 1):
            padding = PaddingGenerate(blockPos)

            # brute force attempts
            for currentByte in asciiList: # 0x02 to 0xff
                # iterating from right to left
                currentPos = len(blockDecodeList) - blockPos
                blockDecodeList[currentPos] = currentByte
                print blockDecodeList

                plainText = "".join(blockDecodeList)

                # 32 characters
                xorOfQuadrants = strxor(previousCipher, padding.decode("hex"), plainText.decode("hex")) + cipher

                # found correct character
                if paddingOracle.query(xorOfQuadrants.encode("hex")):
                    blockDecodeList[currentPos] = currentByte # Issue HTTP query with the given argument
                    break

        blockPlainText = plainText + blockPlainText
        print blockPlainText

        # clear list to iterate again
        blockDecodeList = ["00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00", "00"]
        currentCypherQuadrant = currentCypherQuadrant - 1

    # print current decoded blocks to ascii
    stringSplittedInBytes = [blockPlainText[index : index + 2] for index in range(0, len(blockPlainText), 2)]
    print "".join(stringSplittedInBytes).decode("hex")

    print("total duration: %s seconds" % (time.time() - start_time))

