import json
from flask import Blueprint, jsonify, request # type: ignore
from flask_jwt_extended import jwt_required, get_jwt_identity # type: ignore
from flask_bcrypt import Bcrypt # type: ignore
from config.extensions import db
from app.models.user import Users
from confluent_kafka import Producer # type: ignore

api_changepwd = Blueprint('api_changepwd', __name__, url_prefix='/api')
bcrypt = Bcrypt()

producer_config = {'bootstrap.servers': 'localhost:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Change Password Message delivery failed: {err}")
    else:
        print(f"Change Password Message delivered to {msg.topic()} [{msg.partition()}]")


@api_changepwd.route('/changepassword/<int:id>', methods=['PATCH'])
@jwt_required()
def changePassword(id):
    req = request.get_json()
    pwd = req["password"]    
    user =  db.get_or_404(Users, id)    
    if user is not None:
        hash = bcrypt.generate_password_hash(pwd).decode('utf-8')
        user.password = hash
        db.session.commit()

        message_payload = {
            "event": "user_change_password",
            "user_id": user.id
        }
        
        producer.produce(
            'central-topic', 
            value=json.dumps(message_payload).encode('utf-8'),
            on_delivery=delivery_report
        )

        producer.flush()

        return jsonify({
            'message': 'You have change your password successfully.'
            }), 200        
    else:
        return jsonify({"message": "User ID is not found."}), 404

