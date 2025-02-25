import json
import pika
import threading
import logging
from sqlalchemy.orm import Session
from app.config import settings
from app.crud import book as book_crud
from app.schemas.book import BookCreate
from app.dependencies import get_db

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

def callback(ch, method, properties, body, db: Session):
    """Process received messages"""
    try:
        message = json.loads(body)
        event_type = message.get("event_type")
        payload = message.get("payload")
        
        logger.info(f"Received {event_type} event: {payload}")
        
        if event_type == "book_created":
            # Create the book in the frontend database
            book_in = BookCreate(**payload)
            book_crud.create(db=db, obj_in=book_in)
            logger.info(f"Created book in frontend database: {payload}")
            
        elif event_type == "book_deleted":
            # Delete the book from the frontend database
            book_id = payload.get("id")
            book = book_crud.get(db=db, id=book_id)
            if book:
                book_crud.remove(db=db, id=book_id)
                logger.info(f"Removed book from frontend database: {book_id}")
        
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        # Negative acknowledgement
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_consumer():
    """Start the RabbitMQ consumer in a background thread"""
    db = next(get_db())
    
    def consumer_thread():
        connection = get_connection()
        channel = connection.channel()
        
        # Ensure the exchange exists
        channel.exchange_declare(
            exchange='library_events',
            exchange_type='topic',
            durable=True
        )
        
        # Create a queue for this service
        result = channel.queue_declare(queue='frontend_api_queue', durable=True)
        queue_name = result.method.queue
        
        # Bind the queue to the exchange for specific event types
        channel.queue_bind(
            exchange='library_events',
            queue=queue_name,
            routing_key='book_created'
        )
        channel.queue_bind(
            exchange='library_events',
            queue=queue_name,
            routing_key='book_deleted'
        )
        
        # Set up the callback
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=lambda ch, method, properties, body: 
                callback(ch, method, properties, body, db)
        )
        
        logger.info('Starting to consume messages...')
        channel.start_consuming()
    
    # Start the consumer in a background thread
    thread = threading.Thread(target=consumer_thread)
    thread.daemon = True
    thread.start()
    logger.info("Message consumer started in background thread")