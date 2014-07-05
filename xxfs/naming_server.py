#coding=utf-8
from flask import Flask,request
from flask.ext.restful import reqparse, abort, Api, Resource
import config
import os
import naming_manager

app = Flask(__name__)
api = Api(app)
naming = naming_manager.NamingServer

post_parser = reqparse.RequestParser()
post_parser.add_argument('type',type=str,required=True)
post_parser.add_argument('file_size',type=int)
post_parser.add_argument('block_size',type=int)
post_parser.add_argument('host',type=str)
post_parser.add_argument('port',type=int)
post_parser.add_argument('storage_space',type=int)


get_parser = reqparse.RequestParser()
get_parser.add_argument('type',type=str,required=True)
get_parser.add_argument('info',type=str)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('type',type=str,required=True)

def __error__(err_msg):
    return {'status':"error", "message":err_msg}

class Naming(Resource):
    
    def get(self, target_path):
        args = get_parser.parse_args()
        print args
        if args['type'] == 'file' :
            #TODO check target_path
            file_name = os.path.basename(target_path)
            file_path = os.path.dirname(target_path)
            app.logger.debug("file_name:"+file_name)
            app.logger.debug("file_path:"+file_path)
            
            if args['info'] == 'data':
                return naming.getFile(file_path, file_name)
                # return {
                #     'status':"ok",
                #     'data':{ 
                #         'fid':"fid-test", 
                #         'block_num':2,
                #         'block_list':[
                #             {
                #                 'servers':["127.0.0.1:20001"],
                #                 'bid':"bid-test-0",
                #                 'index':0
                #             },
                #             {
                #                 'servers':["127.0.0.1:20001"],
                #                 'bid':"bid-test-1", 
                #                 'index':1
                #             },
                #         ]
                #     }
                # }
                
            elif args['info'] == 'exist':
                return naming.containFile(file_path,file_name)
                # return {'status':"ok","result":True}
                
            elif args['info'] == 'size':
                return naming.sizeofFile(file_path, file_name)
                # return {'status':"ok","result":111}
                
            else:
                return __error__("invalid info")

        elif args['type'] == 'directory':
            return naming.listDir(target_path)
        else:
            return __error__("invalid type")

    def post(self, target_path):
        args = post_parser.parse_args()
        if args['type'] == 'file':
            file_name = os.path.basename(target_path)
            file_path = os.path.dirname(target_path)
            app.logger.debug("file_name:"+file_name)
            app.logger.debug("file_path:"+file_path)

            file_size = args['file_size']
            block_size = args['block_size']
            if block_size != config.BlockSize :
                return __error__("block_size mismatch")
            app.logger.debug("file_size:"+str(file_size))

            return naming.addFile(file_path, file_name, file_size, block_size)
            # return {
            #     'status':"ok",
            #     'data':{ 
            #         'fid':"fid-test", 
            #         'block_num':2,
            #         'block_list':[
            #             {
            #                 'servers':["127.0.0.1:20001"],
            #                 'bid':"bid-test-0",
            #                 'index':0
            #             },
            #             {
            #                 'servers':["127.0.0.1:20001"],
            #                 'bid':"bid-test-1", 
            #                 'index':1
            #             },
            #         ]
            #     }
            # }
        elif args['type'] == 'directory':
            app.logger.debug("path:"+target_path)
            # return {'status':"ok"}
            return createDir(target_path)
        elif args['type'] == 'storage_server':
            host = args['host']
            port = args['port']
            space = args['storage_space']
            block_num = space/config.BlockSize
            naming.addServer(host+str(port), block_num)
            return {"status":"ok"}
        else:
            return __error__("invalid type")

    def delete(self, target_path):
        args = delete_parser.parse_args()
        # print args
        if args['type'] == 'file':
            file_name = os.path.basename(target_path)
            file_path = os.path.dirname(target_path)
            
            return naming.deleteFile(file_path, file_name)
            # return {'status':"ok"}
        elif args['type'] == 'directory':
            return naming.deleteDir(target_path)
            # return {'status':"ok"}
        else:
            return __error__("invalid type")

    def put(self, target_path):
        args = post_parser.parse_args()
        if args['type'] != 'file' or not args['file_size'] or not args['block_size'] or int(args['block_size']) != config.BlockSize:
            return  {'status':"error", "message":"invalid input"}
        file_size = args['file_size']
        file_name = os.path.basename(target_path)
        file_path = os.path.dirname(target_path)
        return appendFile(file_path, file_name, file_size)
        # return {'status':"ok"}



api.add_resource(Naming, '/<path:target_path>')


if __name__ == '__main__':
    app.run(port=config.NamingServerPort,debug=True)