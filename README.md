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
- Debug Toolbar

## Installation 
1. Clone the repository:
   ```shell
   git clone https://github.com/KirillMelanich/Book_reading_service
   
2. Navigate to the project directory and activate virtual environment:
   ```shell
   cd book_reading_service
   python -m venv venv
   venv\Scripts\activate (on Windows)
   source venv/bin/activate (on macOS)

3. Use `.env_sample` file as a template and create `.env` file with your settings
    . Don't forget to change your database settings for your local database

4. Run migrations
   ```shell
   python manage.py makemigrations
   python manage.py migrate

5. Create superuser
   ```shell
   python manage.py createsuperuser
 
6. Run server:
   ```shell
   python manage.py runserver
   
7. Enjoy Book Reading Service