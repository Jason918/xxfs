import config
import heapq
import uuid

class BlockDefinition:
    def __init__(self, blockID, fileID, fileIndex):
        self.blockID = blockID
        self.fileID = fileID
        self.fileIndex = fileIndex

class ServerDefinition:
    def __init__(self, serverName, validBlock):
        self.serverName = serverName
        self.validBlock = validBlock
        self.blockInfo = []

    def __cmp__(self, other):
        assert other
        if not isinstance(other, ServerDefinition):
            raise TypeError
        return -cmp(self.validBlock, other.validBlock)

class ServerManager:
    def __init__(self):
        self.serverHeap = []

    def addServer(self, serverName, validBlock):
        alreadyAdd = False
        for server in self.serverHeap:
            if server.serverName == serverName:
                alreadyAdd = True
        if not alreadyAdd:
            serverDef = ServerDefinition(serverName, validBlock)
            heapq.heappush(self.serverHeap, serverDef)

    def isAvailable(self, needBlockNum):
        allNeedBlock = config.Redundancy * needBlockNum
        validBlockList = [serverDef.validBlock for serverDef in self.serverHeap]
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
            res["block_list"].append({"servers":[], "bid":blockID, "index":i})
            tmp = []
            for j in range(config.Redundancy):
                serverDef = heapq.heappop(self.serverHeap)
                serverDef.validBlock -= 1
                fileBlock = BlockDefinition(blockID, fileID, i+startIndex)
                serverDef.blockInfo.append(fileBlock)
                res["block_list"][i]["servers"].append(serverDef.serverName)
                tmp.append(serverDef)
            for j in range(config.Redundancy):
                heapq.heappush(self.serverHeap, tmp[j])
        return res

    def getServerInfo(self, serverName):
        for server in self.serverHeap:
            if serverName == server.serverName:
                return server.blockInfo

    def removeServer(self, serverName):
        self.serverHeap = [server for server in self.serverHeap if server.serverName != serverName]
        heapq.heapify(self.serverHeap)
    
    def isTransfer(self, transData):
        serverCopy = []
        for server in self.serverHeap:
            serverCopy.append({"validBlock":server.validBlock, "serverName":server.serverName})
        for block in transData:
            thisBlock = False
            for server in serverCopy:
                if not server["serverName"] in block["servers"] and server["validBlock"] > 0:
                    server["validBlock"] -= 1
                    thisBlock = True
                    break
            if not thisBlock:
                return False
        return True

    def transfer(self, transData):
        if not self.isTransfer(transData):
            return
        else:
            res = []
            for block in transData:
                tmp = []
                server = heapq.heappop(self.serverHeap)
                while server.serverName in block["servers"]:
                    tmp.append(server)
                    server = heapq.heappop(self.serverHeap)
                tmp.append(server)
                server.validBlock -= 1
                server.blockInfo.append(BlockDefinition(block["bid"], block["fid"], block["index"]))
                res.append(server.serverName)
                for tmpServer in tmp:
                    heapq.heappush(self.serverHeap, tmpServer)
            return res

if __name__ == "__main__":
    a = ServerManager()
    a.addServer("192.168.0.1:2000",20)
    a.addServer("192.168.0.1:2001",40)
    a.addServer("192.168.0.1:2002",5)
    res = a.addFile("blabla", 4*1024*128, 128*1024, 5)
    print res
    res = a.getServerInfo("192.168.0.1:2002")
    print res
