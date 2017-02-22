# Item-Catalog
# udacity-catalog #

## Preparations ##

This app uses 

- [Flask](http://flask.pocoo.org)
- [SQLAlchemy](http://www.sqlalchemy.org)

These dependencies must be installed before you can run the app. The easiest way to do so is by using [pip](https://pypi.python.org/pypi/pip). Simply run the following commands:

pip install Flask
pip install SQLAlchemy

Next you have to create the categories. To do so run

python database_setup.py

## Run the app ##

To start the app simply run
Install Vagrant.

Once Vagrant is installed, cd to vagrant/ and run vagrant up && vagrant ssh. In the virtual machine, cd to
/vagrant/pokemon and run python project.py. The item catalog can then be accessed at localhost:8080.

python project.py

## Remarks ##
- The app offers two JSON endpoints:
- User JSON: /trainers/JSON
- User-Pokemon JSON: /trainers/\<int:user_id\>/pokemon/JSON
