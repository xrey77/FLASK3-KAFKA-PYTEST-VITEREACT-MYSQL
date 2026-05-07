import json
from flask import Blueprint, jsonify # type: ignore
from app.services.product_service import get_product_search_results
from confluent_kafka import Producer # type: ignore

api_prodsearch = Blueprint('api_prodsearch', __name__, url_prefix='/api')

producer_config = {'bootstrap.servers': '127.0.0.1:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Product Search Message delivery failed: {err}")
    else:
        print(f"Product Search Message delivered to {msg.topic()} [{msg.partition()}]")

@api_prodsearch.route('/products/search/<int:page>/<keyword>', methods=['GET'])
def product_search(page, keyword):
    results = get_product_search_results(page, keyword)
    
    if not results['products']:
        return jsonify({'message': 'No record(s) found.'}), 404
    
    message_payload = {
        "event": "product_search_viewed",
        "page": page,
        "count": len(results.items())
    }
    
    producer.produce(
        'central-topic', 
        value=json.dumps(message_payload).encode('utf-8'),
        on_delivery=delivery_report
    )

    producer.flush()

    return jsonify(results), 200
