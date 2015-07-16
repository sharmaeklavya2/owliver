import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import json
with open(os.path.join(BASE_DIR,"schemas.json")) as _schemas_file:
	schemas = json.load(_schemas_file)
ptr_pattern = schemas["pointer"]["pattern"]
