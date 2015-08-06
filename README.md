# Owliver
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sharmaeklavya2/owliver?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

Owliver is an educational site to make and take tests. Sort of like BITSAT and JEE Main online.

### Created by
Eklavya Sharma

Using Python 3.4 and Django 1.8

## Features

* Many types of questions (mcq, text, integer, True/False and more)
* Questions can be split across many sections
* Shuffle questions, sections and question options in mcqs
* User's data is not lost when browser window closes
* Control marking scheme independently for each section
* Set time limit if needed and control when users can start exam
* Detailed report shown after (and sometimes during) exam
* Bonus sections which unlock only after attempting a minimum number of questions or scoring min required marks
* Ability to add hint and extra bonus for not viewing hint
* Control when user can see answer and solution (after attempting that question or after finishing whole exam)
* Export exams as JSON

## How to run it

Owliver is written in python 3.4 and is not compatible with python 2.

You should have these python 3 packages installed:

* Django 1.8 (`pip install django`)
* jsonschema (this package is optional, but it is recommended) (`pip install jsonschema`)

Now you must follow these steps to set up the project for use:

* Open a terminal in the project's root directory
* `python manage.py migrate`

Now you should add exams to the database because user-uploadable exams are not yet supported.

* `python scripts/add_exam.py exams/*.json`

Now test using django's development server

* `python manage.py runserver`

## Using libraries locally

By default, The website will load JQuery, Bootstrap and MathJax from the internet when required. If you want it to use a local copy instead, you'll have to make a folder named 'extstatic' in the project's directory and place files in it (symlinks work as well).

* JQuery will be loaded from 'extstatic/jquery.min.js'
* Bootstrap's folder should be 'extstatic/bootstrap'
* MathJax's folder should be 'extstatic/mathjax'

## Documentation

Documentation for this site is in the doc folder in markdown. To generate HTML documentation, run `make docs` in the project's root directory. If you wish to contribute, make sure to read everything in doc.

## Unresolvable Issues
There is a bug in `jsonschema` because of which it does not load nested `$ref`s to external files ([see issue on github](https://github.com/Julian/jsonschema/issues/209)). Because of this bug, I had to make a single schema file.
