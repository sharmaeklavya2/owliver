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
#	"match": "Match the following",
#	"mmatch": "Matrix match",
#	"order": "Arrange in order",
#	"bool": "True or False",
}

# Extra question types:
# mmcq is mcq with multicorrect=True
# regex is text with use_regex=True

QUESTION_TYPE = list(QUESTION_TYPE_DICT.items())

class InvalidOptionsForQuestion(Exception):
	def __str__(self):
		return "These options are invalid for the question"
class OptionDoesNotMatchQuestion(Exception):
	def __str__(self):
		return "Some options do not match the question"
class InvalidQuestionType(Exception):
	def __str__(self):
		return "This is an invalid type of question"
class AnswerHasInvalidSection(Exception):
	def __str__(self):
		return "this answer's question belongs to a section which is not the same as it's section_answer_sheet's section"
class SectionAnswerSheetHasInvalidExam(Exception):
	def __str__(self):
		return "this section_answer_sheet's section belongs to an exam which is not the same as it's exam_answer_sheet's exam"

class Exam(models.Model):
	name = models.CharField(max_length=50,blank=False)
	info = models.TextField(blank=True)
	time_limit = models.DurationField("Time limit to complete exam",default=timedelta())
		# timedelta() means infinite time
	shuffle_sections = models.BooleanField("Randomly shuffle sections",default=False)
	comment = models.TextField(blank=True)

	def __str__(self):
		return self.name

class Section(models.Model):
	name = models.CharField(max_length=50,blank=False)
	info = models.TextField(blank=True)
	exam = models.ForeignKey(Exam)
#	sno = models.PositiveIntegerField(default=0)
	comment = models.TextField(blank=True)

	def __str__(self):
		return self.exam.name+" : "+self.name

	# marking scheme
	correct_marks = models.PositiveIntegerField("Marks for correct answer",default=1)
	wrong_marks = models.PositiveIntegerField("Marks for wrong answer",default=0)
	na_marks = models.PositiveIntegerField("Marks for not attempting question",default=0)
	hint_deduction = models.PositiveIntegerField("Marks deducted for viewing hint",default=0)

# These options will be used if question customization is off
#	# max option (0 to allow all)
#	max_mcq_options = models.PositiveIntegerField("Max options allowed in a single-correct MCQ question",default=0)
#	max_mmcq_options = models.PositiveIntegerField("Max options allowed in a multi-correct MCQ question",default=0)
#	max_match_options = models.PositiveIntegerField("Max options allowed in a match-the-following question",default=0)
#	max_mmatch_options = models.PositiveIntegerField("Max options allowed in a matrix match question",default=0)
#	max_order_options = models.PositiveIntegerField("Max options allowed in an ordering question",default=0)

	# unlock
	unlock_marks = models.PositiveIntegerField("Minimum marks to attempt this section",default=0)
	unlock_questions = models.PositiveIntegerField("Minimum attempted questions to attempt this section",default=0)
	unlock_both_needed = models.BooleanField("Should both minimum question and minimum marks requirements be fulfilled?",default=False)
	def is_unlocked(self,marks,questions):
		has_marks = self.unlock_marks<=marks
		has_questions = self.unlock_questions<=questions
		if self.unlock_both_needed:
			return (has_marks and has_questions)
		else:
			return (has_marks or has_questions)

	#shuffle
	shuffle_options = models.BooleanField("Randomly shuffle options of questions",default=False)
	shuffle_questions = models.BooleanField("Randomly shuffle questions",default=False)

	# other restrictions
	allowed_attempts = models.PositiveIntegerField("Number of attempts allowed per question",default=0)
		# if allowed_attempts is 0, student will have infinite attempts but attempt status will not be shown
		# otherwise attempt status will be shown
	show_correct_answer = models.BooleanField("Should correct answer be shown after attempting a question?",default=False)
		# if show_correct_answer is True and allowed_attempts is not 0,
		# student will be shown correct answer after exhausting all attempts
	max_questions_to_attempt = models.PositiveIntegerField("Maximum number of questions a student is allowed to attempt",default=0)
		# if this value is 0, all questions can be attempted

class Question(models.Model):
	title = models.CharField(max_length=120,blank=True)
	text = models.TextField(blank=True)
	hint = models.TextField(blank=True)
#	qtype = models.CharField("Question Type",max_length=8,choices=QUESTION_TYPE)

	def __str__(self):
		if self.title: return self.title
		elif len(self.text)<30: return self.text
		else: return "Untitled"

	def get_qtype(self):
		for qtype in QUESTION_TYPE_DICT:
			if hasattr(self,qtype+"question"):
				return qtype

	def get_child_question(self):
		qtype = self.get_qtype()
		return getattr(self,qtype+"question")

	section = models.ForeignKey(Section)
#	sno = models.PositiveIntegerField(default=0)
	comment = models.TextField(blank=True)
	metadata = models.TextField(blank=True)

class ExamAnswerSheet(models.Model):
	exam = models.ForeignKey(Exam)
	user = models.ForeignKey(User)
	start_time = models.DateTimeField(null=True)
	end_time = models.DateTimeField(null=True)

	def __str__(self):
		return str(user)+" : "+str(exam)
	def get_duration(self):
		if self.start_time==None or self.end_time==None:
			return None
		else:
			return self.end_time - self.start_time

class SectionAnswerSheet(models.Model):
	# Answer Objects FK to this model
	section = models.ForeignKey(Section)
	exam_answer_sheet = models.ForeignKey(ExamAnswerSheet)
	def __str__(self):
		return str(section)
	def save(self,*args,**kwargs):
		if self.section.exam != self.exam_answer_sheet.exam:
			raise SectionAnswerSheetHasInvalidExam()
#		super().save(*args,**kwargs)
		super(SectionAnswerSheet,self).save(*args,**kwargs)

class Answer(models.Model):
	section_answer_sheet = models.ForeignKey(SectionAnswerSheet)
#	question = models.ForeignKey(Question)

	def get_qtype(self):
		for qtype in QUESTION_TYPE_DICT:
			if hasattr(self,qtype+"answer"):
				return qtype

	def get_child_answer(self):
		qtype = self.get_qtype()
		return getattr(self,qtype+"answer")

	def is_correct(self):
		return self.get_child_answer().is_correct()
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

	class NoCorrectOption(Exception):
		def __str__(self):
			return "There is no correct option for this mcq"
	class TooManyCorrectOptions(Exception):
		def __str__(self):
			return "multicorrect is False, yet there are multiple correct options for this mcq"

	def verify_correct_options(self):
		# raises an exception if the number of correct options is wrong
		correct_options = self.no_of_correct_options()
		if correct_options == 0:
			raise McqQuestion.NoCorrectOption()
		elif self.multicorrect==False and correct_options>1:
			raise McqQuestion.TooManyCorrectOptions()

class McqOption(models.Model):
	title = models.CharField(max_length=30,blank=True)
	text = models.TextField(blank=False)
#	sno = models.PositiveIntegerField(default=0)
	is_correct = models.BooleanField(default=False)
	mcq_question = models.ForeignKey(McqQuestion)

	def option_text(self):
		if self.title: return self.title
		else: return self.text

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

	def is_correct(self):
		wrong_options = self.chosen_options.filter(is_correct=False).count()
		return wrong_options == 0
	def get_section(self):
		return self.mcq_question.get_section()
	def get_qtype(self):
		return self.mcq_question.get_qtype()
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
			raise OptionDoesNotMatchQuestion()
#		super().save(*args,**kwargs)
		super(McqAnswerToMcqOption,self).save(*args,**kwargs)

# Text Questions ===================================================================================

class TextQuestion(models.Model):
	question = models.OneToOneField(Question)
	ignore_case = models.BooleanField(default=False)
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

class TextAnswer(models.Model):
	answer = models.OneToOneField(Answer)
	text_question = models.ForeignKey(TextQuestion)
	response = models.TextField(blank=True)

	def is_correct(self):
		return self.text_question.check_response(self.response)
	def get_section(self):
		return self.text_question.get_section()
	def get_qtype(self):
		return self.text_question.get_qtype()
	def __str__(self):
		return self.response
	def save(self,*args,**kwargs):
		if self.answer.section_answer_sheet.section != self.get_section():
			raise AnswerHasInvalidSection()
#		super().save(*args,**kwargs)
		super(TextAnswer,self).save(*args,**kwargs)
