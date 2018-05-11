#!flask/bin/python
import logging
from flask import Flask, jsonify, abort, make_response, request, url_for, send_from_directory



# enable logging
level = 'INFO'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.getLevelName(level))
logger = logging.getLogger(__name__)

# define app name
app = Flask(__name__)
img = './images/'
app.config['img'] = img

#
@app.route('/api/token')
def get_auth_token():
    token = "1234567890"
    return jsonify({'token': '1qaz2wsx'})

# return all objects
@app.route('/api/v1.0/data', methods=['GET'])
def get_objects():
    return jsonify({'objects':'1'})

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

# return custom error
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.config['img'], 'favicon.png', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=80, debug=False)
