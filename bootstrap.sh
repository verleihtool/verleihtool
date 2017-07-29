#!/usr/bin/env bash

echo "Bootstrapping Django Vagrant machine..."
sudo apt-get update
sudo apt-get install -y vim git make build-essential libssl-dev zlib1g-dev libbz2-dev \
                        libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
                        libncursesw5-dev xz-utils

# Install NodeJS

echo "Installing NodeJS 6.x"
curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install pyenv

echo "Installing pyenv"
curl -LsS https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash

if ! grep -q ".pyenv" /home/vagrant/.bashrc; then
  cat >> /home/vagrant/.bashrc <<- EOF

# Pyenv initialization
export PATH="/home/vagrant/.pyenv/bin:\$PATH"
eval "\$(pyenv init -)"
eval "\$(pyenv virtualenv-init -)"
EOF
fi

export PATH="/home/vagrant/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Install Python 3.6.0 using pyenv

echo "Installing Python 3.6.0"
pyenv install 3.6.0
pyenv global 3.6.0

echo "Python 3.6.0 installed"
which python
which pip

python -V
pip -V

# Link vagrant directory to home

echo "Create symbolic link to the repository"
ln -sfn /vagrant /home/vagrant/verleihtool

# Create helper scripts

echo "Create helper scripts"
cat > /home/vagrant/server.sh <<- EOF
echo "Server listening at http://127.0.0.1:1337/"
python /vagrant/manage.py runserver [::]:8000
EOF

cat > /home/vagrant/test.sh <<- EOF
set -e
cd /vagrant

echo "-- Running linter flake8"
flake8
echo "Linter succeeded"

echo
echo "-- Running tests"
python manage.py test
EOF

chmod u+x /home/vagrant/server.sh /home/vagrant/test.sh
