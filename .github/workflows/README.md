# Simple Asset Management System

A Flask-based web application for managing organizational assets.

## Features

- **Request Asset**: Users can request available assets by providing purpose and duration.
- **Return Asset**: Users can return assigned assets.
- **View Assets**: Users can view all assets with their availability status and allocation details.
- **Admin Panel**: Administrators can add new assets and view all requests.

## Installation

1. Install Python (if not already installed).
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python app.py`

## Usage

- Login with username 'user1' password 'pass1' or 'admin' password 'password'.
- From the dashboard, request, return, or view assets.
- Admin can access admin panel to manage assets.

## Project Structure

- `app.py`: Main Flask application
- `templates/`: HTML templates
- `static/`: CSS styles
- `requirements.txt`: Python dependencies