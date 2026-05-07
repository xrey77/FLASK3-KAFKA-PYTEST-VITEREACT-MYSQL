from confluent_kafka import Producer # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy.orm import DeclarativeBase # type: ignore
from app.services.kafka_service import KafkaProducerService

class Base(DeclarativeBase):
    pass

# The ONLY place db is created
db = SQLAlchemy(model_class=Base)
kafka_producer_service = KafkaProducerService()