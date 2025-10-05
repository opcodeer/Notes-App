Architecture Documentation
1. Database Schema

The application uses SQLite as the database, managed via SQLAlchemy ORM. There are two main entities: User and Note.

User: Represents a registered user. Each user has a unique ID, a username, and a hashed password. A user can have multiple notes.

Note: Represents a note created by a user. Each note has a unique ID, a title, content, category, pinned status, optional AI-generated summary, timestamp, and a foreign key linking it to its user.

The relationship between User and Note is one-to-many, meaning each user can create multiple notes, but each note belongs to exactly one user.

2. Class and Module Breakdown
Backend (app.py)

This is the main backend module that handles:

Flask app initialization and configuration

Database setup using SQLAlchemy

Routes for user authentication, note CRUD operations, and Swagger documentation

JWT-based authentication to secure API endpoints

AI-based note summarization using the Gemini CLI

CORS handling to allow frontend requests

Classes:

User: Represents users in the system.

Note: Represents individual notes with attributes like title, content, category, pinned status, summary, timestamp, and associated user.

Decorators:

token_required: Ensures certain API endpoints are accessible only with a valid JWT token.

Key Routes and Their Purpose:

/login (POST): Handles user login and returns a JWT token.

/register (POST): Handles user registration.

/notes (GET): Fetches all notes for the logged-in user.

/notes (POST): Creates a new note for the user.

/notes/<id> (PUT): Updates an existing note by ID.

/notes/<id> (DELETE): Deletes a note by ID.

/notes-page (GET): Returns the HTML page for notes management.

/docs (GET): Provides Swagger UI documentation for all API endpoints.

Frontend (HTML + JavaScript)

The frontend is built using vanilla HTML, CSS, and JavaScript. It communicates with the Flask backend via API calls.

JavaScript Responsibilities:

Authentication: login, register, and logout functions manage user sessions.

Notes Management: Functions like createNote, updateNote, deleteNote, and loadNotes handle the note CRUD operations.

Filters: setCategoryFilter and setSearchQuery allow the user to filter notes by category and search query.

DOM Event Handling: Listens to DOM events like button clicks and input changes to trigger the above functions.

The frontend stores the JWT token in localStorage and includes it in the Authorization header for all protected API requests.

3. Technical Documentation

Technology Stack:

Backend: Flask (Python)

Database: SQLite via SQLAlchemy ORM

Frontend: HTML, CSS, JavaScript

Authentication: JWT-based token system

AI Functionality: Gemini CLI for generating note summaries

API Documentation: Swagger UI

Hosting/Deployment: Render.com

Key Functionalities:

Secure login and registration with password hashing.

Full CRUD operations for notes, with categories and pinned status.

Client-side filtering by category and search query.

AI-powered automatic summarization for notes.

Responsive frontend that dynamically loads notes based on user actions.

Data Flow:

Users register or login → backend validates credentials → returns JWT.

JWT is stored in the browser and sent with all subsequent API requests.

CRUD operations are performed on notes → backend updates the database → returns updated note data.

Notes are fetched from the backend → frontend dynamically renders them based on filters or search.