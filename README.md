A simple Version Control System implemented using Flask Web Framework.

Software requirements:
1) Python 3.6 or above
2) flask and pymysql libraries
3) MySQL Database

Import vsq.sql as:

$> mysql -u YOUR_USERNAME -p -D DATABASE_NAME < PATH_TO_PROJECT/vcs.sql

Install Python libraries using pip:

$> pip install pymysql flask

Update following variables in server_init.py:

DBHOST="HOST_ADDRESS"
DBUSER="DB_USERNAME"
DBPASS="DB_PASSWORD"
DBNAME="DB_NAME"

Run the server:
$> python server.py
