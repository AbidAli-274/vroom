# Vroom Inventory Backend (vroom-be)

A Django-based backend for managing a vehicle (bike) rental inventory system, including user authentication, inventory management, rental logs, and addons. The project is containerized with Docker and styled with Tailwind CSS for the frontend templates.

---

## Features
- **User Authentication**: Signup, login, logout, JWT-based auth (djangorestframework-simplejwt)
- **Inventory Management**: CRUD for bikes, rental logs, and addons
- **Admin Panel**: Django admin for superusers
- **API Documentation**: Swagger UI at `/swagger/`
- **Cloudinary Integration**: For image uploads and storage
- **Tailwind CSS**: For modern, responsive UI in Django templates
- **PostgreSQL**: As the main database (via Docker)
- **Seeding**: Custom management command to seed bike inventory from CSV

---

## Project Structure
```
vroom-be/
├── account/         # User/member models, views, serializers, auth
├── inventory/       # Bike inventory, rental logs, addons, seeding
├── djangoapp/       # Project settings, URLs, WSGI/ASGI, exception handler
├── templates/       # Django HTML templates (base, navbar, sidebar, etc.)
├── static/          # Static files (Tailwind CSS, images, etc.)
├── certificates/    # SSL certificates for local HTTPS (if any)
├── manage.py        # Django entry point
├── Dockerfile       # Docker build instructions
├── docker-compose.yml # Multi-service orchestration
├── pyproject.toml   # Poetry dependencies
├── poetry.lock      # Poetry lock file
├── package.json     # Tailwind CSS config
├── tailwind.config.js # Tailwind CSS config
├── .env             # Environment variables (not committed)
```

---

## Quick Start

### 1. Clone the Repository
```bash
git clone <repo-url>
cd vroom-be
```

### 2. Environment Variables
Create a `.env` file in `vroom-be/` with the following (replace with your Cloudinary credentials):
```
CLOUD_API_KEY=your_cloudinary_api_key
CLOUD_API_SECRET=your_cloudinary_api_secret
CLOUD_NAME=your_cloudinary_cloud_name
```

### 3. Docker Setup (Recommended)
Ensure you have Docker and Docker Compose installed.

```bash
docker-compose up --build
```
- The backend will be available at [http://localhost:8000](http://localhost:8000)
- PostgreSQL runs in a separate container

### 4. Manual Setup (Without Docker)
- Install Python 3.11+
- Install [Poetry](https://python-poetry.org/docs/#installation)
- Install Node.js (for Tailwind CSS)

```bash
poetry install
npm install
# To build Tailwind CSS
npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch
# Set up the database (PostgreSQL)
createdb vroom_db
# Apply migrations
poetry run python manage.py migrate
# Create a superuser
poetry run python manage.py createsuperuser
# Run the server
poetry run python manage.py runserver
```

---

## Seeding the Inventory
To seed the bike inventory from CSV (uses Cloudinary for images):
```bash
poetry run python manage.py seed_bike_inventory
```

---

## Main Dependencies
- Django 5.1+
- djangorestframework
- drf-yasg (Swagger docs)
- djangorestframework-simplejwt (JWT auth)
- cloudinary, django-cloudinary-storage
- django-compressor
- gunicorn (for production)
- psycopg2-binary (PostgreSQL)
- django-heroku (Heroku deployment support)
- Tailwind CSS (via npm)

---

## API Overview
- **Swagger UI**: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
- **Admin Panel**: [http://localhost:8000/admin/](http://localhost:8000/admin/)

### Main Endpoints
- `/account/signup/` - User registration
- `/account/login/` - User login
- `/account/logout/` - User logout
- `/account/member/` - CRUD for members
- `/account/document/` - Manage member documents
- `/inventory/bike/` - CRUD for bikes
- `/inventory/rental-log/` - CRUD for rental logs
- `/inventory/addon/` - CRUD for addons

---

## Development Notes
- **Static & Media**: Static files are served from `/static/`. Images are uploaded to Cloudinary.
- **Tailwind CSS**: Edit `static/src/input.css` and run the Tailwind build command to update styles.
- **Custom Management Commands**: See `inventory/management/commands/seed_bike_inventory.py` for seeding logic.
- **Testing**: Add tests in `account/tests.py` and `inventory/tests.py`.
- **Deployment**: Use the provided `Dockerfile` and `Procfile` for Heroku or similar platforms.

---

## License
BSD License (see project for details)

---

## Contact
For questions, contact: [Your Name](mailto:you@example.com)
