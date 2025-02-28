import json
import logging
import threading
import time
from typing import Dict, Any

import pika
from sqlalchemy.orm import Session
from sqlalchemy import select

from .dependencies import SessionLocal
from .config import settings
from .schemas import BookCreate
from .crud import books
from .models import Lending, Book


# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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

# Define event handlers using SQLAlchemy 2.0 query methods
def handle_book_created(data: Dict[str, Any], db: Session):
    """Handle book_created events from admin service"""
    logger.info(f"Processing book_created event: {data}")
    
    # Check if book already exists in frontend database
    if data.get('isbn'):
        # Use select statement instead of query
        stmt = select(Book).where(Book.isbn == data['isbn'])
        existing_book = db.execute(stmt).scalar_one_or_none()
        
        if existing_book:
            logger.info(f"Book with ISBN {data['isbn']} already exists, updating")
            # Update existing book
            for key, value in data.items():
                if hasattr(existing_book, key):
                    setattr(existing_book, key, value)
            db.add(existing_book)
            db.commit()
            db.refresh(existing_book)
            return
    
    # Create new book in frontend database
    book_data = BookCreate(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn'],
        publisher=data['publisher'],
        category=data['category'],
        publication_year=data['publication_year'],
        description=data.get('description')
    )
    books.book.create(db=db, obj_in=book_data)

def handle_book_updated(data: Dict[str, Any], db: Session):
    """Handle book_updated events from admin service"""
    logger.info(f"Processing book_updated event: {data}")
    
    # Find the book in frontend database
    book_id = data.get('id')
    if not book_id:
        logger.error("Book ID missing in update event")
        return
    
    # Use select statement for querying
    stmt = select(Book).where(Book.id == book_id)
    existing_book = db.execute(stmt).scalar_one_or_none()
    
    if not existing_book and data.get('isbn'):
        # Fallback to finding by ISBN
        stmt = select(Book).where(Book.isbn == data['isbn'])
        existing_book = db.execute(stmt).scalar_one_or_none()
    
    if existing_book:
        # Update the book
        for key, value in data.items():
            if hasattr(existing_book, key):
                setattr(existing_book, key, value)
        db.add(existing_book)
        db.commit()
        db.refresh(existing_book)
    else:
        logger.error(f"Book with ID {book_id} and ISBN {data.get('isbn')} not found, cannot update")

def handle_book_borrowed(data: Dict[str, Any], db: Session):
    """Handle book_borrowed events from frontend service"""
    logger.info(f"Processing book_borrowed event: {data}")
    
    # Use select statement to check existing lending
    lending_id = data.get('id')
    if lending_id:
        stmt = select(Lending).where(Lending.id == lending_id)
        existing_lending = db.execute(stmt).scalar_one_or_none()
        
        if existing_lending:
            # Update existing record
            for key, value in data.items():
                if hasattr(existing_lending, key):
                    setattr(existing_lending, key, value)
            db.add(existing_lending)
            db.commit()
            return
    
    # Create new lending record
    new_lending = Lending(
        id=data.get('id'),
        user_id=data.get('user_id'),
        book_id=data.get('book_id'),
        borrow_date=data.get('borrow_date'),
        due_date=data.get('due_date'),
        return_date=data.get('return_date')
    )
    
    db.add(new_lending)
    db.commit()

def handle_book_returned(data: Dict[str, Any], db: Session):
    """Handle book_returned events from admin service"""
    book_id = data.get("book_id")
    if not book_id:
        logger.error("Book ID missing in book_returned event")
        return
    
    # Use select statement to find the book
    stmt = select(Book).where(Book.id == book_id)
    book = db.execute(stmt).scalar_one_or_none()
    
    if book:
        # Update book availability
        book.is_available = True
        db.add(book)
        db.commit()
        db.refresh(book)
    else:
        logger.error(f"Book with ID {book_id} not found for updating availability")

def handle_book_deleted(data: Dict[str, Any], db: Session):
    """Handle book_deleted events from admin service"""
    logger.info(f"Processing book_deleted event: {data}")
    
    # Find and delete the book in frontend database
    book_id = data.get('id')
    if not book_id:
        logger.error("Book ID missing in delete event")
        return
    
    # Use select statement to find the book
    stmt = select(Book).where(Book.id == book_id)
    existing_book = db.execute(stmt).scalar_one_or_none()
    
    if existing_book:
        db.delete(existing_book)
        db.commit()
    else:
        logger.warning(f"Book with ID {book_id} not found for deletion")

# Map event types to handler functions
EVENT_HANDLERS = {
    'book_created': handle_book_created,
    'book_updated': handle_book_updated,
    'book_deleted': handle_book_deleted,
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
                
                # Declare a queue and bind it to all admin events
                result = channel.queue_declare(queue='frontend_service_queue', durable=True)
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
                
                logger.info("Frontend service consumer started. Waiting for messages...")
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

# Only start the consumer if this script is run directly
if __name__ == "__main__":
    start_consumer()