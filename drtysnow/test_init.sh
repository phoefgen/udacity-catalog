#!/bin/bash

# Generate fake data for testing the drtysnow app.

echo 'Deleting existing database'
rm /vagrant/drtysnow/data/drtysnow.db
echo '...done'

cd /vagrant/drtysnow/db
echo 'Generating new Database.'
python dbsetup.py
echo '...done'

echo 'Generating fake data'
python makefakedata.py
echo '...done'

echo 'installing Database file'
mv drtysnow.db /vagrant/drtysnow/data
echo '...done'

cd /vagrant/drtysnow
rm ~/drtysnow.db
echo 'DB has been reset'
