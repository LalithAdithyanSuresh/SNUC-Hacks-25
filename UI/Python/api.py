from flask import Flask, request, jsonify, send_file, session
from flask_session import Session
from flask_cors import CORS
import qrcode
import random
import subprocess
from io import BytesIO
import connect

# Start the secondary server
subprocess.Popen(["python3.11", "/home/ubuntu/snuc/UI/Website/webserver.py"])

app = Flask(__name__)

# ✅ Enable CORS for all routes
CORS(app, supports_credentials=True)  # Allow credentials (session cookies)

# ✅ Session configuration
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"  
app.config["SESSION_PERMANENT"] = False  
Session(app)

# ✅ Database connection
connection, cursor = connect.getConnection()


def partyGen():
    return "".join([chr(ord('A') + random.randint(0, 25)) for _ in range(6)])


def idGen():
    return "".join([chr(ord('A') + random.randint(0, 25)) for _ in range(10)])


@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    try:
        data = request.json
        url = data.get('url', 'https://default.com')  # Avoid KeyError

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=1,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill="black", back_color="white")

        # ✅ Convert image to bytes
        img_io = BytesIO()
        img.save(img_io, format="PNG")
        img_io.seek(0)

        response = send_file(img_io, mimetype='image/png')
        
        # ✅ Ensure CORS headers are included
        # response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
        # response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/test', methods=['POST'])
def test():
    return 'Hello, World!'


@app.route('/api/getData', methods=['GET'])
def getData():
    cursor.execute("SELECT * FROM user")
    result = cursor.fetchall()
    return jsonify(result)


@app.route('/api/addUser', methods=['POST'])
def addUser():
    data = request.json
    ID = data.get('id', idGen())  # Use default if no ID provided
    p = data.get('party', partyGen())

    if 'party' not in data:
        cursor.execute("INSERT INTO party VALUES (%s, %s,%s,%s)", (p, ID,"{}","{}"))

    cursor.execute("INSERT INTO user VALUES (%s, %s, %s)", (ID, data['name'], p))
    connection.commit()

    # ✅ Store session data
    session["id"] = ID
    session["username"] = data['name']
    session["party"] = p

    response = jsonify({'status': 'success', 'message': 'User added successfully!', 'party': p})
    
    # ✅ Ensure CORS headers are included
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

@app.route('/api/addItems',methods=['POST'])
def addItems():
    

if __name__ == '__main__':
    app.run(debug=True, port=9876, host='0.0.0.0')
