import os
from flask import Flask, url_for, Blueprint, jsonify, request, send_from_directory, make_response
api_prodpic = Blueprint('api_prodpic', __name__, url_prefix='/api') # Use url_prefix to group all API routes

app = Flask(__name__) 

basedir = os.path.abspath(os.path.dirname('static'))
IMAGES_DIR = os.path.join(basedir, 'static/products/')

@api_prodpic.route('/products/<filename>', methods=['GET'])
def staticImage(filename):    
    try:
        return send_from_directory(IMAGES_DIR, filename)    
    except FileNotFoundError:
        return make_response({"error": "Image not found"}, 404)
    
