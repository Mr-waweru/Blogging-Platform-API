# Blogging API

A Django Rest Framework (DRF)-based API that allows users to manage blog posts. Users can create, update, delete, and view blog posts, filter posts by category, tag or author, and manage comments. The API also includes JWT-based authentication for secure access.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)

---

## Overview

The Blogging API is designed to provide a platform for managing blog posts and comments. Users can:
- Perform CRUD operations on blog posts.
- Retrieve posts by category or author.
- Add and view comments on blog posts.
- Authenticate using JWT for secure access.

**Technologies used:**
- **Backend Framework**: Django Rest Framework (DRF)
- **Authentication**: JWT (JSON Web Token)

---

## Features

- Create, retrieve, update, and delete blog posts.
- Filter blog posts by category and author.
- Add and view comments on posts.
- Secure API access using JWT authentication.

---

## Installation

Follow these steps to set up the project locally:

```bash
# Clone the repository
git clone https://github.com/Mr-waweru/Blogging-Platform-API.git

# Navigate to the project directory
cd blogging-api

# Set up a virtual environment
python -m venv venv

# Activate the virtual environment
source env/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Start the server
python manage.py runserver
