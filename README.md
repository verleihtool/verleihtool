# Verleihtool

[![Build Status](https://travis-ci.org/verleihtool/verleihtool.svg?branch=master)](https://travis-ci.org/verleihtool/verleihtool)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/verleihtool/verleihtool/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/verleihtool/verleihtool/?branch=master)
[![GitHub release](https://img.shields.io/github/tag/verleihtool/verleihtool.svg)](https://github.com/verleihtool/verleihtool/releases)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

The **Verleihtool** helps with the administration of public depots and allows
users to send rental requests for items in this depots. It also supports to
assign managers for each depot and group them into several organizations.

This project uses [Semantic Versioning](https://semver.org) and the latest
releases can be found [here](https://github.com/verleihtool/verleihtool/releases).

## Development

### Setting up Vagrant

The development of the Verleihtool happens via [Vagrant](https://www.vagrantup.com/)
and preferably with the [VirtualBox](https://www.virtualbox.org/) provider.
After installing these components, invoking `vagrant up` from the project's
directory will create the virtual machine and run the provisioner on it.
When the process is finished, one can login to the machine using `vagrant ssh`.
In case the provision script gets updated afterwards, the command
`vagrant provision` will update the virtual machine accordingly.

### Starting the tool

To install the dependencies, run `pip install -r requirements.txt` and
`npm install` from the `/vagrant` directory in the virtual machine.
On a Windows host, the parameter `--no-bin-links` is most likely required.
Afterwards, apply all migrations using the command `python manage.py migrate`.

To generate the JavaScript and CSS files, enter `npm run dev` or alternatively
`npm run watch-poll` if the script should automatically detect changes to the
source files. The translation files can be updated from source files with the
command `python manage.py makemessages -l <lang>`. This will update all messages
in the `django.po` files which can be found in the `locale` directory.

Finally, the server can be started using the provided script in
the home directory of the vagrant user called `server.sh`. The tool can
then be reached at [http://127.0.0.1:1337/](http://127.0.0.1:1337/).

To create a superuser, execute the command `python manage.py createsuperuser`
in the `/vagrant` folder and follow the process.

### Running the tests

The Verleihtool comes with a full test suite that can be run using the command
`python manage.py test`. This will not touch the existing database but create a
new test database every time. To run the lint script, execute `flake8` from
the `/vagrant` directory.

Alternatively, when using vagrant a `test.sh` script is provided to automate
the steps described above.

## Deployment

The Verleihtool requires Python 3.6 to be installed on the server as well as a
database backend that is [supported by Django](https://docs.djangoproject.com/en/1.10/ref/databases/).
The web server must be configured to access static files from the `static`
directory of this project. for more information, please consult the
[Django manual for deployments](https://docs.djangoproject.com/en/1.10/howto/deployment/).

Before each deployment, the resource files have to be
generated either on the production server or on another device using the
`npm run production` command. This will place the minified JavaScript and CSS
files in the `static` directory.

To create the optimized translation files, a call to `python manage.py compilemessages`
is required whenever the translations are updated.

## Credits

The Verleihtool was written as a [Projektarbeit](https://mpi.fs.tum.de/fuer-studierende/projektarbeit/)
for the Fachschaft MPI at TU Munich during winter semester 2016/17
by Benedikt Seidl, Florian Stamer, Stefan Su and Leo Tappe.
