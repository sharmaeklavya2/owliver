# Scripts
There are several scripts in the [scripts folder](../scripts).

### `add_exam.py`

`python add_exam.py path_to_json_file_1.json path_to_json_file_2.json ...`

This script interprets all json files as `Exam`s and adds them to database.

This script uses the jsonschema module. It can run without that module as well, but if the json file does not conform to the schema you'll have problems later.

### `add_anssheet.py`

`python add_anssheet.py exam_name username`

This script adds an `ExamAnswerSheet` object to the database. The `ExamAnswerSheet` is bound to an `Exam` with name _exam___name_ and `User` with username _username_.

### `add_tags.py`

`python add_tags.py [tagfile]`

This script adds all tags in _tagfile_ to database. If _tagfile_ is not specified, a default file is used (currently data/tags.txt)

### `clear_from_db.py`

`python clear_from_db.py [tags] [exams] [eas|examanswersheet]`

If _tags_ is given as an argument, all `Tag`s are cleared from database.  
If _exams_ is given as an argument, all `Exam`s are cleared from database.  
If _eas_ or _examanswersheet_ is given as an argument, all `ExamAnswerSheet`s are cleared from database.

This script cannot be imported as a module.

### `validation.py`

`python validation.py [exam_path]`

Tests all questions in the directory 'test_questions' if there are no command line arguments
Otherwise validates and displays the exam json file given in the first command line argument
This script uses the jsonschema module.
