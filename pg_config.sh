# install system packages:
apt-get -qqy update
apt-get -qqy install python-flask python-sqlalchemy
apt-get -qqy install python-pip

# Install custom modules:
pip install oauth2client
pip install requests
pip install httplib2
pip install flask-httpauth
pip install oauth2client
pip install Flask-WTF

# This line deletes all the data, and sets up a new Db with test lorem ipsum.
bash /vagrant/drtysnow/test_init.sh

vagrantTip="[35m[1mThe shared directory is located at /vagrant\nTo access your shared files: cd /vagrant(B[m"
echo -e $vagrantTip > /etc/motd
