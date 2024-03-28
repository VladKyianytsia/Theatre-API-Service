# Theatre-API-Service


Theatre service API. The idea is to allow visitors of the Theatre to make Reservations online and choose needed seats, without going physically to the Theatre.

## Installing using GitHub
If you are not using docker, install PostgreSQL and create DB. Create .env file ind fill it using .env.sample as an example
```shell
git clone https://github.com/VladKyianytsia/Theatre-API-Service
python -m venv venv
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
## Using Docker
```shell
docker-compose build
docker-compose up
```

## Features

* Managing plays, performances, actors, genres, theatre halls
* Managing reservations with tickets
* JWT authentication
* Different users permissions(anonymous, authenticated, admin)
* Documentation(/api/doc/swagger/)
* Pagination for reservations
* Throttling
* Media files handling
* Email instead of username authentication

## Get access

To create new user go to /api/user/register or use:
* email: admin@admin.com
* password: adminpassword

* Then obtain refresh and access tokens /api/user/token (active for 30 minutes) and pass access token in headers for every request
* To refresh your access token use your refresh token on /api/user/token/refresh