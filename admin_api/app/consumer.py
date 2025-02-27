import json
import logging
import threading
import time
from typing import Dict, Any

import pika
from sqlalchemy.orm import Session

from .dependencies import SessionLocal
from .config import settings
from . import crud, schemas

# Configure logging
logging.basicConfig(level=logging.INFO)
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

# Define event handlers
def handle_user_created(data: Dict[str, Any], db: Session):
    """Handle user_created events from frontend service"""
    logger.info(f"Processing user_created event: {data}")
    
    # Check if user already exists in admin database
    if data.get('email'):
        existing_user = crud.user.get_by_email(db, email=data['email'])
        if existing_user:
            logger.info(f"User with email {data['email']} already exists, skipping")
            return
    
    # Create new user in admin database using the UserCreate schema
    user_data = schemas.UserCreate(
        email=data.get("email"),
        first_name=data.get("first_name"),
        last_name=data.get("last_name")
    )
    crud.user.create(db=db, obj_in=user_data)

def handle_book_borrowed(data: Dict[str, Any], db: Session):
    """Handle book_borrowed events from frontend service"""
    logger.info(f"Processing book_borrowed event: {data}")
    
    # Extract data
    book_id = data.get("book_id")
    user_id = data.get("user_id")
    borrow_date = data.get("borrow_date")
    due_date = data.get("due_date")
    
    if not book_id or not user_id:
        logger.error("Book ID or User ID missing in book_borrowed event")
        return
    
    # Check if book exists
    book = crud.book.get(db, id=book_id)
    if not book:
        logger.error(f"Book with ID {book_id} not found")
        return
    
    # Check if user exists
    user = crud.user.get(db, id=user_id)
    if not user:
        logger.error(f"User with ID {user_id} not found")
        return
    
    # Update book availability
    crud.book.update(db=db, db_obj=book, obj_in={"is_available": False})
    
    # Create lending record using the structure from the event
    lending_data = {
        "book_id": book_id,
        "user_id": user_id,
        "borrow_date": borrow_date,
        "due_date": due_date,
        "return_date": data.get("return_date")
    }
    
    # Either create a new record or update existing one
    existing_lending = crud.lending.get_by_book_and_user(
        db, book_id=book_id, user_id=user_id, is_returned=False
    ) if hasattr(crud.lending, 'get_by_book_and_user') else None
    
    if existing_lending:
        crud.lending.update(db=db, db_obj=existing_lending, obj_in=lending_data)
    else:
        crud.lending.create(db=db, obj_in=lending_data)

def handle_book_returned(data: Dict[str, Any], db: Session):
    """Handle book_returned events from frontend service"""
    logger.info(f"Processing book_returned event: {data}")
    
    # Extract data
    book_id = data.get("book_id")
    
    if not book_id:
        logger.error("Book ID missing in book_returned event")
        return
    
    # Check if book exists
    book = crud.book.get(db, id=book_id)
    if not book:
        logger.error(f"Book with ID {book_id} not found")
        return
    
    # Update book availability
    crud.book.update(db=db, db_obj=book, obj_in={"is_available": True})
    
    # Find and update any active lending records for this book
    active_lending = crud.lending.get_active_lending_by_book(db, book_id=book_id)
    if active_lending:
        crud.lending.mark_as_returned(db, lending_id=active_lending.id)

# Map event types to handler functions
EVENT_HANDLERS = {
    'user_created': handle_user_created,
    'book_borrowed': handle_book_borrowed,
    'book_returned': handle_book_returned
}

def callback(ch, method, properties, body, db: Session):
    """Process incoming messages from the queue"""
    try:
        # Parse the message
        message = json.loads(body)
        event_type = message.get('event_type')
        payload = message.get('payload')
        
        logger.info(f"Received {event_type} event")
        
        # Process the event if we have a handler for it
        if event_type in EVENT_HANDLERS:
            handler = EVENT_HANDLERS[event_type]
            handler(payload, db)
            # Acknowledge the message
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logger.warning(f"No handler for event type: {event_type}")
            # Acknowledge the message anyway
            ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        # Reject the message and requeue it
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_consumer():
    """Start the event consumer in a background thread"""
    def consume():
        # Retry connection until RabbitMQ is available
        while True:
            try:
                # Connect to RabbitMQ using the get_connection() function
                connection = get_connection()
                channel = connection.channel()
                
                # Declare the exchange
                channel.exchange_declare(exchange='library_events', exchange_type='topic', durable=True)
                
                # Declare a queue and bind it to all frontend events
                result = channel.queue_declare(queue='admin_service_queue', durable=True)
                queue_name = result.method.queue
                
                # Bind to all relevant event types
                for event_type in EVENT_HANDLERS.keys():
                    channel.queue_bind(
                        exchange='library_events',
                        queue=queue_name,
                        routing_key=event_type
                    )
                
                # Set up the callback with a database session
                def process_message(ch, method, properties, body):
                    db = SessionLocal()
                    try:
                        callback(ch, method, properties, body, db)
                    finally:
                        db.close()
                
                # Configure consumer
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(
                    queue=queue_name,
                    on_message_callback=process_message
                )
                
                logger.info("Admin service consumer started. Waiting for messages...")
                channel.start_consuming()
            except pika.exceptions.AMQPConnectionError:
                logger.warning("Failed to connect to RabbitMQ. Retrying in 5 seconds...")
                time.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error in consumer: {str(e)}")
                time.sleep(5)
    
    # Start the consumer in a background thread
    consumer_thread = threading.Thread(target=consume, daemon=True)
    consumer_thread.start()
    logger.info("Consumer thread started")

start_consumer()