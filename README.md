# channels
Channel management project.

1. create configuration file as config.py
for example u can use sqlite databases:

config_local = 'sqlite:///local.db'
config_server_1 = 'sqlite:///server1.db'
config_server_2 = 'sqlite:///server2.db'

host = 'localhost'
port = '5000'

SECRER_KEY='...' it is key to generate safe-forms in flask app

2. run engine_and_models.py to create test databases

3. add to congig_local database into table 'users' username and password

to add password u shold generate hash from your password 
i used wekzeug lib. 
from werkzeug.security import generate_password_hash
hash = generate_password_hash(password)

4. run loop.py 
5. run app.py
