from sqlalchemy import text
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.sql import func
from config.extensions import db

class Categories(db.Model, SerializerMixin):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    
    products = db.relationship('Products', backref='category', lazy=True)

    def __repr__(self):
        return f"<Category '{self.name}'>"


class Products(db.Model, SerializerMixin):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    descriptions = db.Column(db.String(50),nullable=False, unique=True)
    qty= db.Column(db.Integer, server_default=text("0"))
    unit = db.Column(db.String(10),nullable=False)
    costprice = db.Column(db.Numeric(10, 2), nullable=False, server_default=text("0.00"))
    sellprice = db.Column(db.Numeric(10, 2), nullable=False, server_default=text("0.00"))
    saleprice = db.Column(db.Numeric(10, 2), nullable=False, server_default=text("0.00"))        
    alertstocks = db.Column(db.Integer, server_default=text("0"))
    criticalstocks = db.Column(db.Integer, server_default=text("0"))
    productpicture = db.Column(db.String(20))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category.name,
            'descriptions': self.descriptions,
            'qty': self.qty,
            'unit': self.unit,
            'costprice': self.costprice,
            'sellprice': self.sellprice,
            'saleprice': self.saleprice,
            'productpicture': self.productpicture,
            'alertstocks': self.alertstocks,
            'criticalstocks': self.criticalstocks,
        }

    def __repr__(self):
        return f"<Products '{self.id}','{self.category}','{self.descriptions}'>"
