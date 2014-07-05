#coding=utf-8
from flask import Flask,request
from flask.ext.restful import reqparse, abort, Api, Resource
import os
import sys
import base64
import config
import requests
import threading
import time
import requests

app = Flask(__name__)
api = Api(app)

storage_path = "./"
host = "127.0.0.1"
port = 10000

class Storage(Resource):
    def get(self, fid, bid):
        target_file = storage_path + '/' + bid
        print "request block:",target_file
        if not os.path.isfile(target_file):
            return {'status': "error",'message':"block does not exist"}  
        fin = open(target_file , 'rb')
        in_data = fin.read()
        size = len(in_data)
        print "block size:",size
        in_data = base64.b64encode(in_data)
        data = {
            'content':in_data,
            'size':size
        }
        fin.close()
        return {'status':"ok", 'data':data}

    def post(self, fid, bid):
        print "fid:",base64.b64decode(fid)
        print "bid:",bid
        upload_file = request.files['file']

        file_path = storage_path + '/' + bid
        upload_file.save(file_path)
        # print len(request.form["file"].decode("utf-8"))
        # fout = open(storage_path + '/' + fid + "-" + bid, 'w')
        # data = request.form["file"]
        # fout.write(data)
        # fout.close()
        return {'status': "ok"}
    def put(self, fid, bid):
        print "trans fid:",base64.b64decode(fid)
        print "trans bid:",bid
        target_server = request.args['trans_server']
        target_file = storage_path + '/' + bid
        print "---"
        with open(target_file,"rb") as fin:
            block_data = fin.read()
            print len(block_data)
            url = "http://" + target_server + "/" + fid + "/" + bid
            r = requests.post(url,files={"file":(bid,block_data)})
            if r.status_code != 200:
                print "trans error"
                

# api.add_resource(Storage, '/<path:file_path>')
api.add_resource(Storage, '/<string:fid>/<string:bid>')

def register(host, port, space):
    url = "http://"+config.NamingServer+"/storage_server"
    param = {
        'type':'storage_server',
        'host':host,
        'port':port,
        'storage_space': space
    }
    r = requests.post(url, params = param)
    if r.status_code != 200:
        print "register error"
        exit(0)
    else:
        print "register success"

class HeartBeatSender(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        url = "http://"+config.NamingServer+"/storage_server"
        param = {
            'type':'storage_server',
            'server_name':host+":"+str(port)
        }
        while True:
            # print "sending HB"
            requests.put(url,params = param)
            time.sleep(1)


if __name__ == '__main__':
    argv = sys.argv
    if len(argv) < 5:
        print "not enough arguments"
        print """USAGE:
        storage_server.py host port storage_path storage_space(MB)
        """
        exit(1)
    host = argv[1]
    port = int(argv[2])
    storage_path = argv[3]
    storage_space = int(argv[4]) * 1000000

    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
        print "storage path ", storage_path, " does not exists, creating..."
    register(host, port, storage_space)


    hb = HeartBeatSender()
    hb.setDaemon(True)
    hb.start()
    print "init done"

    app.run(port=port,debug=True,use_debugger=False,use_reloader=False)