import config
import heapq
import uuid

class BlockDefinition:
    def __init__(self, blockID, fileID, fileIndex):
        self.blockID = blockID
        self.fileID = fileID
        self.fileIndex = fileIndex

class SeverDefinition:
    def __init__(self, severName, validBlock):
        self.severName = severName
        self.validBlock = validBlock
        self.blockInfo = []

    def __cmp__(self, other):
        assert other
        if not isinstance(other, SeverDefinition):
            raise TypeError
        return -cmp(self.validBlock, other.validBlock)

class SeverManager:
    def __init__(self):
        self.severHeap = []

    def addSever(self, severName, validBlock):
        severDef = SeverDefinition(severName, validBlock)
        heapq.heappush(self.severHeap, severDef)

    def isAvailable(self, needBlockNum):
        allNeedBlock = config.Redundancy * needBlockNum
        validBlockList = [severDef.validBlock for severDef in self.severHeap]
        i = 0
        while i < len(validBlockList):
            allNeedBlock -= min(needBlockNum, validBlockList[i])
            i += 1
        if allNeedBlock <= 0:
            return True
        else:
            return False

    def addFile(self, fileID, fileSize, blockSize, startIndex):
        if blockSize != config.BlockSize:
            return 0
        blockNum = (fileSize + blockSize - 1) / blockSize
        if not self.isAvailable(blockNum):
            return 1
        res = {"fid" : fileID, "block_num" : blockNum, "block_list" : []}
        for i in range(blockNum):
            blockID = uuid.uuid1().get_hex()
            res["block_list"].append({"severs":[], "bid":blockID, "index":i+startIndex})
            tmp = []
            for j in range(config.Redundancy):
                severDef = heapq.heappop(self.severHeap)
                severDef.validBlock -= 1
                fileBlock = BlockDefinition(blockID, fileID, i+startIndex)
                severDef.blockInfo.append(fileBlock)
                res["block_list"][i]["severs"].append(severDef.severName)
                tmp.append(severDef)
            for j in range(config.Redundancy):
                heapq.heappush(self.severHeap, tmp[j])
        return res

if __name__ == "__main__":
    a = SeverManager()
    a.addSever("192.168.0.1:2000",20)
    a.addSever("192.168.0.1:2001",40)
    a.addSever("192.168.0.1:2002",5)
    res = a.addFile("blabla", 4*1024*1024*64, 64*1024*1024, 5)
    
    print res
