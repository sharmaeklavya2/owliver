import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

unicode_dict = {}
with open(os.path.join(BASE_DIR,"data","unicode_chars.txt")) as _unifile:
	for line in _unifile:
		numval, charname = line.split()
		unicode_dict[charname] = numval

