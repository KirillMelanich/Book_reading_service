## Kyrylo Melanich Test Task for Globaldev
# Book Reading Service
This API allows an authorized user to read books and measure the time of reading sessions
### Main rules:
- Only admin user can create update and delete book instances
- Authorized user can start reading sessions only for himself
- Any user can view only his own profile and reading sessions
- Profile instances are generated automatically
- No one can update or delete Profile instances
- Every user has to pass JWT token authentication
- Every book instance contains statistics for current user and some extra global stats that shows total reading time for all users and total number of reading sessions  for all users
- If new reading session is started previous stops automatically 

## Technologies used
- Django
- Django Rest Framework
- JWT authentication
- Pytest
- Drf-spectacular
- Docker
- Debug Toolbar

## Installation with Docker
1. Clone the repository:
   ```shell
   git clone https://github.com/KirillMelanich/Book_reading_service
   
2. Launch project with docker-compose using terminal commands:
   ```shell
    docker-compose up

3. Create Superuser:
   ```shell
    docker exec -it book_reading_service-app-1 python manage.py createsuperuser   
Don't forget to change 0.0.0.0:8000 port in your browser search line to 127.0.0.1:8000

## Installation without Docker
1. Clone the repository:
   ```shell
   git clone https://github.com/KirillMelanich/Book_reading_service
   
2. If not using docker navigate to the project directory and activate virtual environment:
   ```shell
   cd crypto_staking_platform
   python -m venv venv
   venv\Scripts\activate (on Windows)
   source venv/bin/activate (on macOS)

3. Use `.env_sample` file as a template and create `.env` file with your settings
    . Don't forget to change your database settings for your local database

4. Run app
   ```shell
   python manage.py runserver
5. Create superuser:
   ```shell
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   
6. Enjoy Book Reading Service