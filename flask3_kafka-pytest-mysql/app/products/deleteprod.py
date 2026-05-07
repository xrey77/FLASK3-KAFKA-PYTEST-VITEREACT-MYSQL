from flask import Blueprint, jsonify # type: ignore
from flask_jwt_extended import jwt_required # type: ignore
from config.extensions import db
from app.models.product import Products
from confluent_kafka import Producer # type: ignore

api_deleteproduct = Blueprint('api_deleteproduct', __name__, url_prefix='/api') 

@api_deleteproduct.route('/deleteproduct/<int:id>', methods=['DELETE'])
@jwt_required()
def deleteProduct(id):
    product =  db.get_or_404(Products, id)    
    if product is not None:
        db.session.delete(product)            
        return jsonify({'message': f'Product ID {id} has been deleted.'}), 200
    else:
        return jsonify({
            "message": "Product ID not found."
        }), 200

