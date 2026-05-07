import json
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from flask import Blueprint, jsonify # type: ignore
from app.services.user_service import get_users_paginated
from confluent_kafka import Producer # type: ignore

api_getusers = Blueprint('api_getusers', __name__, url_prefix='/api')

producer_config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Get Users Message delivery failed: {err}")
    else:
        print(f"Get Users Message delivered to {msg.topic()} [{msg.partition()}]")


@api_getusers.route('/getallusers/<int:page>', methods=['GET'])
@jwt_required()
def get_users_route(page):
    try:
        user_id = get_jwt_identity() 
        data = get_users_paginated(page)
        if not data["users"]:
            return jsonify({'message': "No record(s) found."}), 404
            
        message_payload = {
            "event": "users_get_all",
            "user_id": user_id
        }
        
        producer.produce(
            'central-topic', 
            value=json.dumps(message_payload).encode('utf-8'),
            on_delivery=delivery_report
        )

        producer.flush()

        return jsonify({
            "page": page,
            "totpage": data["total_pages"],
            "totalrecords": data["total_records"],
            "users": data["users"]
        }), 200
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'message': f"Error! {str(e)}"}), 500        
