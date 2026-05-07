import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy.orm import DeclarativeBase # type: ignore
from sqlalchemy import text # type: ignore
from config.extensions import db
from app.models.user import Users, Roles, Departments
from app.models.product import Products, Categories
from app.models.sale import Sales
class Base(DeclarativeBase):
    pass

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_MYSQL_URI')


def setup_db(app):
    print("Initializing Database...")    
    db.init_app(app)
    
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print("Database connection successful!")
            
            from app.models.user import Users, Roles, Departments
            from app.models.product import Products, Categories           
            from app.models.sale import Sales
            db.create_all() 
            print("Tables created.")
        except Exception as e:
            print(f"Database connection failed: {e}")
