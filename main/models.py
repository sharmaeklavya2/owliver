from django.db import models
from django.contrib.auth.models import User

from datetime import timedelta, datetime
from django.utils import timezone
import re

QUESTION_TYPE_DICT = {
	"mcq": "Single-correct MCQ",
	"text": "Text based subjective",
#	"int": "Integer",
#	"float": "Real number"
#	"bool": "True or False",
#	"match": "Match the following",
#	"mmatch": "Matrix match",
#	"order": "Arrange in order",
#	"enlist": "List out" # can be in order or without order
}

# Extra question types:
# mmcq is mcq with multicorrect=True
# regex is text with use_regex=True

QUESTION_TYPE = list(QUESTION_TYPE_DICT.items())
UNKNOWN_TAG_ACTION = "create"
# UNKNOWN_TAG_ACTION decides what add_tag does when it encounters a tag not already saved in database
# "create" means create the new tag
# "error" means raise an exception (or let one get raised by django)
# "ignore" means don't add that tag to db and continue

# Exceptions =======================================================================================

from custom_exceptions import CustomException, QuestionTypeNotImplemented

class McqOptionDoesNotMatchQuestion(CustomException):
	def __str__(self):
		return "Some options do not match the mcq question"
class AnswerHasInvalidSection(CustomException):
	def __str__(self):
		return "this answer's question belongs to a section which is not the same as it's section_answer_sheet's section"
class SectionAnswerSheetHasInvalidExam(CustomException):
	def __str__(self):
		return "this section_answer_sheet's section belongs to an exam which is not the same as it's exam_answer_sheet's exam"

# Main Models ======================================================================================

class Tag(models.Model):
	name = models.CharField(max_length=30,blank=False,unique=True)
	description = models.TextField(blank=True)

	def __str__(self):
		return self.name

def add_tag(obj,tagname):
	try:
		tag = Tag.objects.get(name=tagname)
		obj.tags.add(tag)
	except Tag.DoesNotExist:
		if UNKNOWN_TAG_ACTION=="create":
			tag = Tag(name=tagname)
			tag.save()
			obj.tags.add(tag)
		elif UNKNOWN_TAG_ACTION=="error":
			raise

class Exam(models.Model):
	name = models.CharField(max_length=50,blank=False)
	info = models.TextField(blank=True)
	time_limit = models.DurationField("Time limit to complete exam",default=timedelta(0))
		# timedelta(0) means infinite time
	shuffle_sections = models.BooleanField("Randomly shuffle sections",default=False)
	author = models.TextField(blank=True)
	comment = models.TextField(blank=True)
	postinfo = models.TextField(blank=True)
	owner = models.ForeignKey(User,null=True)
	tags = models.ManyToManyField(Tag)

	def __str__(self):
		return self.name
	def add_tag(self,tagname):
		return add_tag(self,tagname)
	def export(self):
		exam_dict = {"name":self.name}
		if self.info: exam_dict["info"] = self.info
		if self.comment: exam_dict["comment"] = self.comment
		if self.time_limit!=timedelta(0): exam_dict["time_limit"] = self.time_limit.total_seconds()
		if self.shuffle_sections: exam_dict["shuffle_sections"] = self.shuffle_sections
		tags_list = [tag.name for tag in self.tags.order_by('id')]
		if tags_list: exam_dict["tags"] = tags_list
		sections_list = [section.export() for section in self.section_set.order_by('id')]
		if sections_list: exam_dict["sections"] = sections_list
		return exam_dict

class Section(models.Model):
	name = models.CharField(max_length=50,blank=False)
	info = models.TextField(blank=True)
	exam = models.ForeignKey(Exam)
#	sno = models.PositiveIntegerField(default=0)
	comment = models.TextField(blank=True)
	postinfo = models.TextField(blank=True)
	tags = models.ManyToManyField(Tag)

	def __str__(self):
		return self.exam.name+" : "+self.name
	def add_tag(self,tagname):
		return add_tag(self,tagname)

	# marking_scheme
	correct_marks = models.IntegerField("Marks for correct answer",default=1)
	wrong_marks = models.IntegerField("Marks for wrong answer",default=0)
	na_marks = models.IntegerField("Marks for not attempting question",default=0)
	hint_deduction = models.IntegerField("Marks deducted for viewing hint",default=0)
	def export_marking_scheme(self):
		ms_dict = {}
		if self.correct_marks!=1: ms_dict["correct"] = self.correct_marks
		if self.wrong_marks!=0: ms_dict["wrong"] = self.wrong_marks
		if self.na_marks!=0: ms_dict["na"] = self.na_marks
		if self.hint_deduction!=0: ms_dict["hint_deduction"] = self.hint_deduction
		return ms_dict

	# unlock
	unlock_marks = models.IntegerField("Minimum marks to attempt this section",default=0)
	unlock_questions = models.PositiveIntegerField("Minimum attempted questions to attempt this section",default=0)
	unlock_both_needed = models.BooleanField("Should both minimum question and minimum marks requirements be fulfilled?",default=False)
	def is_unlocked(self,marks,questions):
		has_marks = self.unlock_marks<=marks
		has_questions = self.unlock_questions<=questions
		if self.unlock_both_needed:
			return (has_marks and has_questions)
		else:
			return (has_marks or has_questions)
	def export_unlock(self):
		unlock_dict = {}
		if self.unlock_marks!=0: unlock_dict["marks"]=self.unlock_marks
		if self.unlock_questions!=0: unlock_dict["questions"]=self.unlock_questions
		if self.unlock_both_needed!=False: unlock_dict["both_needed"]=self.unlock_both_needed
		return unlock_dict

	# shuffle
	shuffle_options = models.BooleanField("Randomly shuffle options of questions",default=False)
	shuffle_questions = models.BooleanField("Randomly shuffle questions",default=False)
	def export_shuffle(self):
		shuffle_dict = {}
		if self.shuffle_questions: shuffle_dict["questions"] = self.shuffle_questions
		if self.shuffle_options: shuffle_dict["options"] = self.shuffle_options
		return shuffle_dict

	# other restrictions
	allowed_attempts = models.IntegerField("Number of attempts allowed per question",default=0)
		# if allowed_attempts is 0, student will have infinite attempts but attempt status will not be shown
		# if allowed_attempts is negative, student will have infinite attempts and attempt status will be shown after every submit
		# if allowed_attempts is a positive integer n, student will have n attempts and attempt status will be shown after every submit
	show_correct_answer = models.BooleanField("Should correct answer be shown after attempting a question?",default=False)
		# if show_correct_answer is True and allowed_attempts is not 0,
		# student will be shown correct answer after exhausting all attempts
	max_questions_to_attempt = models.PositiveIntegerField("Maximum number of questions a student is allowed to attempt",default=0)
		# if this value is 0, all questions can be attempted

	def export(self):
		sec_dict = {"name":self.name}
		if self.info: sec_dict["info"] = self.info
		if self.comment: sec_dict["comment"] = self.comment
		if self.allowed_attempts!=0: sec_dict["allowed_attempts"] = self.allowed_attempts
		if self.show_correct_answer!=False: sec_dict["show_correct_answer"] = self.show_correct_answer
		if self.max_questions_to_attempt!=0: sec_dict["max_questions_to_attempt"] = self.max_questions_to_attempt
		tags_list = [tag.name for tag in self.tags.order_by('id')]
		if tags_list: sec_dict["tags"] = tags_list
		ms_dict = self.export_marking_scheme()
		if ms_dict: sec_dict["marking_scheme"] = ms_dict
		unlock_dict = self.export_unlock()
		if unlock_dict: sec_dict["unlock"] = unlock_dict
		shuffle_dict = self.export_shuffle()
		if shuffle_dict: sec_dict["shuffle"] = shuffle_dict
		questions_list = [question.export() for question in self.question_set.order_by('id')]
		if questions_list: sec_dict["questions"] = questions_list
		return sec_dict

class Question(models.Model):
	title = models.CharField(max_length=120,blank=True)
	text = models.TextField(blank=True)
	hint = models.TextField(blank=True)
	solution = models.TextField(blank=True)
#	qtype = models.CharField("Question Type",max_length=8,choices=QUESTION_TYPE)

	def __str__(self):
		if self.title: return self.title
		elif len(self.text)<=50: return self.text
		else: return "Untitled"

	def get_qtype(self):
		for qtype in QUESTION_TYPE_DICT:
			if hasattr(self,qtype+"question"):
				return qtype
		return ""

	class TypelessQuestion(CustomException):
		def __str__(self):
			return "This question has no type associated with it"

	def get_child_question(self):
		for qtype in QUESTION_TYPE_DICT:
			try:
				return getattr(self,qtype+"question")
			except AttributeError:
				pass
		raise Question.TypelessQuestion()

	section = models.ForeignKey(Section)
#	sno = models.PositiveIntegerField(default=0)
	comment = models.TextField(blank=True)
	metadata = models.TextField(blank=True)
	tags = models.ManyToManyField(Tag)

	def add_tag(self,tagname):
		return add_tag(self,tagname)
	def export(self):
		ques_dict = self.get_child_question().export()
		if self.title: ques_dict["title"] = self.title
		if self.text: ques_dict["text"] = self.text
		if self.hint: ques_dict["hint"] = self.hint
		if self.comment: ques_dict["comment"] = self.comment
		tags_list = [tag.name for tag in self.tags.order_by('id')]
		if tags_list: ques_dict["tags"] = tags_list
		return ques_dict

class ExamAnswerSheet(models.Model):
	exam = models.ForeignKey(Exam)
	user = models.ForeignKey(User)
	start_time = models.DateTimeField(null=True)
	end_time = models.DateTimeField(null=True)

	def __str__(self):
		return str(self.user)+" : "+str(self.exam)

	TIMER_ERROR = 0			# error
	TIMER_NOT_SET = 1		# timer not set (start_time is None)
	TIMER_NOT_STARTED = 2	# timer set but exam not started (start_time is in the future)
	TIMER_IN_USE = 3		# exam in progress
	TIMER_ENDED = 4			# exam ended
	DURATIONLESS_TIMER_STATII = (TIMER_ERROR, TIMER_NOT_SET, TIMER_NOT_STARTED)

	def set_timer(self,start_time=None):
		if start_time==None:
			start_time = timezone.now()
		self.start_time = start_time
		time_limit = self.exam.time_limit
		if time_limit==timedelta(0):
			self.end_time = None
		else:
			self.end_time = self.start_time + time_limit
		self.save()

	def get_timer_status(self):
		if self.start_time==None:
			if self.end_time==None:	return ExamAnswerSheet.TIMER_NOT_SET
			else: return ExamAnswerSheet.TIMER_ERROR
		now = timezone.now()
		if self.end_time==None:
			if now < self.start_time:
				return ExamAnswerSheet.TIMER_NOT_STARTED
			else:
				return ExamAnswerSheet.TIMER_IN_USE
		if self.end_time < self.start_time:
			return ExamAnswerSheet.TIMER_ERROR
		if now < self.start_time:
			return ExamAnswerSheet.TIMER_NOT_STARTED
		elif now < self.end_time:
			return ExamAnswerSheet.TIMER_IN_USE
		else:
			return ExamAnswerSheet.TIMER_ENDED

	def get_attempt_duration(self):
		"""
		max duration of time which a student has given to this exam
		TIMER_ERROR, TIMER_NOT_SET, TIMER_NOT_STARTED : return None
		TIMER_IN_USE : return timezone.now() - self.start_time
		TIMER_ENDED	: return self.end_time - self.start_time
		"""
		timer_status = self.get_timer_status()
		if timer_status in ExamAnswerSheet.DURATIONLESS_TIMER_STATII:
			return None
		if timer_status == ExamAnswerSheet.TIMER_IN_USE:
			return timezone.now() - self.start_time
		else:
			return self.end_time - self.start_time

class SectionAnswerSheet(models.Model):
	# Answer Objects FK to this model
	section = models.ForeignKey(Section)
	exam_answer_sheet = models.ForeignKey(ExamAnswerSheet)
	def __str__(self):
		return str(self.section)
	def save(self,*args,**kwargs):
		if self.section.exam != self.exam_answer_sheet.exam:
			raise SectionAnswerSheetHasInvalidExam()
#		super().save(*args,**kwargs)
		super(SectionAnswerSheet,self).save(*args,**kwargs)

class Answer(models.Model):
	section_answer_sheet = models.ForeignKey(SectionAnswerSheet)
#	question = models.ForeignKey(Question)
	viewed_hint = models.BooleanField(default=False)

	def get_qtype(self):
		for qtype in QUESTION_TYPE_DICT:
			if hasattr(self,qtype+"answer"):
				return qtype
		return ""

	class TypelessAnswer(CustomException):
		def __str__(self):
			return "This answer has no type associated with it"

	def get_child_answer(self):
		for qtype in QUESTION_TYPE_DICT:
			try:
				return getattr(self,qtype+"answer")
			except AttributeError:
				pass
		raise Answer.TypelessAnswer()

	def get_typed_question(self):
		return self.get_child_answer().get_typed_question()
	def get_generic_question(self):
		return self.get_child_answer().get_generic_question()
	def attempt_status(self):
		# should return True for correct answer, False for wrong answer and None for not attempted
		return self.get_child_answer().attempt_status()
	def get_section(self):
		return self.get_child_answer().get_section()
	def __str__(self):
		return self.get_qtype()+" : "+str(self.get_child_answer())

# MCQ questions ====================================================================================

class McqQuestion(models.Model):
	question = models.OneToOneField(Question)
	multicorrect = models.BooleanField(default=False)

	def get_qtype(self):
		return "mcq"
	def get_section(self):
		return self.question.section
	def __str__(self):
		return str(self.question)
	def no_of_correct_options(self):
		return self.mcqoption_set.filter(is_correct=True).count()

	class NoCorrectOption(CustomException):
		def __str__(self):
			return "There is no correct option for this mcq"
	class TooManyCorrectOptions(CustomException):
		def __str__(self):
			return "multicorrect is False, yet there are multiple correct options for this mcq"

	def verify_correct_options(self):
		# raises an exception if the number of correct options is wrong
		correct_options = self.no_of_correct_options()
		if correct_options == 0:
			raise McqQuestion.NoCorrectOption()
		elif self.multicorrect==False and correct_options>1:
			raise McqQuestion.TooManyCorrectOptions()

	def export(self):
		mcq_ques_dict = {}
		if self.multicorrect:
			mcq_ques_dict["type"]="mmcq"
		else:
			mcq_ques_dict["type"]="mcq"
		mcq_ques_dict["options"] = [option.export() for option in self.mcqoption_set.order_by('id')]
		return mcq_ques_dict

class McqOption(models.Model):
	title = models.CharField(max_length=30,blank=True)
	text = models.TextField(blank=False)
#	sno = models.PositiveIntegerField(default=0)
	is_correct = models.BooleanField(default=False)
	mcq_question = models.ForeignKey(McqQuestion)

	def option_text(self):
		if self.title: return self.title
		else: return self.text

	def export(self):
		if not self.title and not self.is_correct:
			return self.text
		else:
			mydict = {"text":self.text}
			if self.title: mydict["title"] = self.title
			if self.is_correct: mydict["is_correct"] = self.is_correct
			return mydict

	def __str__(self):
		return str(self.mcq_question) + " : " + self.option_text()

class McqAnswer(models.Model):
	answer = models.OneToOneField(Answer)
	mcq_question = models.ForeignKey(McqQuestion)
	chosen_options = models.ManyToManyField(McqOption,through="McqAnswerToMcqOption")

	def verify_options(self):
		# returns True if all options belong to this question and False otherwise
		good_options = self.chosen_options.filter(mcq_question=self.mcq_question).count()
		all_options = self.chosen_options.count()
		return good_options == all_options

	def attempt_status(self):
		total_options = self.chosen_options.count()
		if total_options==0:
			return None
		wrong_options = self.chosen_options.filter(is_correct=False).count()
		return wrong_options == 0
	def get_section(self):
		return self.mcq_question.get_section()
	def get_qtype(self):
		return self.mcq_question.get_qtype()
	def get_typed_question(self):
		return self.mcq_question
	def get_generic_question(self):
		return self.mcq_question.question
	def __str__(self):
		return " ; ".join([option.option_text() for option in self.chosen_options.all()])

	def save(self,*args,**kwargs):
		if self.answer.section_answer_sheet.section != self.get_section():
			raise AnswerHasInvalidSection()
#		super().save(*args,**kwargs)
		super(McqAnswer,self).save(*args,**kwargs)

class McqAnswerToMcqOption(models.Model):
	mcq_answer = models.ForeignKey(McqAnswer)
	mcq_option = models.ForeignKey(McqOption)

	def save(self,*args,**kwargs):
		if self.mcq_answer.mcq_question != self.mcq_option.mcq_question:
			raise McqOptionDoesNotMatchQuestion()
#		super().save(*args,**kwargs)
		super(McqAnswerToMcqOption,self).save(*args,**kwargs)

# Text Questions ===================================================================================

class TextQuestion(models.Model):
	question = models.OneToOneField(Question)
	ignore_case = models.BooleanField(default=True)
	use_regex = models.BooleanField(default=False)
	correct_answer = models.TextField(blank=False)

	def get_qtype(self):
		return "text"
	def get_section(self):
		return self.question.section
	def __str__(self):
		return str(self.question)
	def check_response(self,response):
		if self.use_regex:
			if self.ignore_case: flags=0
			else: flags=re.IGNORECASE
			return bool(re.fullmatch(self.correct_answer,response,flags))
		else:
			if self.ignore_case:
				return response.lower()==self.correct_answer.lower()
			else:
				return response==self.correct_answer

	def export(self):
		text_ques_dict = {}
		if self.use_regex:
			text_ques_dict["type"]="regex"
		else:
			text_ques_dict["type"]="text"
		text_ques_dict["answer"] = self.correct_answer
		text_ques_dict["ignore_case"] = self.ignore_case
		return text_ques_dict

class TextAnswer(models.Model):
	answer = models.OneToOneField(Answer)
	text_question = models.ForeignKey(TextQuestion)
	response = models.TextField(blank=True)

	def attempt_status(self):
		if self.response:
			return self.text_question.check_response(self.response)
		else:
			return None
	def get_section(self):
		return self.text_question.get_section()
	def get_qtype(self):
		return self.text_question.get_qtype()
	def get_typed_question(self):
		return self.text_question
	def get_generic_question(self):
		return self.text_question.question
	def __str__(self):
		return self.response
	def save(self,*args,**kwargs):
		if self.answer.section_answer_sheet.section != self.get_section():
			raise AnswerHasInvalidSection()
#		super().save(*args,**kwargs)
		super(TextAnswer,self).save(*args,**kwargs)
