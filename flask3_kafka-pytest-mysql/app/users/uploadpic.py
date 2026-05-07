import json
from flask import Blueprint, jsonify, request # type: ignore
from app.services.user_service import update_profile_picture
from confluent_kafka import Producer # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore

api_profilepic = Blueprint('api_profilepic', __name__, url_prefix='/api')

producer_config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Upload Profile Picture Message delivery failed: {err}")
    else:
        print(f"Upload Profile Picture Message delivered to {msg.topic()} [{msg.partition()}]")

@api_profilepic.route('/uploadpicture/<int:id>', methods=['PATCH'])
@jwt_required()
def profile_picture(id):
    user_id = get_jwt_identity() 
    if 'userpic' not in request.files:
        return jsonify({"message": "No Image found."}), 400
    
    file = request.files['userpic']
    result, status_code = update_profile_picture(id, file)
    
    message_payload = {
        "event": "user_upload_picture",
        "user_id": user_id
    }
    
    producer.produce(
        'central-topic', 
        value=json.dumps(message_payload).encode('utf-8'),
        on_delivery=delivery_report
    )

    producer.flush()

    return jsonify(result), status_code