import requests
import os
import config

def __check_local_file__(local_file):
    if not os.path.exists(local_file):
        print "local file does not exist"
        exit(1)
    if not os.path.isfile(local_file):
        print local_file," is not a file";
        exit(1)

def __upload_file_to_storage_servers__(local_file,fid,block_info_list):
    fin = open(local_file,"rb");
    for block_info in block_info_list:
        storage_servers = block_info["storage_server_list"]
        bid = block_info["bid"]
        block_data = fin.read(config.BlockSize)
        for storage_server in storage_servers:
            url = "http://" + storage_server + "/" + fid + "/" + bid
            r = requests.post(url,data={"file":block_data})
            ret = r.json()
            if ret["status"] == "error":
                print ret["error_msg"]
                exit(1)
    fin.close();

def add(argv):
    if len(argv) < 2:
        print "not enough arguments"
        exit(1)
    local_file = argv[0]
    remote_path = argv[1]
    
    __check_local_file__(local_file)

    file_name = os.path.basename(local_file)
    file_size = os.path.getsize(local_file)
    param = {
        "file_size":file_size,
        "type":"file",
        "block_size":config.BlockSize
    }
    url = "http://"+config.NamingServer+"/"+remote_path+"/"+file_name
    r = requests.post(url,params=param);
    # print r.url
    ret = r.json()
    
    if ret["status"] == "error":
        print ret["error_msg"]
        exit(1)
    data = ret["data"]
    fid = data["fid"]
    block_num = data["block_num"]
    block_list = data["block_list"]
    block_info_list = range(block_num)
    for block in block_list:
        index = int(block["index"]);
        block_info_list[index] = {
            "storage_server_list":block_info["block_servers"],
            "bid":block_info["bid"]
        }

    __upload_file_to_storage_servers__(local_file,fid,block_info_list)
    
    print "add file success!"

def append(argv):
    if len(argv) < 2:
        print "not enough arguments"
        exit(1)
    remote_file = argv[0]
    append_file = argv[1]

    __check_local_file__(append_file)
    file_size = os.path.getsize(append_file)
    param = {
        "file_size":file_size,
        "block_size":config.BlockSize
    }
    url = "http://"+config.NamingServer+"/"+remote_file
    r = requests.post(url,params=param);
    # print r.url
    ret = r.json()
    
    if ret["status"] == "error":
        print ret["error_msg"]
        exit(1)

    data = ret["data"]
    fid = data["fid"]
    block_num = data["append_block_num"]
    block_list = data["append_block_list"]
    block_info_list = range(block_num)
    for block in block_list:
        index = int(block["index"]);
        block_info_list[index] = {
            "storage_server_list":block_info["block_servers"],
            "bid":block_info["bid"]
        }

    __upload_file_to_storage_servers__(append_file,fid,block_info_list)

    print "append file success!"

def delete(argv):
    if len(argv) < 1:
        print "not enough arguments"
        exit(1)
    remote_file = argv[0]
    param = {
        'type':"file"
    }
    url = "http://" + config.NamingServer + "/" + remote_file
    r = requests.delete(url,params=param);
    ret = r.json()
    if ret["status"] == "error":
        print ret["error_msg"]
        exit(1)

def get(argv):
    if len(argv) < 2:
        print "not enough arguments"
        exit(1)
    remote_file = argv[0]
    local_path = argv[1]

    #get meta info from naming server
    url = "http://"+config.NamingServer+"/"+remote_file
    param = {
        "info":"data",
        "type":"file"
    }
    r = requests.get(url,params=param);
    ret = r.json()
    if ret["status"] == "error":
        print ret["error_msg"]
        exit(1)
    data = ret["data"]
    fid = data["fid"]
    block_num = data["block_num"]
    block_list = data["block_list"]
    block_info_list = range(block_num)
    for block in block_list:
        index = int(block["index"]);
        block_info_list[index] = {
            "storage_server_list":block_info["block_servers"],
            "bid":block_info["bid"]
        }

    #get data from storage server
    file_name = os.path.basename(remote_file)
    fout = open(local_path+"/"+file_name, "wb");
    for block_info in block_info_list:
        storage_servers = block_info["storage_server_list"]
        bid = block_info["bid"]
        block_data = None
        block_size = 0
        for storage_server in storage_servers:
            url = "http://" + storage_server + "/" + fid + "/" + bid
            r = requests.post(url,data=block_data)
            ret = r.json()
            if ret["status"] == "error":
                print ret["error_msg"]
                exit(1)
            else:
                block_size = int(ret["data"]["size"])
                block_data = ret["data"]["content"]
                break;

        if block_size != len(block_data):
            print "size mismatch"
        fout.write(block_data)
    fout.close();

def exist(argv):
    if len(argv) < 1:
        print "not enough arguments"
        exit(1)
    remote_file = argv[0]
    url = "http://"+config.NamingServer+"/"+remote_file
    param = {
        "info":"exist",
        "type":"file"
    }
    r = requests.get(url,params=param);
    ret = r.json()
    if ret["status"] == "error":
        print ret["error_msg"]
        exit(1)
    if ret["result"] == True:
        print "YES, it exists"
    else:
        print "NO, it doesn't exist"


def sizeof(argv):
    if len(argv) < 1:
        print "not enough arguments"
        exit(1)
    remote_file = argv[0]
    url = "http://"+config.NamingServer+"/"+remote_file
    param = {
        "info":"sizeof",
        "type":"file"
    }
    r = requests.get(url,params=param);
    ret = r.json()
    if ret["status"] == "error":
        print ret["error_msg"]
        exit(1)
    print "size=",ret["result"]+"Byte"

def mkdir(argv):
    if len(argv) < 1:
        print "not enough arguments"
        exit(1)
    remote_path = argv[0]
    url = "http://"+config.NamingServer+"/"+remote_path
    param = {
        "type":"directory"
    }
    r = requests.post(url,params=param);
    ret = r.json()
    if ret["status"] == "error":
        print ret["error_msg"]
        exit(1)
    print "mkdir success"


def rmdir(argv):
    if len(argv) < 1:
        print "not enough arguments"
        exit(1)
    remote_path = argv[0]
    url = "http://"+config.NamingServer+"/"+remote_path
    param = {
        "type":"directory"
    }
    r = requests.delete(url,params=param);
    ret = r.json()
    if ret["status"] == "error":
        print ret["error_msg"]
        exit(1)
    print "rmdir success"



def ls(argv):
    if len(argv) < 1:
        print "not enough arguments"
        exit(1)
    remote_path = argv[0]

    url = "http://"+config.NamingServer+"/"+remote_path
    param = {
        "type":"directory",
        "info":"file_list"

    }
    r = requests.get(url,params=param);
    ret = r.json()
    if ret["status"] == "error":
        print ret["error_msg"]
        exit(1)

    data = ret["data"]
    print "File Number:",data['file_num']
    for f in data["file_list"]:
        print "\t",f
    print "ls success"


