pip3 install flask_sqlalchemy
pip3 install flask_cors
pip3 install flask --upgrade
pip3 uninstall flask-socketio -y
service postgresql start
psql -d postgres -U mucahit psql < backend/setup.sql
psql bookshelf < backend/books.psql