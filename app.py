from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

# --- KONFIGURASI MONGODB ATLAS (ONLINE) ---

# Password: 041002Dekgus (Tanda < > sudah dihapus)
# Database Name: kuliah_db (Kita tentukan nama databasenya di sini)
CONNECTION_STRING = "mongodb+srv://dwiadnyana:041002Dekgus@cluster0.rv3yldr.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(CONNECTION_STRING)
    # Cek koneksi (ping)
    client.admin.command('ping')
    print("✅ Berhasil terhubung ke MongoDB Atlas!")
except Exception as e:
    print(f"❌ Gagal terhubung ke MongoDB: {e}")

# Pilih Database (Otomatis dibuat jika belum ada di Atlas)
db = client['kuliah_db']       
tasks_collection = db['tasks'] 

@app.route('/')
def index():
    return render_template('index.html')

# --- API ENDPOINTS (Sama seperti sebelumnya) ---

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = []
    try:
        # Sort berdasarkan tanggal pembuatan (terbaru di atas)
        for doc in tasks_collection.find().sort('created_at', -1):
            doc['_id'] = str(doc['_id'])
            tasks.append(doc)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    new_task = {
        'name': data['name'],
        'category': data['category'],
        'date': data['date'],
        'completed': False,
        'created_at': datetime.now()
    }
    result = tasks_collection.insert_one(new_task)
    return jsonify({'msg': 'Berhasil ditambah', 'id': str(result.inserted_id)})

@app.route('/api/tasks/<id>', methods=['PUT'])
def update_task(id):
    data = request.json
    update_data = {}
    
    if 'name' in data: update_data['name'] = data['name']
    if 'category' in data: update_data['category'] = data['category']
    if 'date' in data: update_data['date'] = data['date']
    if 'completed' in data: update_data['completed'] = data['completed']

    tasks_collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
    return jsonify({'msg': 'Berhasil diupdate'})

@app.route('/api/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    tasks_collection.delete_one({'_id': ObjectId(id)})
    return jsonify({'msg': 'Berhasil dihapus'})

if __name__ == '__main__':
    app.run(debug=True)