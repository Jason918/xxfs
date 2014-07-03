import treelib
import sever_manager

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
        
class NamingSever:
    dirPrefix = "dir_"
    filePrefix = "file_"
    treeRoot = "dir_root"

    """init"""
    def __init__(self):
        self.namingTree = treelib.Tree()
        self.namingTree.create_node(self.treeRoot, self.treeRoot)
        self.severManager = sever_manager.SeverManager()
    
    def getFileID(self, allPath, fileName):
        fileID = self.treeRoot + '/' + '/'.join([self.dirPrefix + path for path in allPath.split('/')]) + '/' + self.filePrefix + fileName
        return fileID

    def getPathID(self, allPath):
        pathID = self.treeRoot + '/' + '/'.join([self.dirPrefix + path for path in allPath.split('/')])
        return pathID

    """add file"""
    def addFile(self, allPath, fileName, fileSize, blockSize):
        jason = {}

        fileID = self.getFileID(allPath, fileName)
        if self.namingTree.contains(fileID):
            jason["status"] = "error"
            jason["error_msg"] = "file already exists!"
        else:
            fileData = self.severManager.addFile(fileID, fileSize, blockSize, 0)
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

        fileID = self.getFileID(allPath, fileName)

        if self.namingTree.contains(fileID):
            jason["status"] = "ok"
            jason["result"] = "true"
        else:
            jason["status"] = "ok"
            jason["result"] = "false"
        
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
            appendData = self.severManager.addFile(fileID, fileSize, blockSize, fileData["data"]["block_num"])

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

    def addSever(self, severName, validBlock):
        self.severManager.addSever(severName, validBlock)

if __name__ == "__main__":
    a = NamingSever()
    a.addSever("192.168.0.1:2000", 20)
    a.addSever("192.168.0.1:2001", 20)
    a.addSever("192.168.0.1:2002", 20)
    res = a.addFile("aaa/bbb/aaa", "aaa", 2*64*1024*1024, 64*1024*1024)
    res = a.appendFile("aaa/bbb/aaa", "aaa", 3*64*1024*1024, 64*1024*1024)
    print res
    res = a.getFile("aaa/bbb/aaa", "aaa")
    print res
    res = a.containsFile("aaa/bbb/ccc", "aaa")
    print res
    res = a.containsFile("aaa/bbb/aaa", "aaa")
    print res
    res = a.sizeofFile("aaa/bbb/aaa", "aaa")
    print res
    res = a.createDir("aaa/bbb/aaa")
    print res
    res = a.createDir("aaa/bbb/ccc")
    print res
    res = a.deleteDir("aaa/bbb/aaa")
    print res
    res = a.listDir("aaa")
    print res
    a.namingTree.show(idhidden = False)

