import json
from flask import Blueprint, jsonify, request # type: ignore
from confluent_kafka import Producer # type: ignore

api_signup = Blueprint('api_signup', __name__, url_prefix='/auth')

producer_config = {'bootstrap.servers': '127.0.0.1:9092', 'linger.ms': 10}   # Reduced latency for 10ms
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"User Registration Message delivery failed: {err}")
    else:
        print(f"User Registration Message delivered to {msg.topic()} [{msg.partition()}]")

@api_signup.route('/signup', methods=['POST'])
def userRegister():
    from app.services.auth_service import register_user    
    req_data = request.get_json()
    
    try:
        user = register_user(req_data)

        message_payload = {
            "event": "user_registration",
            "user_id": user.id,
            "email": user.email
        }
        
        producer.produce(
            'central-topic', 
            value=json.dumps(message_payload).encode('utf-8'),
            on_delivery=delivery_report
        )

        producer.flush(timeout=5)

        return jsonify({
            "message": "You have registered successfully, please sign-in now."
        }), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Server Error: {str(e)}"}), 500
