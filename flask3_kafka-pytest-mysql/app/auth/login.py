import json
from flask import Blueprint, jsonify, request # type: ignore
from app.services.auth_service import authenticate_user
from confluent_kafka import Producer # type: ignore

api_signin = Blueprint('api_signin', __name__, url_prefix='/auth')

producer_config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"User Login Message delivery failed: {err}")
    else:
        print(f"User Login Message delivered to {msg.topic()} [{msg.partition()}]")

@api_signin.route('/signin', methods=['POST'])
def user_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # Call the service
    error, user_info = authenticate_user(username, password)

    if error:
        return jsonify({"message": error["error"]}), error["status"]


    message_payload = {
        "event": "user_login",
        "user_id": user_info.get("id"),
        "email": user_info.get("email")
    }
    
    producer.produce(
        'central-topic', 
        value=json.dumps(message_payload).encode('utf-8'),
        on_delivery=delivery_report
    )

    producer.flush()


    return jsonify(user_info), 200

