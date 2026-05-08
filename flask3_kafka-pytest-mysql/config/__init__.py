import datetime
import threading
from flask import Flask,jsonify # type: ignore
from flask_jwt_extended import JWTManager # type: ignore
from flask_cors import CORS # type: ignore

# Internal imports
from .db import setup_db
from app.services.kafka_service import KafkaConsumerService
from config.extensions import kafka_producer_service

# Import blueprints/routes
from app.auth.register import api_signup
from app.auth.mfa_activate import api_mfa
from app.auth.mfa_verifyotp import api_otp
from app.users.getid import api_getuserid
from app.users.getusers import api_getusers
from app.users.uploadpic import api_uploadpic
from app.users.updateprofile import api_profile
from app.users.changepassword import api_changepwd
from app.users.delete import api_deleteuser
from app.products.productlist import api_prodlist
from app.products.search import api_prodsearch
from app.products.sales import api_sales
from app.products.deleteprod import api_deleteproduct
from app.products.productreport import api_productreport
from app.products.productcategory import api_productcategory
from app.files.users import api_userpic
from app.files.image import api_image
from app.files.products import api_prodpic
from app.auth.login import api_signin

from config.main import main_bp

def create_app(config_name='default'):     
    app = Flask(__name__, static_url_path='', static_folder='templates')

    # Start the consumer in a daemon thread so it doesn't block Flask
    kafka_consumer_service = KafkaConsumerService(app)
    threading.Thread(target=kafka_consumer_service.start, args=(app,), daemon=True).start()
    kafka_producer_service.init_app(app)
 
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql+pymysql://rey:rey@127.0.0.1/flask3_kafka'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SQLALCHEMY_ECHO'] = True

    app.config["JWT_SECRET_KEY"] = "super-secret-key-that-should-be-long-and-random"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=24)     

    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
    CORS(app, methods=["GET", "POST", "PATCH", "PUT", "DELETE"])

    jwt = JWTManager(app)    
    @jwt.unauthorized_loader
    def custom_unauthorized_callback(err):
        return jsonify({
            'message': 'Unauthorized Access.',
        }), 401    
    
    with app.app_context():
        setup_db(app)


    app.register_blueprint(api_signup)    
    app.register_blueprint(api_mfa)
    app.register_blueprint(api_otp)

    app.register_blueprint(api_getuserid)
    app.register_blueprint(api_getusers)
    app.register_blueprint(api_prodlist)
    app.register_blueprint(api_prodsearch)
    app.register_blueprint(api_productcategory)
    app.register_blueprint(api_sales)
    app.register_blueprint(api_productreport)
    app.register_blueprint(api_deleteuser)
    
    app.register_blueprint(api_uploadpic)
    app.register_blueprint(api_profile)
    app.register_blueprint(api_changepwd)
    
    app.register_blueprint(api_image)
    app.register_blueprint(api_prodpic)
    app.register_blueprint(api_userpic)
    app.register_blueprint(api_signin)

    # app.register_blueprint(main_bp)

    return app

    

