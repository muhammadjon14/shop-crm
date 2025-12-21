# Frontend Transformation Guide

I have transformed the frontend to use React and Tailwind CSS as requested.

## Changes Made

1.  **Backend (Django)**:
    *   Added `/api/home/` endpoint in `main/views.py` to serve product and employee data as JSON.
    *   Updated `main/urls.py` to include the API endpoint.

2.  **Frontend (React)**:
    *   Configured **Tailwind CSS** (v4).
    *   Created a modern **Layout** with Navbar and Footer.
    *   Created **Home**, **About**, and **Contact** pages.
    *   **Home** page fetches data from the Django API and displays it using a modern design (Hero section, Cards, Grids).
    *   Configured **Vite** to proxy API requests to Django (`http://127.0.0.1:8000`).

## How to Run

You need to run both the Django backend and the React frontend.

### 1. Start Django Backend

Open a terminal in the root directory (`c:\Users\Oybek\Desktop\Projects - python\django`) and run:

```bash
python manage.py runserver
```

### 2. Start React Frontend

Open a **new** terminal, navigate to the `frontend` directory, install dependencies (if not already done), and start the server:

```bash
cd frontend
npm install
npm run dev
```

### 3. Access the App

Open your browser and go to the URL shown in the React terminal (usually `http://localhost:5173`).

The frontend will proxy requests to the Django backend, so you will see real data from your database.

## Note on "Admin Style" Issue

The new React frontend uses a completely custom design with Tailwind CSS, replacing the old Django templates. This resolves the issue of the site looking like the Django Admin.
