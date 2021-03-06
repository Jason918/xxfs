#coding=utf-8
import treelib
import server_manager
import time
import threading
import heapq
import requests
import config


#class DirNode:
#    "init"
#    def __init__(self):
#        self.isTrash = False
#
#class FileNode:
#    def __init__(self, fileID, blockNum, blockList):
#        self.fid = fileID
#        self.isTrash = Fasle
#        self.blockNum = blockNum
#        self.blockList = blockList
class ServerHeartBeat:
    def __init__(self, serverName, timeStamp):
        self.serverName = serverName
        self.timeStamp = timeStamp

    def __cmp__(self, other):
        assert other
        if not isinstance(other, ServerHeartBeat):
            raise TypeError
        return cmp(self.timeStamp, other.timeStamp)

class HeartBeatChecker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            mutex.acquire()
            # print "checking HB"
            if len(naming_server.heartBeatQueue) != 0:
                nowTime = int(time.time())
                server = heapq.heappop(naming_server.heartBeatQueue)
                if nowTime - server.timeStamp > config.HeartBeatTime:
                    print server.serverName
                    url = "http://"+config.NamingServer+"/storage_server"
                    param = {
                        "server_name":server.serverName,
                        'type':'storage_server'
                    }
                    requests.delete(url, params = param)
                else:
                    heapq.heappush(naming_server.heartBeatQueue, server)
            mutex.release()
            time.sleep(1)

mutex = threading.Lock()
class NamingServer:
    dirPrefix = "dir_"
    filePrefix = "file_"
    treeRoot = "dir_root"
    global mutex

    """init"""
    def __init__(self):
        self.namingTree = treelib.Tree()
        self.namingTree.create_node(self.treeRoot, self.treeRoot)
        self.serverManager = server_manager.ServerManager()
        self.heartBeatQueue = [] 

    def getFileID(self, allPath, fileName):
        fileID = self.treeRoot + '/' + '/'.join([self.dirPrefix + path for path in allPath.split('/')]) + '/' + self.filePrefix + fileName
        return fileID

    def getPathID(self, allPath):
        pathID = self.treeRoot + '/' + '/'.join([self.dirPrefix + path for path in allPath.split('/')])
        return pathID

    """get a hreart beat"""
    def getHeartBeat(self, serverName):
        mutex.acquire()
        add = False
        for server in self.heartBeatQueue:
            if serverName == server.serverName:
                add = True
                server.timeStamp = int(time.time())
                break
        if add:
            heapq.heapify(self.heartBeatQueue)
        else:
            newServer = ServerHeartBeat(serverName, int(time.time()))
            heapq.heappush(self.heartBeatQueue, newServer)
        mutex.release()

    """add file"""
    def addFile(self, allPath, fileName, fileSize, blockSize):
        jason = {}

        fileID = self.getFileID(allPath, fileName)
        if self.namingTree.contains(fileID):
            jason["status"] = "error"
            jason["error_msg"] = "file already exists!"
        else:
            fileData = self.serverManager.addFile(fileID, fileSize, blockSize, 0)
            if fileData == 0:
                jason["status"] = "error"
                jason["error_msg"] = "block size mismatch!"
            elif fileData == 1:
                jason["status"] = "error"
                jason["error_msg"] = "out of disk space!"
            else:
                nowDir = self.treeRoot
                pathList = allPath.split('/')
                for path in pathList:
                    newDir =  nowDir + '/' + self.dirPrefix + path
                    if not self.namingTree.contains(newDir):
                        self.namingTree.create_node(self.dirPrefix + path ,newDir, parent = nowDir)
                    nowDir = newDir
                self.namingTree.create_node(self.filePrefix + fileName, fileID, parent = nowDir, data = {"data": fileData, "size" : fileSize})
                jason["status"] = "ok"
                jason["data"] = fileData

        return jason

    """get file"""
    def getFile(self, allPath, fileName):
        jason = {}

        fileID = self.getFileID(allPath, fileName)
        if self.namingTree.contains(fileID):
            jason["status"] = "ok"
            jason["data"] = self.namingTree.get_node(fileID).data["data"]
        else:
            jason["status"] = "error"
            jason["error_msg"] = "file does not exist!"

        return jason

    """exist file"""
    def containsFile(self, allPath, fileName):
        jason = {}
        print "a:",allPath,fileName
        fileID = self.getFileID(allPath, fileName)
        print "b:",fileID
        if self.namingTree.contains(fileID):
            jason["status"] = "ok"
            jason["result"] = True
        else:
            jason["status"] = "ok"
            jason["result"] = False
        
        return jason

    """sizeof file"""
    def sizeofFile(self, allPath, fileName):
        jason = {}

        fileID = self.getFileID(allPath, fileName)

        if self.namingTree.contains(fileID):
            jason["status"] = "ok"
            jason["result"] = self.namingTree.get_node(fileID).data["size"]
        else:
            jason["status"] = "error"
            jason["error_msg"] = "file does not exist!"
        return jason

    """append file"""
    def appendFile(self, allPath, fileName, fileSize, blockSize):
        jason = {}

        fileID = self.getFileID(allPath, fileName)
        if not self.namingTree.contains(fileID):
            jason["status"] = "error"
            jason["error_msg"] = "file does not exist!"
        else:
            fileData = self.namingTree.get_node(fileID).data
            appendData = self.serverManager.addFile(fileID, fileSize, blockSize, fileData["data"]["block_num"])

            if appendData == 0:
                jason["status"] = "error"
                jason["error_msg"] = "block size mismatch!"
            elif appendData == 1:
                jason["status"] = "error"
                jason["error_msg"] = "out of disk space!"
            else:
                fileData["size"] += fileSize
                fileData["data"]["block_num"] += appendData["block_num"]
                fileData["data"]["block_list"] += appendData["block_list"]
                jason["status"] = "ok"
                jason["data"] = {}
                jason["data"]["fid"] = appendData["fid"]
                jason["data"]["append_block_num"] = appendData["block_num"]
                jason["data"]["append_block_list"] = appendData["block_list"]

        return jason

    """delete file"""
    def deleteFile(self, allPath, fileName):
        jason = {}

        fileID = self.getFileID(allPath, fileName)
        
        if self.namingTree.contains(fileID):
            self.namingTree.remove_node(fileID)
            jason["status"] = "ok"
        else:
            jason["status"] = "error"
            jason["error_msg"] = "file does not exist!"

        return jason

    """create dir"""
    def createDir(self, allPath):
        jason = {}

        pathID = self.getPathID(allPath)
        if self.namingTree.contains(pathID):
            jason["status"] = "error"
            jason["error_msg"] = "dir already exists!"

        else:
            nowDir = self.treeRoot
            pathList = allPath.split('/')
            for path in pathList:
                newDir =  nowDir + '/' + self.dirPrefix  + path
                if not self.namingTree.contains(newDir):
                    self.namingTree.create_node(self.dirPrefix + path, newDir, parent = nowDir)
                nowDir = newDir
            jason["status"] = "ok"

        return jason

    """delete dir"""    
    def deleteDir(self, allPath):
        jason = {}

        pathID = self.getPathID(allPath)
        if not self.namingTree.contains(pathID):
            jason["status"] = "error"
            jason["error_msg"] = "dir does not exist!"
        elif self.namingTree.is_branch(pathID):
            jason["status"] = "error"
            jason["error_msg"] = "dir is not empty!"
        else:
            self.namingTree.remove_node(pathID)
            jason["status"] = "ok"

        return jason

    """list dir"""
    def listDir(self, allPath):
        jason = {}

        pathID = self.getPathID(allPath)
        if not self.namingTree.contains(pathID):
            jason["status"] = "error"
            jason["error_msg"] = "dir does not exist!"
        else:
            fileList = [node.tag for node in self.namingTree.children(pathID)]
            jason["status"] = "ok"
            jason["data"] = {"file_num":len(fileList), "file_list":fileList}

        return jason

    """add Server"""
    def addServer(self, serverName, validBlock):
        self.serverManager.addServer(serverName, validBlock)

    """remove Server"""
    def removeServer(self, serverName):
        jason = {}
        serverInfo = self.serverManager.getServerInfo(serverName)
        if serverInfo == None:
            jason["status"] = "error"
            jason["error_msg"] = "server does not exist!"
        else:
            transData = []
            for blockInfo in serverInfo:
                if self.namingTree.contains(blockInfo.fileID):
                    fileInfo = self.namingTree.get_node(blockInfo.fileID).data["data"]
                    if fileInfo["block_num"] > blockInfo.fileIndex:
                        fileBlock = fileInfo["block_list"][blockInfo.fileIndex]
                        if fileBlock["bid"] == blockInfo.blockID:
                            fileBlock["servers"].remove(serverName)
                            transData.append({"servers":[block for block in fileBlock["servers"]], "fid":fileInfo["fid"], "bid":fileBlock["bid"], "index":fileBlock["index"]})
            self.serverManager.removeServer(serverName)
            res = self.serverManager.transfer(transData)            
            if res == None:
                jason["status"] = "error"
                jason["error_msg"] = "server does not have enough space!"
                jason["error_log"] = transData
            else:
                for i in range(len(transData)):
                    fileData = self.namingTree.get_node(transData[i]["fid"]).data["data"]
                    fileData["block_list"][transData[i]["index"]]["servers"].append(res[i])
                    transData[i]["trans_server"] = res[i]
                jason["status"] = "ok"
                jason["data"] = transData
        return jason
naming_server = NamingServer()
#a = NamingServer()
if __name__ == "__main__":
    global a
    a.addServer("192.168.0.1:2000", 2)
    a.addServer("192.168.0.1:2001", 4)
    a.addServer("192.168.0.1:2002", 6)
    a.addServer("192.168.0.1:2003", 8)
    a.addServer("192.168.0.1:2004", 10)
    res = a.addFile("aaa/bbb/aaa", "aaa", 2*1024, 128*1024)
    print res
    res = a.addFile("aaa/bbb/aa", "aaa", 2*1024, 128*1024)
    print res
    a.getHeartBeat("192.168.0.1:2000")
    a.getHeartBeat("192.168.0.1:2001")

    check = HeartBeatChecker()
#    check.setDaemon(True)
    check.start()
#    res = a.appendFile("aaa/bbb/aaa", "aaa", 3*64*1024*1024, 64*1024*1024)
#    print res
#    res = a.getFile("aaa/bbb/aaa", "aaa")
#    print res
#    res = a.containsFile("aaa/bbb/ccc", "aaa")
#    print res
#    res = a.containsFile("aaa/bbb/aaa", "aaa")
#    print res
#    res = a.sizeofFile("aaa/bbb/aaa", "aaa")
#    print res
#    res = a.createDir("aaa/bbb/aaa")
#    print res
#    res = a.createDir("aaa/bbb/ccc")
#    print res
#    res = a.deleteDir("aaa/bbb/aaa")
#    print res
#    res = a.listDir("aaa")
#    print res
#    a.deleteFile("aaa/bbb/aaa", "aaa")
#    a.addFile("aaa/bbb/aaa", "aaa", 64*1024*1024, 64*1024*1024)
#    res = a.getFile("aaa/bbb/aaa", "aaa")
#    print res
#    res = a.removeServer("192.168.0.1:2003")
#    print res
    a.namingTree.show(idhidden = False)

