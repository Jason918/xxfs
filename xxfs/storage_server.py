#coding=utf-8
from flask import Flask,request
from flask.ext.restful import reqparse, abort, Api, Resource
import os

app = Flask(__name__)
api = Api(app)

storage_path = "./"

class Storage(Resource):
    def get(self, fid, bid):
        target_file = storage_path + '/' + fid + "-" + bid
        print target_file
        # if not os.path.isfile(target_file):
        #     return {'status': "error",'message':"block does not exist"}  
        # fin = open(target_file , 'rb')
        # send_file(fin)
        # in_data = fin.read()
        # data = {
        #     'content':in_data,
        #     'size':len(in_data)
        # }

        fin.close()
        # return {'status':"ok", 'data':data}

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

if __name__ == '__main__':
    app.run(port=20001,debug=True)