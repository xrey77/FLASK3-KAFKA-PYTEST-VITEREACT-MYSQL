import json
from flask import Blueprint, jsonify # type: ignore
from app.services.product_service import get_all_sales_service
from confluent_kafka import Producer # type: ignore

api_sales = Blueprint('api_sales', __name__, url_prefix='/api')

producer_config = {'bootstrap.servers': '127.0.0.1:9092', 'linger.ms': 10}   # Reduced latency for 10ms
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Sales Data Message delivery failed: {err}")
    else:
        print(f"Sales Data Message delivered to {msg.topic()} [{msg.partition()}]")

@api_sales.route('/getsales', methods=['GET'])
def get_sales_route():
    try:
        sales_list = get_all_sales_service()
        
        if sales_list is None:
            return jsonify({'message': "No record(s) found."}), 404
            

        message_payload = {
            "event": "sales_data_viewed",
            "count": len(sales_list)
        }
        
        producer.produce(
            'central-topic', 
            value=json.dumps(message_payload).encode('utf-8'),
            on_delivery=delivery_report
        )

        producer.flush(timeout=5)

        return jsonify({
            "sales": sales_list
        }), 200
        
    except Exception as e:
        # Log the error here
        return jsonify({'message': f"Error! {str(e)}"}), 500
