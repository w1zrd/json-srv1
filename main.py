#!flask/bin/python
from flask import Flask, jsonify, abort, make_response, request, url_for
from flask_httpauth import HTTPBasicAuth
import postgresql

# TODO: make a houserecord`s structure
# TODO: add json header with records count, previous and next URI
# TODO: move records to the results section

# define app name
app = Flask(__name__)

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
    new_object = {}
    for field in object:
        if field == 'id':
            new_object['uri'] = url_for('get_object', object_id=object['id'], _external=True)
        else:
            new_object[field] = object[field]
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
@app.route('/estate/api/v1.0/objects/<int:object_id>', methods=['GET'])
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
@app.route('/estate/api/v1.0/objects', methods=['POST'])
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
@app.route('/estate/api/v1.0/objects/<int:object_id>', methods=['PUT'])
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

@app.route('/estate/api/v1.0/objects/<int:object_id>', methods=['DELETE'])
@auth.login_required
def delete_object(object_id):
    object = list(filter(lambda t: t['id'] == object_id, objects))
    if len(object) == 0:
        abort(404)
    objects.remove(object[0])
    return jsonify({'result': True})

##
    # connect to database
    db = postgresql.open('pq://user:postgres@localhost:5432/jsonsrv')
    logger.debug('init a database connection string')

    init_us = db.execute("CREATE TABLE IF NOT EXISTS profiles ("
                               "user_id INTEGER PRIMARY KEY, "
                               "username VARCHAR(64))")

    init_db = db.execute("CREATE TABLE IF NOT EXISTS objects ("
                         "id SERIAL PRIMARY KEY, "
                         "o_date TIMESTAMP, "
                         "o_name VARCHAR(64), "
                         "o_currency VARCHAR(64), "
                         "o_sum INTEGER NOT NULL, "
                         "user_id INTEGER REFERENCES profiles(user_id), "
                         "o_state INTEGER NOT NULL DEFAULT '1')")

    # using db.query for get data from table
    orders = db.query("SELECT * FROM objects ORDER BY id DESC LIMIT 1");

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=80, debug=True)
    app.run(host='0.0.0.0', port=80, debug=False)
