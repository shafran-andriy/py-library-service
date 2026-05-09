# Library Service

**Modern Book Borrowing Management System**

---

## Project Description

This project is a backend system designed to modernize a city library’s outdated paper-based workflow.
It digitizes book inventory, user accounts, and borrowings, providing real-time tracking and structured data management. 
The system automatically updates book availability and helps administrators monitor overdue borrowings.
It offers a browsable API interface that allows full interaction without a dedicated front-end.
The service improves operational efficiency for library staff and creates a more convenient borrowing experience for users.

---

## Features

### Books Service
- Full CRUD operations for books
- Inventory tracking
- Only admins can create, update, or delete books
- Public access to book list and details

### Users Service
- Custom User model (email as login)
- JWT Authentication
- User registration and token management

### Borrowings Service
- Create borrowing with inventory validation
- Return book functionality
- Detailed borrowing list with filters
- Automatic inventory update on borrow and return
- Protection against returning the same book twice

**Business Rules**:
- Regular users can only view their own borrowings
- Admins can view all borrowings (with optional `user_id` filter)
- `is_active` filter for currently active borrowings

---

## DB Structure
<img src="/docs/library_schema.svg" alt="Library Database Schema">

## Tech Stack

- **Backend**: Django + Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL
- **Cache / Broker**: Redis + Celery
- **API Documentation**: Swagger (drf-spectacular)
- **Containerization**: Docker + Docker Compose
- **Testing**: Coverage 60%+ on custom code

---

## How to Run

1. Clone the repository
2. Copy the environment variables file:
   ```bash
   cp .env.sample .env
   ```
3. Start the project:
    ```bash
    docker-compose up --build
    ```
4. Create an admin user:
    ```bash
    docker compose exec library python manage.py createsuperuser
    ```
5. If necessary, you can import a JSON file containing test data and use it to test the service:
    ```bash
    docker compose exec library python manage.py loaddata py_library_service_data.json
    ```
6. If you need to run tests:
   ```bash
   docker compose exec library python manage.py test tests
   ```