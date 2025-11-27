# Social Media API (FastAPI)

A simple **Social Media REST API** built with **FastAPI**, **SQLite (SQLAlchemy)** and **JWT-based authentication**.  
The API supports user registration & login, creating posts with images, and basic profile functionality.  
All APIs are testable with **Postman** and documented using FastAPI’s built-in **Swagger UI**.

---

## 🚀 Features

- User registration & login with **JWT authentication**
- Secure password hashing
- CRUD operations for:
  - Users (sign up, login, profile)
  - Posts / Images (upload, fetch)
- SQLite database (`test.db`) using SQLAlchemy
- Input validation using **Pydantic** schemas
- Interactive API docs via **Swagger UI** and **ReDoc**
- Postman collection for manual testing

---

## 🛠 Tech Stack

- **Language:** Python
- **Framework:** FastAPI
- **Database:** SQLite (`test.db`) via SQLAlchemy
- **Auth:** JWT (JSON Web Tokens)
- **API Testing:** Postman
- **Server:** uvicorn

---

## 📁 Project Structure

```bash
app/
├── __pycache__/
├── app.py       # FastAPI entry point (routes are included/registered here)
├── db.py        # Database engine, session and models
├── images.py    # Image / post related logic & routes
├── schema.py    # Pydantic schemas (request/response models)
├── users.py     # User & auth routes (register, login, profile)
└── test.db      # SQLite database file
