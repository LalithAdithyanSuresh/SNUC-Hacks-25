from flask import Flask, request, jsonify,send_file
import random
import connect
import qrcode
from io import BytesIO
from flask_cors import CORS

def partyGen():
    return "".join([chr(ord('A') + random.randint(0,25)) for i in range(6)])

app = Flask(__name__)
CORS(app)


connection, cursor = connect.getConnection()


@app.route('/generate_qr',methods=['GET'])
def generate_qr():
    url = request.json['url']
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


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
    if 'party' not in data:
        p = partyGen()
        data['party'] = p
        cursor.execute("INSERT INTO party VALUES (%s, %s)", (p, data['id']))
    cursor.execute("INSERT INTO user VALUES (%s, %s,%s)", (data['id'], data['name'],data['party']))
    connection.commit()
    return jsonify({'status': 'success', 'message': 'User added successfully!', 'party': data['party']})

if __name__ == '__main__':
    app.run(debug=True,port=9876,host='0.0.0.0')