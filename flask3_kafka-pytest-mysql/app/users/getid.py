import json
from flask import Blueprint, jsonify # type: ignore
from flask_jwt_extended import jwt_required # type: ignore
from config.extensions import db
from app.models.user import Users
from app.services.user_service import UserService
from confluent_kafka import Producer # type: ignore

api_getuserid = Blueprint('api_getuserid', __name__, url_prefix='/api') 

producer_config = {'bootstrap.servers': '127.0.0.1:9092', 'linger.ms': 10}   # Reduced latency for 10ms
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Get User ID Message delivery failed: {err}")
    else:
        print(f"Get User ID Message delivered to {msg.topic()} [{msg.partition()}]")


@api_getuserid.route('/getuserid/<int:id>', methods=['GET'])
@jwt_required()
def get_user_id(id):
    try:
        user_data = UserService.get_user_by_id(id)

        message_payload = {
            "event": "user_get_id",
            "user_id": user_data['id'],
            "email": user_data['email']
        }
        
        producer.produce(
            'central-topic', 
            value=json.dumps(message_payload).encode('utf-8'),
            on_delivery=delivery_report
        )        

        producer.flush(timeout=5)

        return jsonify(user_data), 200
    except Exception as e:
        return jsonify({"message": "User ID not found."}), 404

