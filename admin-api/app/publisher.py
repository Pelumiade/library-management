# admin-api/app/message_broker/publisher.py
import json
import pika
import logging
from app.config import settings

logger = logging.getLogger(__name__)

def get_connection():
    """Establish a connection to RabbitMQ"""
    credentials = pika.PlainCredentials(
        settings.RABBITMQ_USER,
        settings.RABBITMQ_PASSWORD
    )
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        virtual_host='/',
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

def publish_event(event_type: str, payload: dict):
    """Publish an event to RabbitMQ"""
    try:
        connection = get_connection()
        channel = connection.channel()
        
        # Ensure the exchange exists
        channel.exchange_declare(
            exchange='library_events',
            exchange_type='topic',
            durable=True
        )
        
        # Prepare the message
        message = {
            "event_type": event_type,
            "payload": payload
        }
        
        # Publish the message
        channel.basic_publish(
            exchange='library_events',
            routing_key=event_type,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                content_type='application/json'
            )
        )
        
        logger.info(f"Published {event_type} event: {payload}")
        connection.close()
    except Exception as e:
        logger.error(f"Error publishing event: {str(e)}")
        raise

