# Food Waste Redistribution API

## 📌 Project Overview

This project is a RESTful API built using Flask and MongoDB.

The system connects food providers (e.g., supermarkets, restaurants) with charities to redistribute surplus food and reduce waste.

---

## 🏗 Technology Stack

- Python
- Flask (Web Framework)
- MongoDB (NoSQL Database)
- Flask-JWT-Extended (JSON Web Token Authentication)
- bcrypt (Password Hashing)

---

## 🔐 Authentication System

The system uses JSON Web Tokens (JWT) for secure authentication.

### Endpoints

#### Register
POST /api/auth/register

Registers a new user with role:
- provider
- charity

#### Login
POST /api/auth/login

Returns a JWT access token.

#### Profile
GET /api/auth/profile

Protected route that returns logged-in user information.

---

## 🚀 Phase 5 – Food Listings

### Create Food Listing

POST /api/food/

Security:
- Requires JWT authentication
- Only users with role "provider" can create listings
- Role-Based Access Control (RBAC) enforced

Validation:
- title (required)
- description (required)
- quantity (must be positive integer)
- expiry_date (required)
- location (required)

Response:
201 Created

{
  "message": "Food listing created successfully"
}

---

## 🧱 Architecture

This project uses the Flask Application Factory Pattern.

Routes are modularised using Flask Blueprints:

- /api/auth → Authentication routes
- /api/food → Food listing routes

---

## 🛠 Setup Instructions

1. Clone repository
2. Create virtual environment
3. Install dependencies
4. Run application



Server runs on:
http://127.0.0.1:5000

---

## 📚 Current Features Completed

- User registration with role validation
- Password hashing using bcrypt
- JWT-based authentication
- Protected routes
- Role-Based Access Control
- Food listing creation endpoint
- MongoDB integration

### Get All Food Listings

GET /api/food/

Returns all food listings in the system.

## Authentication System

This project implements manual JWT authentication using PyJWT.
Token generation, signature verification, expiration handling, and role-based access control are implemented without Flask-JWT-Extended.

## Food Lifecycle

available → requested → approved → completed