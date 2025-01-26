# TodoApp - Simple TodoList Management with FastAPI

This is a simple TodoList management project developed while learning FastAPI. Through this project, you can learn how to build a simple web application using FastAPI and implement basic CRUD operations.

## Tech Stack

- Frontend: Uses Jinja2 template engine to render HTML pages.
- Backend: Built with FastAPI framework to provide API support and handle business logic.

## How to Run the Project Locally

You can follow these steps to run the project locally on your computer.

### 1. Clone the Project

First, clone the project to your local machine:

```bash
git clone https://github.com/Foolish-Wang/TodoApp.git
```

### 2. Navigate to the Project Directory

After cloning, navigate to the project directory:

```bash
cd TodoApp
```

### 3. Create a Development Environment

You can use `conda` or `venv` to create an isolated Python development environment.

#### Using Conda

```bash
conda create -n todoapp_env python=3.11
conda activate todoapp_env
```

#### Using Venv

```bash
python -m venv todoapp_env
source todoapp_env/bin/activate  # On Windows, use `todoapp_env\Scripts\activate`
```

### 4. Install Dependencies

After activating the development environment, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 5. Create the `.env` File

Create a `.env` file in the project root directory and set the `SQLAlchemy` database connection URL. For example:

```env
SQLALCHEMY_DATABASE_URL=sqlite:///./todos.db
```

### 6. Modify the `database.py` File

In the `database.py` file, modify the `SQLALCHEMY_DATABASE_URL` variable to ensure it matches the configuration in the `.env` file.

```python
# database.py
import os
SQLALCHEMY_DATABASE_URL = os.getenv("YOUR_URL")
```

### 7. Start the Project

Use `uvicorn` to start the project:

```bash
uvicorn main:app --reload
```

Once started, you can visit `http://127.0.0.1:8000` in your browser to see the project running.

# Appendix: Development and Deployment Notes

## Docker's PostgreSQL Image

During local development, I used Docker's PostgreSQL image to run the database. If you use a different database, some code adjustments may be required.

---

## Deployment

I deployed the project to [Render](https://render.com/), a cloud platform that supports various applications and databases.

---

## Database Hosting

For deployment, I used [Aiven](https://aiven.io/) to host the PostgreSQL database.
