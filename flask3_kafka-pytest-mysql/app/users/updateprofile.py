import json
from flask import Blueprint, jsonify, request # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from app.services.user_service import update_user_profile
from confluent_kafka import Producer # type: ignore

api_profile = Blueprint('api_profile', __name__, url_prefix='/api') 

producer_config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Profile Update Message delivery failed: {err}")
    else:
        print(f"Profile Update Message delivered to {msg.topic()} [{msg.partition()}]")

@api_profile.route('/updateprofile/<int:id>', methods=['PATCH'])
@jwt_required()
def update_profile(id):
    user_id = get_jwt_identity() 
    try:
        req_data = request.get_json()
        
        # Call the service layer
        update_user_profile(id, req_data)
        
        message_payload = {
            "event": "user_profile_update",
            "user_id": user_id
        }
        
        producer.produce(
            'central-topic', 
            value=json.dumps(message_payload).encode('utf-8'),
            on_delivery=delivery_report
        )

        producer.flush()

        return jsonify({
            "message": "Your profile info has been updated."
        }), 200
        
    except Exception as e:
        return jsonify({"message": str(e)}), 400