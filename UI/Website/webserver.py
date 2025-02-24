from flask import Flask, request, jsonify,send_file
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/<path:path>')
def send_js(path):
    return send_file(path)

@app.route('/')
def start():
    return send_file('index.html')

if __name__ == '__main__':
    app.run(ssl_context=('/etc/letsencrypt/live/vijayanthaalumni.net/fullchain.pem',
                         '/etc/letsencrypt/live/vijayanthaalumni.net/privkey.pem'),
            host='0.0.0.0', port=443,debug=True)