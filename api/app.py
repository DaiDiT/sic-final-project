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
        
        if not all(k in data for k in ('temperature', 'humidity', 'CO', 'CO2')):
            raise ValueError("Missing required sensor data fields")

        sensor_data = {
            'temperature': data['temperature'],
            'humidity': data['humidity'],
            'CO': data['CO'],
            'CO2': data['CO2'],
            'timestamp': datetime.now()
        }

        collections.insert_one(sensor_data)
        
        sensor_data['_id'] = str(sensor_data['_id'])
        
        response = {
            "status": "Success",
            "message": "Data received",
            "data": sensor_data
        }
        
        return jsonify(response), 200

    except ValueError as ve:
        return jsonify({"status": "Error", "message": str(ve)}), 400

    except Exception as e:
        return jsonify({"status": "Error", "message": "An error occurred", "details": str(e)}), 500

@app.route('/api/v1/sic5/sensor-data', methods=['GET'])
def retrieve_data():
    try:
        data = collections.find_one(sort=[('timestamp', -1)])
        
        if data:
            data['_id'] = str(data['_id'])
        else:
            data = {}
        
        return jsonify(data), 200

    except Exception as e:
        return jsonify({"status": "Error", "message": "An error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000)