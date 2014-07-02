from flask import Flask,request
from flask.ext.restful import reqparse, abort, Api, Resource


app = Flask(__name__)
api = Api(app)

post_parser = reqparse.RequestParser()
post_parser.add_argument('type',type=str,required=True)
post_parser.add_argument('file_size',type=int)
post_parser.add_argument('block_size',type=int)

get_parser = reqparse.RequestParser()
get_parser.add_argument('type',type=str,required=True)
get_parser.add_argument('info',type=str)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('type',type=str,required=True)

class Naming(Resource):
    def get(self, target_path):
        args = get_parser.parse_args()
        if args['type'] == 'file' :
            #TODO check target_path
            file_name = os.path.basename()
            file_path = os.path.dirname();
            if args['info'] == 'data':
                pass #TODO
            elif args['info'] == 'exist':
                pass #TODO
            elif args['info'] == 'size':
                pass #TODO
            else:
                return {'status':"error", "error_msg":"invalid info"}    

        else if args['type'] == 'directory':
            pass
        else:
            return {'status':"error", "error_msg":"invalid type"}

    def post(self, target_path):
        args = post_parser.parse_args()
        if args['type'] == 'file':
            file_size = args['file_size']
            block_size = args['block_size']
            #TODO
        elif args['type'] == 'directory':
            #TODO 
        else:
            return {'status':"error", "error_msg":"invalid type"}

    def delete(self, target_path):
        args = delete_parser.parse_args()
        if args['type'] == 'file':
            file_size = args['file_size']
            block_size = args['block_size']
            #TODO
        elif args['type'] == 'directory':
            #TODO 
        else:
            return {'status':"error", "error_msg":"invalid type"}

    def put(self, target_path):
        args = post_parser.parse_args()
        pass

api.add_resource(Naming, '/<path:target_path>')


if __name__ == '__main__':
    app.run(debug=True)