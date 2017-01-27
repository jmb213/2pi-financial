[![Stories in Ready](https://badge.waffle.io/JPZ13/2pi-financial.png?label=ready&title=Ready)](https://waffle.io/JPZ13/2pi-financial)
# 2pi-financial

# Getting set up

## Heroku

heroku login
# heroku create
git push heroku master

## Set up on the server:

heroku config:set FLASKENV=prod
Server host, port?
configure the database
add database resource to the application

## Set up for development

git clone
virtualenv venv
source venv/bin/Activate
pip install -r requirements
export FLASKENV=development
create Postgres database
python runserver.py

Creating the Postgres database:
sudo apt-get install postgres-9.3
sudo apt-get install pgadmin3
su - postgres
psql
CREATE DATABASE development;
\l
exit
sudo gedit /etc/postgresql/9.3/main/postgresql.conf
--change the port to 1111

(make sure database is setup to the correct port and environment variable is development)
(double check the config.py file)

# Contents

## Parent Directory

 - config: basic configuration for the dev and prod environments (not included in repository)
 - runserver: file that launches the instance of the application

## Application

 - init.py: configuration, logging, set up web assets, load the database; run when the application is launched
 - views.py: different pages on the website; demo accounts; data access functions (needs to be broken up)
 - models.py: database models definitions and functionality
 - forms.py: login form, can be reworked

## Static

CSS, Images, Javascript

## Templates

HTML templates