#!/usr/bin/env bash

echo "Bootstrapping Django Vagrant machine..."
sudo apt-get update
sudo apt-get install -y vim git make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils

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

echo "Installing Django"
pip install Django

python -m django --version

# Create simple start script
cat > /home/vagrant/startServer.sh <<- EOF
python /vagrant/manage.py runserver [::]:8000
EOF

chmod u+x /home/vagrant/startServer.sh
