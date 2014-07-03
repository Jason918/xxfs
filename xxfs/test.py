from flask import Flask,request
from flask.ext.restful import reqparse, abort, Api, Resource


app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('a',type=str)

class HelloWorld(Resource):
    def get(self, file_path):
        args = parser.parse_args()
        return {'hello': args ,'path':file_path}
    def post(self, file_path):
        args = parser.parse_args()
        f = request.files['file']
        print len(f)
        return {'hello': args,'path':file_path}

api.add_resource(HelloWorld, '/<path:file_path>')

if __name__ == '__main__':
    app.run(debug=True)