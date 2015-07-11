"""
This module aims to load an exam or section or question from a set of files into a python dict
and validate it using the module 'jsonschema' at the same time.
If the jsonschema module is not present, it skips all schema-based validations
It will follow links of the form "file: something.json" and replace them with contents of something.json
It also has a function to test all questions in the folder "test_questions"
"""

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import json
_schemas_file = open(os.path.join(BASE_DIR,"schemas.json"))
schema = json.load(_schemas_file)
_schemas_file.close()
ptr_pattern = schema["pointer"]["pattern"]

import re

JSONSCHEMA_PRESENT = True
try:
	import jsonschema
except ImportError:
	JSONSCHEMA_PRESENT=False
	print("ImportError caught: Module jsonschema is not present - schema-based validation will not take place")

# Test questions ===================================================================================

_FAIL = 0
_FAIL_SCHEMA = 1
_PASS = 2
def validate_and_show(filepath,type_of_schema,print_messages=True):
	# filepath is an absolute path
	# returns _FAIL if document is not a valid JSON file
	# returns _FAIL_SCHEMA if jsonschema is present and document is a valid JSON file but does not match schema
	# returns _PASS otherwise
	schema["$ref"]="#/"+type_of_schema
	relfilepath = os.path.relpath(filepath,BASE_DIR)
	try:
		jsonobj = json.load(open(filepath))
		if JSONSCHEMA_PRESENT:
			try:
				jsonschema.validate(jsonobj,schema)
				if print_messages: 
					print(relfilepath+" is a correct "+type_of_schema+" by schema")
				return _PASS
			except jsonschema.ValidationError:
				# print("ValidationError:", relfilepath, "is an invalid", type_of_schema, "by schema.") would be invalid in python2
				if print_messages:
					print("ValidationError caught: "+relfilepath+" is an invalid "+type_of_schema+" by schema.")
				return _FAIL_SCHEMA
		else:
			if print_messages:
				print(relfilepath+" is a valid JSON document")
			return _PASS
	except ValueError:
		if print_messages:
			print("ValueError caught: "+relfilepath+" is an invalid JSON document.")
		return _FAIL

DEFAULT_TEST_QUESTIONS_DIR = os.path.join(BASE_DIR,"test_questions")
def validate_all_test_questions(root=DEFAULT_TEST_QUESTIONS_DIR):
	"""
	Looks for all JSON files in the directory 'root' and validates them against the question schema.
	It prints the result on stdout. 
	If a file name starts with 'pass' and the file does not pass validation, or
	if a file name starts with 'fail' and the file does not fail validation,
	it displays a '*' next to the file name in the printed results
	"""
	for rootdir, subdir, files in os.walk(root):
		for filename in files:
			if filename.endswith(".json"):
				filepath = os.path.join(rootdir,filename)
				relpath = os.path.relpath(filepath,root)
				result = validate_and_show(filepath,"question",False)
				marker = " *"
				if result==_PASS:
					if filename.startswith("pass"): marker=""
					print("PASS: "+relpath+marker)
				else:
					if filename.startswith("fail"): marker=""
					if result==_FAIL_SCHEMA:
						print("FAILS: "+relpath+marker)
					else:
						print("FAILJ: "+relpath+marker)

# Validate and get exam, section or question =======================================================

def validate_and_get_obj(filepath,type_of_schema):
	"""
	Gets an objects from its JSON file and tests it against the schema with type 'type_of_schema'
	It does not follow links to other files in the JSON object retrieved from filepath
	"""
	# filepath is an absolute path
	schema["$ref"]="#/"+type_of_schema
	jsonobj = json.load(open(filepath))
	if JSONSCHEMA_PRESENT:
		jsonschema.validate(jsonobj,schema)
	return jsonobj

def validate_and_get_question(filepath):
	""" same as validate_and_get_obj(filepath,"question") """
	return validate_and_get_obj(filepath,"question")

def _replace_object_pointers_by_contents(obj_list,directory,object_validator_and_getter):
	for i in range(len(obj_list)):
		obj = obj_list[i]
		if type(obj)==str:
			filename = re.search(ptr_pattern,obj).group(1)
			obj_list[i] = object_validator_and_getter(os.path.join(directory,filename))

def validate_and_get_section(abspath_to_section):
	""" 
	validates a section JSON file and follows links in it to questions
	Returns the completely build section as a dict
	An exception is raised if the section or questions referred in it are invalid
	"""
	section_dir = os.path.dirname(abspath_to_section)
	section = validate_and_get_obj(abspath_to_section,"section")
	_replace_object_pointers_by_contents(section["questions"],section_dir,validate_and_get_question)
	return section

def validate_and_get_exam(abspath_to_exam):
	"""
	Validates a exam JSON file and follows links in it to sections and questions
	Returns the completely build exam as a dict
	An exception is raised if the exam or the sections or questions referred in it are invalid
	"""
	exam_dir = os.path.dirname(abspath_to_exam)
	exam = validate_and_get_obj(abspath_to_exam,"exam")
	section_list = exam["sections"]
	_replace_object_pointers_by_contents(section_list,exam_dir,validate_and_get_section)
	for section in section_list:
		_replace_object_pointers_by_contents(section["questions"],exam_dir,validate_and_get_question)
	return exam

def main(argv):
	"""
	Tests all questions in the directory test_questions if there is no command line argument
	Otherwise validates and displays an exam object given in the first command line argument
	"""
	if len(argv)==1:
		print("Testing test_questions:")
		validate_all_test_questions()
	else:
		from pprint import pprint
		abspath_to_exam = os.path.abspath(argv[1])
		exam = validate_and_get_exam(abspath_to_exam)
		pprint(exam)
	return 0

if __name__=="__main__":
	import sys
	main(sys.argv)
