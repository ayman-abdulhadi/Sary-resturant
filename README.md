## Sary-resturant

# Installation & Run
  ```
  pip install -r requirements.txt
  python manage.py makemigrations && python manage.py migrate
  python manage.py createsuperuser
  flake8 && python manage.py test && python manage.py runserver
  ```
  
# Info
  - ### **You have to change the new superuser role from django admin panel**
  - You can find postman data in 'Sary Restaurant.postman_collection.json'
  - You can test APIs using the browsable API or using swagger at URL 'http://127.0.0.1:8000/swagger/'
  - You can find SQL queries in 'sql_queries.sql'
  - For filterations please check Postman collections
