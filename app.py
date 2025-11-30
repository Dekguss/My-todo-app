from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='')

# --- KONFIGURASI MONGODB ATLAS (ONLINE) ---
CONNECTION_STRING = "mongodb+srv://dwiadnyana:041002Dekgus@cluster0.rv3yldr.mongodb.net/kuliah_db?retryWrites=true&w=majority&appName=Cluster0"

# Inisialisasi koneksi MongoDB
try:
    client = MongoClient(CONNECTION_STRING)
    # Test koneksi
    client.admin.command('ping')
    db = client.get_database('kuliah_db')
    tasks_collection = db['tasks']
    print("✅ Berhasil terhubung ke MongoDB Atlas!")
except Exception as e:
    print(f"❌ Gagal terhubung ke MongoDB: {e}")
    db = None
    tasks_collection = None

# Middleware untuk mengecek koneksi database
@app.before_request
def check_db_connection():
    if request.endpoint and request.endpoint != 'static' and not db:
        return jsonify({'error': 'Database connection failed'}), 500

@app.route('/')
def index():
    return render_template('index.html')

# --- API ENDPOINTS ---

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = []
    try:
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
    try:
        result = tasks_collection.insert_one(new_task)
        new_task['_id'] = str(result.inserted_id)
        return jsonify({'msg': 'Berhasil ditambah', 'task': new_task})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<id>', methods=['PUT'])
def update_task(id):
    data = request.json
    update_data = {}
    
    if 'name' in data: update_data['name'] = data['name']
    if 'category' in data: update_data['category'] = data['category']
    if 'date' in data: update_data['date'] = data['date']
    if 'completed' in data: update_data['completed'] = data['completed']

    try:
        result = tasks_collection.update_one(
            {'_id': ObjectId(id)}, 
            {'$set': update_data}
        )
        if result.matched_count == 0:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify({'msg': 'Berhasil diupdate'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    try:
        result = tasks_collection.delete_one({'_id': ObjectId(id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Task not found'}), 404
        return jsonify({'msg': 'Berhasil dihapus'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Handler untuk Vercel
def vercel_handler(request):
    from flask import Response
    with app.app_context():
        response = app.full_dispatch_request()
        return Response(
            response=response.get_data(),
            status=response.status_code,
            headers=dict(response.headers)
        )

# Gunakan ini untuk development lokal
if __name__ == '__main__':
    app.run(debug=True)