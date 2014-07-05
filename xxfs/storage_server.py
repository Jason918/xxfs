#coding=utf-8
from flask import Flask,request
from flask.ext.restful import reqparse, abort, Api, Resource
import os
import sys
import base64
import config
import requests

app = Flask(__name__)
api = Api(app)

storage_path = "./"

class Storage(Resource):
    def get(self, fid, bid):
        target_file = storage_path + '/' + fid + "-" + bid
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
        upload_file = request.files['file']

        file_path = storage_path + '/' + fid + "-" + bid
        upload_file.save(file_path)
        # print len(request.form["file"].decode("utf-8"))
        # fout = open(storage_path + '/' + fid + "-" + bid, 'w')
        # data = request.form["file"]
        # fout.write(data)
        # fout.close()
        return {'status': "ok"}

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
    if r.status != 200:
        print "register error"
        exit(1)
    else:
        print "register success"


if __name__ == '__main__':
    argv = sys.argv()
    if len(argv) < 3:
        print "not enough arguments"
        print """USAGE:
        storage_server.py host port storage_path storage_space
        """
    host = argv[1]
    port = int(argv[2])
    storage_path = argv[3]
    storage_space = int(argv[4])
    register(host, port, storage_space)

    app.run(port=port,debug=True)