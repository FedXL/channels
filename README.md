# Channel Management Project

+ This project is a channel management system that allows you to manage multiple databases and hosts. 
+ The system uses SQLite databases and can be configured by modifying the `config.py` file.

## Configuration

+ To configure the system, create the `config.py` file with the following parameters:
- `config_local`: Local database configuration.
- `config_server_1`: Configuration for server 1.
- `config_server_2`: Configuration for server 2.
- `host`: Host for the application.
- `port`: Port for the application.
- `SECRET_KEY`: Key used to generate safe-forms in the Flask app.
- You can use 'sqlite:///local.db', 'sqlite:///server1.db','sqlite:///server2.db' to create test sqllite databases
## Creating Test Databases

+ To create test databases, run `engine_and_models.py`.

## Adding Users

+ To add a user to the `users` table in the `config_local` database, generate a hash from the user's password using the `werkzeug.security.generate_password_hash` method. Then, add the username and hashed password to the `users` table.

## Running the Application

+ To run the application, first run `loop.py`, and then run `app.py`.

**Note:** Make sure that the required libraries and dependencies are installed before running the application.
