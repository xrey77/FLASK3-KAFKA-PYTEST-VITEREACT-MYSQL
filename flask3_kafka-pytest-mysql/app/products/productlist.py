import json
from flask import Blueprint, jsonify # type: ignore
from app.services.product_service import get_paginated_products
from confluent_kafka import Producer # type: ignore

api_prodlist = Blueprint('api_prodlist', __name__, url_prefix='/api') 

producer_config = {'bootstrap.servers': '127.0.0.1:9092', 'linger.ms': 10}   # Reduced latency for 10ms
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Product List Message delivery failed: {err}")
    else:
        print(f"Product List Message delivered to {msg.topic()} [{msg.partition()}]")

@api_prodlist.route('/products/list/<int:page>', methods=['GET'])
def product_list(page):
    # Call the service
    data = get_paginated_products(page)
    if data is None:
        return jsonify({
            'message': 'No record(s) found.'
        }), 404

    message_payload = {
        "event": "product_list_viewed",
        "page": page,
        "count": len(data.items())
    }
    
    producer.produce(
        'central-topic', 
        value=json.dumps(message_payload).encode('utf-8'),
        on_delivery=delivery_report
    )

    producer.flush(timeout=5)

    return jsonify(data), 200