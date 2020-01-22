export $(cat .env.dev | xargs)
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
