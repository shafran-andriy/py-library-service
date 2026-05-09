# Library Service

**Modern Book Borrowing Management System**

---

## Project Description

In this city library, users can borrow books and pay upon return depending on the number of days taken. 

The old system was completely manual (paper-based), with no real-time inventory tracking, no digital user management, and cash-only payments. Administrators had no clear visibility into who returned books on time and who didn’t.

This project implements a **web-based library management system** that solves all these issues. The system provides efficient management of books, users, and borrowings through a clean and well-documented REST API.

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
    docker-compose exec library python manage.py createsuperuser
    ```
5. If necessary, you can import a JSON file containing test data and use it to test the service:
    ```bash
    docker compose exec library python manage.py loaddata py_library_service_data.json
    ```