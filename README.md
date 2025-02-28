# Library Management System

![Coverage](coverage_badge.svg)

A modern, microservices-based application for managing library resources, built with Python, FastAPI, and RabbitMQ.

## Overview

This Library Management System is designed with a microservices architecture, consisting of two independent API services that communicate through message queuing. The system allows users to browse the library catalog, borrow books, and return them, while administrators can manage the inventory of books.

### Features

#### Frontend API
- User enrollment using email, first name, and last name
- Browsing available books in the catalog
- Retrieving book details by ID
- Filtering books by publishers and categories
- Book borrowing with customizable duration periods
- Book return functionality

#### Admin API
- Adding new books to the catalog
- Removing books from the catalog
- Listing enrolled library users
- Tracking borrowed books and their availability status
- Viewing unavailable books with their expected return dates

## Architecture

The application is built using the following architecture:

- **Microservices**: Two independent API services (Frontend and Admin)
- **Database Isolation**: Each service uses its own database
- **Message Queue**: RabbitMQ for inter-service communication
- **Containerization**: Docker for deployment and scaling
- **REST API**: FastAPI for creating performant API endpoints

## Technology Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL, SQLAlchemy ORM
- **Message Broker**: RabbitMQ
- **Development**: Alembic for migrations, Pydantic for data validation
- **Testing**: Pytest for unit and integration tests
- **Deployment**: Docker, AWS EC2

## Deployment

This application is deployed on an AWS EC2 instance with the following endpoints:

- **Admin API Documentation**: [https://www.cryptofrere.org/admin/docs](https://www.cryptofrere.org/admin/docs)
- **Frontend API Documentation**: [https://www.cryptofrere.org/frontend/docs](https://www.cryptofrere.org/frontend/docs)
- **RabbitMQ Management Interface**: [https://www.cryptofrere.org/rabbitmq/#/](https://www.cryptofrere.org/rabbitmq/#/)

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.8+
- PostgreSQL
- RabbitMQ

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Pelumiade/library-management.git
   cd library-management
   ```

2. Set up environment variables:
   ```bash
   # Create .env files for both services
   cp frontend_api/.env.example frontend_api/.env
   cp admin_api/.env.example admin_api/.env
   
   # Edit the .env files with your configuration
   ```

3. Start the services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. The APIs will be available at:
   - Frontend API: http://localhost:8000
   - Admin API: http://localhost:8001
   - RabbitMQ Management: http://localhost:15672

### Running Tests

```bash
# Run tests for Frontend API
cd frontend_api
python -m pytest

# Run tests for Admin API
cd admin_api
python -m pytest
```

## API Documentation

When the application is running, you can access the interactive API documentation:

- Frontend API: http://localhost:8000/docs
- Admin API: http://localhost:8001/docs

## Communication Between Services

The two API services communicate asynchronously through RabbitMQ messages:

1. When Admin API adds/updates/removes a book, it publishes a message to RabbitMQ
2. The Frontend API consumes these messages and updates its database accordingly
3. This ensures that the catalog stays in sync between both services

## Database Schema

### Frontend API Database

- **Users**: Stores user information (email, first name, last name)
- **Books**: Mirror of the catalog maintained by Admin API
- **Lending**: Records of books borrowed by users

### Admin API Database

- **Books**: The authoritative source for the book catalog
- **Users**: Mirror of users registered through Frontend API
- **Lending**: Mirror of lending records from Frontend API

## Acknowledgements

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- RabbitMQ: https://www.rabbitmq.com/
