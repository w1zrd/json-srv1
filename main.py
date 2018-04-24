#!flask/bin/python
import logging
from flask import Flask, jsonify, abort, make_response, request, url_for, send_from_directory
from flask_httpauth import HTTPBasicAuth

# TODO: convert picture name to URI
# TODO: add load picture method

# enable logging
level = 'INFO'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.getLevelName(level))
logger = logging.getLogger(__name__)

# define app name
app = Flask(__name__)
UPLOAD_FOLDER = './images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# define auth method
auth = HTTPBasicAuth()

# sample object list
objects = [
    {
        'id': 0,
        'title': u'White house',
        'description': u'The general USA house',
        'pictures' : ["0001.jpg", "0002.jpg"],
        'sold': False
    },
    {
        'id': 1,
        'title': u'Black house',
        'description': u'The Roskomnadzor office',
        'pictures' : [],
        'sold': False
    }
]

#
def make_public_objects(object):
    new_object = object
#    new_object = {}
#    for field in object:
#        if field == 'id':
#            new_object['uri'] = url_for('get_object', object_id=object['id'], _external=True)
#        else:
#            new_object[field] = object[field]
    new_object['uri'] = url_for('get_object', object_id=object['id'], _external=True)
    return new_object


@auth.get_password
def get_password(username):
    if username == 'user':
        return 'estate'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)

#
@app.route('/estate/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

# return all objects
@app.route('/estate/api/v1.0/objects', methods=['GET'])
@auth.login_required
def get_objects():
    return jsonify({'objects': list(map(make_public_objects, objects))})

# return 1 object
@app.route('/estate/api/v1.0/object/<int:object_id>', methods=['GET'])
@auth.login_required
def get_object(object_id):
    object = list(filter(lambda t: t['id'] == object_id, objects))
    if len(object) == 0:
        abort(404)
    return jsonify({'object': make_public_objects(object[0])})

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify( { 'error': 'Bad request' } ), 400)

# return custom error
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# return
@app.route('/estate/api/v1.0/object', methods=['POST'])
@auth.login_required
def create_object():
    if not request.json or not 'title' in request.json:
        abort(400)
    object = {
        'id': objects[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'sold': False
    }
    objects.append(object)
    return jsonify({'object': make_public_objects(object)}), 201

#
@app.route('/estate/api/v1.0/object/<int:object_id>', methods=['PUT'])
@auth.login_required
def update_object(object_id):
    object = list(filter(lambda t: t['id'] == object_id, objects))
    if len(object) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'sold' in request.json and type(request.json['sold']) is not bool:
        abort(400)
    object[0]['title'] = request.json.get('title', object[0]['title'])
    object[0]['description'] = request.json.get('description', object[0]['description'])
    object[0]['sold'] = request.json.get('sold', object[0]['sold'])
    return jsonify({'object': make_public_objects(object[0])})

@app.route('/estate/api/v1.0/object/<int:object_id>', methods=['DELETE'])
@auth.login_required
def delete_object(object_id):
    object = list(filter(lambda t: t['id'] == object_id, objects))
    if len(object) == 0:
        abort(404)
    objects.remove(object[0])
    return jsonify({'result': True})

# loading images form root folders
@app.route('/estate/api/v1.0/picture/<string:prefix>/<string:name>', methods=['GET'])
def send_pics(prefix, name):
    pics = open(UPLOAD_FOLDER + prefix + '/' + name)
    if pics:
        return send_from_directory(app.config['UPLOAD_FOLDER'], prefix + '/' + name)
    abort(404)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.config['UPLOAD_FOLDER'], 'favicon.png', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=80, debug=True)
    app.run(debug=True)
