import json
from flask import Blueprint, jsonify, request # type: ignore
from app.services.auth_service import verify_user_totp
from confluent_kafka import Producer # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore

api_otp = Blueprint('api_otp', __name__, url_prefix='/auth') 

producer_config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"MFA Verification Message delivery failed: {err}")
    else:
        print(f"MFA Verification Message delivered to {msg.topic()} [{msg.partition()}]")


@api_otp.route('/mfa/verifytotp/<int:id>', methods=['PATCH'])
@jwt_required()
def verify_otp(id):
    data = request.get_json()
    otp = data.get("otp")
    user_id = get_jwt_identity() 

    if not otp:
        return jsonify({"message": "OTP is required"}), 400

    try:
        # Call the service
        result = verify_user_totp(id, otp)

        message_payload = {
            "event": "user_mfa_verification",
            "user_id": user_id
        }
        
        producer.produce(
            'central-topic', 
            value=json.dumps(message_payload).encode('utf-8'),
            on_delivery=delivery_report
        )

        producer.flush()


        return jsonify(result), 200
    except Exception as e:
        # Catch the BadRequest or NotFound raised in the service
        return jsonify({"message": str(e)}), getattr(e, 'code', 400)

