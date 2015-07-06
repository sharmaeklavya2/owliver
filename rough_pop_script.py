from main.models import *
from django.contrib.auth.models import User
import datetime
from django.utils import timezone

eklavya = User(username="eklavya")
eklavya.save()

myexam = Exam(name="Sample exam")
myexam.save()
mysection = Section(name="Sample section", exam=myexam, correct_marks=4, wrong_marks=-1)
mysection.save()

myeas = ExamAnswerSheet(exam=myexam, user=eklavya, start_time=timezone.now(), end_time=timezone.now())
myeas.save()
mysas = SectionAnswerSheet(section=mysection, exam_answer_sheet=myeas)
mysas.save()

# MCQ Questions ====================================================================================

ques1 = Question(text="What is the capital of India?", section=mysection)
ques1.save()
ques2 = Question(text="What is the capital of USA?", section=mysection)
ques2.save()

mcq1 = McqQuestion(question=ques1, multicorrect=False)
mcq1.save()
mcq2 = McqQuestion(question=ques2, multicorrect=False)
mcq2.save()

opt1a = McqOption(text="Delhi", is_correct=True, mcq_question=mcq1)
opt1a.save()
opt1b = McqOption(text="Bombay", is_correct=False, mcq_question=mcq1)
opt1b.save()
opt1c = McqOption(text="Kolkata", is_correct=False, mcq_question=mcq1)
opt1c.save()

opt2a = McqOption(text="New York", is_correct=False, mcq_question=mcq2)
opt2a.save()
opt2b = McqOption(text="Washington DC", is_correct=True, mcq_question=mcq2)
opt2b.save()
opt2c = McqOption(text="Florida", is_correct=False, mcq_question=mcq2)
opt2c.save()

ans1 = Answer(section_answer_sheet=mysas)
ans1.save()
ans2 = Answer(section_answer_sheet=mysas)
ans2.save()

mcqans1 = McqAnswer(answer=ans1,mcq_question=mcq1)
mcqans1.save()
mcqans2 = McqAnswer(answer=ans2,mcq_question=mcq2)
mcqans2.save()

McqAnswerToMcqOption(mcq_answer=mcqans1, mcq_option=opt1a).save()
McqAnswerToMcqOption(mcq_answer=mcqans2, mcq_option=opt2a).save()

# Subj Questions ===================================================================================

ques3 = Question(text="Who is India's Prime Minister?", section=mysection)
ques3.save()
ques4 = Question(text="What is the chemical formula of water?", section=mysection)
ques4.save()

textq1 = TextQuestion(question=ques3, correct_answer_re="Narendra Modi")
textq1.save()
textq2 = TextQuestion(question=ques4, correct_answer_re="H2O")
textq2.save()

ans3 = Answer(section_answer_sheet=mysas)
ans3.save()
ans4 = Answer(section_answer_sheet=mysas)
ans4.save()

textans1 = TextAnswer(answer=ans3,text_question=textq1,response="Narendra Modi")
textans1.save()
textans2 = TextAnswer(answer=ans4,text_question=textq2,response="H2O2")
textans2.save()

