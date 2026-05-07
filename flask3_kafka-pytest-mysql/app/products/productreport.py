import json
from flask import Blueprint, jsonify # type: ignore
from sqlalchemy import select # type: ignore
from config.extensions import db
from app.models.product import Products, Categories
from confluent_kafka import Producer # type: ignore

api_productreport = Blueprint('api_productreport', __name__, url_prefix='/api')

producer_config = {'bootstrap.servers': '127.0.0.1:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Product Report Message delivery failed: {err}")
    else:
        print(f"Product Report Message delivered to {msg.topic()} [{msg.partition()}]")

@api_productreport.route('/productreport', methods=['GET'])
def productReport():
    try:
        # 1. Define the selection statement
        stmt = select(
            Products.id,
            Categories.name.label('category'),
            Products.descriptions,
            Products.qty,
            Products.unit,
            Products.costprice,
            Products.sellprice # Ensure this is in your model
        ).join(Categories)

        # 2. Execute directly (Recommended for Flask 3/SQLAlchemy 2.0)
        # We use .mappings() to easily access columns by name
        products_records = db.session.execute(stmt).mappings().all()

        if not products_records:
            return jsonify({'message': "No record(s) found."}), 404
            
        # 3. Convert records to a list of dictionaries
        products_list = [dict(row) for row in products_records]

        # 4. Correct payload logic (removed .items())
        message_payload = {
            "event": "sales_data_viewed",
            "count": len(products_list)
        }
        
        producer.produce(
            'central-topic', 
            value=json.dumps(message_payload).encode('utf-8'),
            on_delivery=delivery_report
        )
        producer.flush() 

        return jsonify({"products": products_list}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
