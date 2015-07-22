"""
This module adds all tags in a given file to the database
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
if BASE_DIR not in sys.path:
	sys.path.append(BASE_DIR)

from scripts import read_schemas
tag_pattern = read_schemas.schemas["tag_list"]["items"]["pattern"]

import re
from custom_exceptions import CustomException

class InvalidTagName(CustomException):
	tagname = ""
	def __init__(self,tagname):
		self.tagname = tagname
	def __str__(self):
		return self.tagname + " is an invalid tag name"

DEFAULT_PATH = os.path.join(BASE_DIR,"data","tags.txt")
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
