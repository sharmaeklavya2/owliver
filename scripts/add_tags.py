"""
This module adds all tags in a given file to the database
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

import json
_schema_file_path = os.path.join(BASE_DIR,"schemas.json")
with open(_schema_file_path) as _schema_file:
	schema = json.load(_schema_file)
tag_pattern = schema["tag_list"]["items"]["pattern"]
schema.clear()

import re
from custom_exceptions import CustomException

class InvalidTagName(CustomException):
	tagname = ""
	def __init__(self,tagname):
		self.tagname = tagname
	def __str__(self):
		return self.tagname + " is an invalid tag name"

DEFAULT_PATH = os.path.join(BASE_DIR,"tags.txt")
def import_tags_from_file(filepath=DEFAULT_PATH):
	for line in open(filepath):
		parts = line.split(maxsplit=1)
		if len(parts)>=1:
			name = parts[0]
			desc = ""
			if len(parts)==2:
				desc = parts[1]
			if not re.search(tag_pattern,name):
				raise InvalidTagName(name)
			tag = Tag(name=name,description=desc)
			tag.save()

if __name__=="__main__":
	os.environ.setdefault('DJANGO_SETTINGS_MODULE','owliver.settings')
	print("Setting up Django ...")
	import django
	django.setup()

from main.models import Tag

if __name__=="__main__":
	print("Importing tags ...")
	import_tags_from_file()
