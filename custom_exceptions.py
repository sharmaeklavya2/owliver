class CustomException(Exception):
	pass

class QuestionTypeNotImplemented(CustomException,NotImplementedError):
	qtype = "unspecified"
	def __init__(self,qtype):
		self.qtype=qtype
	def __str__(self):
		return "Questions of type \""+qtype+"\" are not yet supported"
