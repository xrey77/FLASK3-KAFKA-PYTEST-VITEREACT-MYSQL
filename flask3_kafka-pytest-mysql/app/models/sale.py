from sqlalchemy import text
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.sql import func
from config.extensions import db

class Sales(db.Model, SerializerMixin):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    # Renamed to salesdate to match your methods
    salesamount = db.Column(db.Numeric(10, 2), nullable=False, server_default=text("0.00"))
    salesdate = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # OPTIONAL: If you want to use the mixin's better to_dict, 
    # remove this block entirely.
    def to_dict(self):
        return {
            'id': self.id,
            'salesamount': float(self.salesamount) if self.salesamount else 0.0,
            'salesdate': self.salesdate.isoformat() if self.salesdate else None,
        }

    def __repr__(self):
        return f"<Sales id={self.id} amount={self.salesamount} date={self.salesdate}>"
