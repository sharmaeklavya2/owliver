# Owliver

Owliver is an educational site to make and take tests.

### Created by
Eklavya Sharma

Using Python 3.4 and Django 1.8

## How to run it
You must have these python packages installed:

* Django 1.8 (`pip install django`)
* jsonschema (this package is optional, but it is recommended) (`pip install jsonschema`)
* Pillow (you might need it in the future if I add support for user-uploadable images) (`pip install pillow`)

Now you must follow these steps:

1. Open a terminal in the project's directory
2. `python manage.py makemigrations main`
3. `python manage.py migrate`
4. `python manage.py runserver`

If your default `python` points to a python 2.x installation, or you are using a virtualenv, you might need to replace `python` in the above commands by whatever python 3 installation you are using.
On most Debian-based systems, `python3` points to the default python 3 installation.

## Unresolvable Issues
There is a bug in `jsonschema` because of which it does not load nested `$ref`s to external files (https://github.com/Julian/jsonschema/issues/209). Because of this bug, I had to make a single schema file.
