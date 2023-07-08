# fastapi-project-tasks
The api application is developed using a framework [FastApi](https://fastapi.tiangolo.com/) and [SQLAlchemy2.0](https://www.sqlalchemy.org/). 
- The purposes of this application
1. Working with users
	- Authorization and Authentication is implemented with JWT TOKEN
2. Creating individual tasks
	- Creating 
	- Changing
	- Deleting
3. Group of users for common tasks
	- creating a group
	- adding users
	- adding individual tasks
	- adding a debtor for a task
	- editing
	- removal
## launching the application
1. Create .env file
- With docker -> Run:
```sh
docker-compose up --build
```
Application runs on port 8000 
- Local with Python -> Run:
```sh
poetry install # install all packeges and dependencys
poetry run alembic upgrade head # create all table in database
poetry run python main.py # run app
```
Application runs on port 8000
