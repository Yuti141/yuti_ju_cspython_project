from web_app import app_flask
from db.core import init_database

init_database()

if __name__ == "__main__":
    app_flask.run()
