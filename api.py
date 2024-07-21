import os
from flask import Flask, request, jsonify
from pymongo.mongo_client import MongoClient
from datetime import datetime
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URL'))
db = client['sic']
collections = db['sensor_data']

@app.route('/', methods=['GET'])
def home():
    return "Ini Flask API"

@app.route('/api/v1/sic5/sensor-data', methods=['POST'])
def store_data():
    try:
        data = request.get_json()
        
        if not all(k in data for k in ('temperature', 'humidity', 'aqi')):
            raise ValueError("Missing required sensor data fields")

        sensor_data = {
            'temperature': data.temperature,
            'humidity': data.humidity,
            'aqi': data.aqi,
            'datetime': datetime.now()
        }

        collections.insert_one(sensor_data)
        
        response = {
            "status": "Success",
            "message": "Data received",
            "data": sensor_data,
            "result": predict(sensor_data)
        }
        
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"status": "Error", "message": str(ve)}), 400

    except Exception as e:
        return jsonify({"status": "Error", "message": "An error occurred", "details": str(e)}), 500

@app.route('/api/v1/sic5/sensor-data', methods=['GET'])
def retrieve_data():
    try:
        data = list(collections.find().sort('datetime', -1).limit(10))
        
        data.reverse()

        for item in data:
            item['_id'] = str(item['_id'])

        response = {
            "status": "Success",
            "message": "Data retrieved",
            "data": data
        }
        
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"status": "Error", "message": "An error occurred", "details": str(e)}), 500
    
def predict(sensor_data):
    return 'BAIK'

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)