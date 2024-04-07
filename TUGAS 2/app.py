from flask import Flask, render_template
import requests
from flask import jsonify
from flask import request
from flask_mysqldb import MySQL
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'property'
mysql = MySQL(app)

app.config['JWT_SECRET_KEY'] = 'your_secret_key' 
jwt = JWTManager(app)


def validate_user(username, password):
    if username == 'yesroyoan' and password == 'dijaminA':
        return True
    return False


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Please provide username and password'}), 400

    if validate_user(username, password):
        # Jika usernya valid, maka JWT akan mengirim respons
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({'message': 'Incorrect username or password'}), 401

# Memprotect route autentikasi 
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

#Tampilan Halaman Utama untuk menambah keluhan
@app.route('/')
def index():
    return render_template('index.html')

# Menggunakan Method POST
@app.route('/helpdesk', methods=['POST'])
def add_helpdesk():
    try:
        id_pelanggan = request.form['id_pelanggan']
        tanggal = request.form['tanggal']
        topik = request.form['topik']
        deskripsi = request.form['deskripsi']
        status = request.form['status']

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO helpdesk (id_pelanggan, tanggal, topik, deskripsi, status) VALUES (%s, %s, %s, %s, %s)",
                       (id_pelanggan, tanggal, topik, deskripsi, status))
        mysql.connection.commit()
        cursor.close()

        return render_template('success.html')
    except Exception as e:
        return jsonify({'error': str(e), 'status_code': 500})

#Menampilkan Daftar Keluhan dengan Menggunakan Method GET
@app.route('/helpdesk_view', methods=['GET'])
def helpdesk_view():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM HELPDESK")

    # Fetch data yang telah diperbarui
    helpdesk_data = cursor.fetchall()

    cursor.close()

    return render_template('helpdesk.html', helpdesk_data=helpdesk_data)

#Menampilkan Daftar Keluhan dengan Menggunakan Method GET dan POST tanpa HTML (hanya JSON)
@app.route('/helpdesk', methods=['GET', 'POST'])
def helpdesk():
    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM HELPDESK")

        # Get column names from cursor.description
        column_names = [i[0] for i in cursor.description]

        # Fetch data yang telah diperbarui
        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(column_names, row)))


        cursor.close()
    
        return jsonify(data)
    
    elif request.method == 'POST':
            request_data = request.json
            id_pelanggan = request_data.get('id_pelanggan')
            tanggal = request_data.get('tanggal')
            topik = request_data.get('topik')
            deskripsi = request_data.get('deskripsi')
            status = request_data.get('status')

            # Memasukkan data baru ke dalam tabel helpdesk
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO helpdesk (id_pelanggan, tanggal, topik, deskripsi, status) VALUES (%s, %s, %s, %s, %s)",
                        (id_pelanggan, tanggal, topik, deskripsi, status))
            mysql.connection.commit()
            cursor.close()

            return render_template('confirmation.html', message='Data helpdesk berhasil ditambahkan', status_code=201)

#Tampilan untuk melakukan pencarian berdasarkan ID Number
@app.route('/helpdesk/<int:id_pelanggan>', methods=['GET'])
def get_helpdesk_by_id(id_pelanggan):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM HELPDESK WHERE id_pelanggan = %s", (id_pelanggan,))

    # Get column names from cursor.description
    column_names = [i[0] for i in cursor.description]

    # Fetch data yang telah diperbarui
    data = []
    for row in cursor.fetchall():
        data.append(dict(zip(column_names, row)))

    cursor.close()

    if len(data) == 0:
        return jsonify({'message': 'ID pelanggan tidak ditemukan'}), 404
    else:
        return render_template('helpdesk_by_id.html', helpdesk_data=data)


#Tampilan untuk melakukan pencarian berdasarkan Nama Customer
@app.route('/helpdesk/<string:nama>', methods=['GET'])
def get_helpdesk_by_customer_name(nama):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT H.* FROM HELPDESK H JOIN PELANGGAN P ON H.id_pelanggan = P.id_pelanggan WHERE P.nama = %s", (nama,))

    # Get column names from cursor.description
    column_names = [i[0] for i in cursor.description]

    # Fetch data yang telah diperbarui
    data = []
    for row in cursor.fetchall():
        data.append(dict(zip(column_names, row)))

    cursor.close()

    if len(data) == 0:
        return jsonify({'message': 'Tidak ada pertanyaan dari pelanggan dengan nama tersebut'}), 404
    else:
        return render_template('helpdesk_by_name.html', helpdesk_data=data)

#Untuk melakukan Edit Data 
@app.route('/edithelpdesk/<int:id_pelanggan>', methods=['PUT'])
def edit_helpdesk(id_pelanggan):
    request_data = request.json
    tanggal = request_data.get('tanggal')
    topik = request_data.get('topik')
    deskripsi = request_data.get('deskripsi')
    status = request_data.get('status')

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE HELPDESK SET tanggal = %s, topik = %s, deskripsi = %s, status = %s WHERE id_pelanggan = %s",
                   (tanggal, topik, deskripsi, status, id_pelanggan))
    mysql.connection.commit()
    cursor.close()
    
    # Menambahkan informasi timestamp
    timestamp = datetime.utcnow()
    
    response = {
        "timestamp": timestamp,
        "code": 200,
        "message": "Data helpdesk berhasil diubah"
    }
    
    return jsonify(response)

#Untuk Menghapus Data
@app.route('/deletehelpdesk/<int:id_pelanggan>', methods=['DELETE'])
def delete_helpdesk(id_pelanggan):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM HELPDESK WHERE id_pelanggan = %s", (id_pelanggan,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': 'Data berhasil dihapus'})

   # Menambahkan informasi timestamp
    timestamp = datetime.utcnow()
    
    response = {
        "timestamp": timestamp,
        "code": 200,
        "message": "Data berhasil dihapus"
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50, debug=True)
