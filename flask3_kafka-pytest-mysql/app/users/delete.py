import json
from flask import Blueprint, jsonify, request # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from config.extensions import db
from app.models.user import Users
from confluent_kafka import Producer # type: ignore

api_deleteuser = Blueprint('api_deleteuser', __name__, url_prefix='/api') 

producer_config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"User Delete Message delivery failed: {err}")
    else:
        print(f"User Delete Message delivered to {msg.topic()} [{msg.partition()}]")


@api_deleteuser.route('/deleteuser/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteUser(id):
    try:
        user =  db.get_or_404(Users, id)    
        if user is not None:
            db.session.delete(user)     
            db.session.commit()
            
            message_payload = {
                "event": "user_delete",
                "user_id": user.id
            }
            
            producer.produce(
                'central-topic', 
                value=json.dumps(message_payload).encode('utf-8'),
                on_delivery=delivery_report
            )

            producer.flush()

            return jsonify({'message': f'User ID {id} has been deleted.'}), 200
        
    except Exception as e:
        return jsonify({"message": "User ID not found."}), 404