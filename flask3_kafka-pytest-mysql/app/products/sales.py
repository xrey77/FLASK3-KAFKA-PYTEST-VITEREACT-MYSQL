import json
from flask import Blueprint, jsonify # type: ignore
from config.extensions import db
from app.models.sale import Sales
from confluent_kafka import Producer # type: ignore

api_sales = Blueprint('api_sales', __name__, url_prefix='/api')

producer_config = {'bootstrap.servers': '127.0.0.1:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Sales Data Message delivery failed: {err}")
    else:
        print(f"Sales Data Message delivered to {msg.topic()} [{msg.partition()}]")

@api_sales.route('/getsales', methods=['GET'])
def get_sales_route():
    try:
        query = db.select(Sales)
        sales_records = db.session.execute(query).scalars().all()
        print(sales_records)
        if not sales_records:
            return jsonify({'message': "No record(s) found."}), 404
            
        sales_list = []
        for sale in sales_records:
            sales_list.append({
                "id": sale.id,
                "salesamount": sale.salesamount,
                "salesdate": sale.salesdate.isoformat() if sale.salesdate else None
            })


        message_payload = {
            "event": "sales_data_viewed",
            "count": len(sales_list)
        }
        
        producer.produce(
            'central-topic', 
            value=json.dumps(message_payload).encode('utf-8'),
            on_delivery=delivery_report
        )

        producer.flush() 

        return jsonify({
            "sales": sales_list
        }), 200
        
    except Exception as e:
        return jsonify({'message': f"Error! {str(e)}"}), 500
