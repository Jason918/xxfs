from flask import Flask,request
from flask.ext.restful import reqparse, abort, Api, Resource


app = Flask(__name__)
api = Api(app)

# add_parser = reqparse.RequestParser()
# add_parser.add_argument('file_size',type=int)
# add_parser.add_argument('type',type=str)
# add_parser.add_argument('block_size',type=int)

class Storage(Resource):
    def get(self, fid, bid):
        target_file = storage_path + '/' + fid + "/" + bid;
        if not os.path.isfile(target_file):
            return {'status': "error",'error_msg':"block does not exist"}  
        fin = open(target , 'rb')
        data = {
            'content':fin.read(),
            'size':len(data)
        }
        fin.close()
        return {'status':"ok", data}

    def post(self, fid, bid):
        fout = open(storage_path + '/' + fid + "/" + bid, 'wb')
        fout.write(request.form["data"])
        fout.close()
        return {'status': "ok"}

# api.add_resource(Storage, '/<path:file_path>')
api.add_resource(Storage, '/<string:fid>/<string:bid>')

if __name__ == '__main__':
    app.run(debug=True)