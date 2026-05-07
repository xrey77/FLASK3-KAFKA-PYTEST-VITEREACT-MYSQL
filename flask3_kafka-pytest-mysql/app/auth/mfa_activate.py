import json
from flask import Blueprint, jsonify, request # type: ignore
from app.services.auth_service import mfa_activation
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from confluent_kafka import Producer # type: ignore

api_mfa = Blueprint('api_mfa', __name__, url_prefix='/auth') # Use url_prefix to group all API routes

producer_config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"MFA Activation Message delivery failed: {err}")
    else:
        print(f"MFA Activation Message delivered to {msg.topic()} [{msg.partition()}]")

@api_mfa.route('/mfa/activate/<int:id>', methods=['PATCH'])
@jwt_required()
def mfa_activate(id):
    data = request.get_json()
    enable_mfa = data.get("TwoFactorEnabled", False)
    user_id = get_jwt_identity() 
    result = mfa_activation(id, enable_mfa)

    if result.get("enabled"):

        message_payload = {
            "event": "user_activate_mfa",
            "user_id": user_id
        }
        
        producer.produce(
            'central-topic', 
            value=json.dumps(message_payload).encode('utf-8'),
            on_delivery=delivery_report
        )

        producer.flush()

        return jsonify({
            "qrcodeurl": result["qrcodeurl"],
            "message": "Multi-Factor Authenticator has been enabled."
        }), 200
    


    message_payload = {
        "event": "user_activate_mfa",
        "user_id": user_id
    }
    
    producer.produce(
        'central-topic', 
        value=json.dumps(message_payload).encode('utf-8'),
        on_delivery=delivery_report
    )

    producer.flush()

    return jsonify({
        "message": "Multi-Factor Authenticator has been disabled."
    }), 200
