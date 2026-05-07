import json
from flask import Blueprint, jsonify # type: ignore
from app.services.product_service import get_paginated_products
from confluent_kafka import Producer # type: ignore
from app.models.product import Products, Categories

api_productcategory = Blueprint('api_productcategory', __name__, url_prefix='/api')
 
producer_config = {'bootstrap.servers': '127.0.0.1:9092'}
producer = Producer(producer_config)

def delivery_report(err, msg):
    if err is not None:
        print(f"Product Category Message delivery failed: {err}")
    else:
        print(f"Product Category Message delivered to {msg.topic()} [{msg.partition()}]")

@api_productcategory.route('/products/category', methods=['GET'])
def product_category():
    categories = Categories.query.all()
    data = []

    for cat in categories:
        cat_data = {
            'category': cat.name,
            'products': [
                {
                    'id': p.id,
                    'descriptions': p.descriptions,
                    'qty': p.qty,
                    'unit': p.unit,
                    'costprice': float(p.costprice), # Numeric needs conversion to float for JSON
                    'sellprice': float(p.sellprice)
                } for p in cat.products
            ]
        }
        data.append(cat_data)

    if data is None:
        return jsonify({
            'message': 'No record(s) found.'
        }), 404

    message_payload = {
        "event": "product_category_viewed",
        "count": len(data)
    }
    
    producer.produce(
        'central-topic', 
        value=json.dumps(message_payload).encode('utf-8'),
        on_delivery=delivery_report
    )

    producer.flush()

    return jsonify(data), 200