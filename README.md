# Owliver
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sharmaeklavya2/owliver?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

Owliver is an educational site to make and take tests.

### Created by
Eklavya Sharma

Using Python 3.4 and Django 1.8

## How to run it

Owliver is written in python 3.4 and is not compatible with python 2

You might need to replace `python` and `pip` in the following commands by something else if `python` and `pip` don't point to a python 3 executable and a package manager for it respectively.  
If you're on a Debian-based system (like Ubuntu), use `python3` instead of `python` and `pip3` instead of `pip`.

You should have these python 3 packages installed:

* Django 1.8 (`pip install django`)
* jsonschema (this package is optional, but it is recommended) (`pip install jsonschema`)

Now you must follow these steps to set up the project for use:

* Open a terminal in the project's root directory
* `python manage.py makemigrations main`
* `python manage.py migrate`

Now you should add exams to the database because user-uploadable exams are not yet supported.

* `python scripts/add_exam.py exams/*.json`

Now test using django's development server

* `python manage.py runserver`

## Documentation

Documentation for this site is in the doc folder in markdown. To generate HTML documentation, run `make docs` in the project's root directory. If you wish to contribute, make sure to read everything in doc.

## Unresolvable Issues
There is a bug in `jsonschema` because of which it does not load nested `$ref`s to external files ([see issue on github](https://github.com/Julian/jsonschema/issues/209)). Because of this bug, I had to make a single schema file.
