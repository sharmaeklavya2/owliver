# Models

For those who don't know what models are, they are just an abstraction of the objects involved in this project (along with functionality to read and write them to the database).

There are 3 main models: `User`, `Exam` and `ExamAnswerSheet`

An `Exam` stores all info about a test: all questions and their correct answers, how they are divided into sections and metadata like per-section marking scheme, time-limit, solutions, etc.

I named it `Exam` instead of `Test` because 'test' can also mean a unit test or something similar. ( [Test-driven development](https://en.wikipedia.org/wiki/Test-driven_development), [Python unittest](https://docs.python.org/3/library/unittest.html) )

A `User` represents a user who can log in and give exams on this site. I didn't need to make this model from scratch as django already provides it. (For those who know django, this is actually django.contrib.auth.models.User)

An `ExamAnswerSheet` is an area where a user's responses are recorded. An `ExamAnswerSheet` has an associated `Exam` and a `User` (the user who is giving the exam). In cases where an `Exams`'s sections or questions are to be shuffled and then presented to the user, the shuffling is recorded in the `ExamAnswerSheet`

## Details of Exam

Though the above 3 models are central to understanding Owliver, there are other submodels involved 

An `Exam` has multiple `Sections`. A `Section` has multiple `Questions`.

There are some settings which are per-question. For eg, in a text-based question, whether to check in a case-sensitive manner or not is stored in the `Question`.

There are some settings which are section-wide. For eg, marking scheme of `Question`s in a `Section` is stored in the `Section`.

Finally, some settings are exam-wide, like time limit and whether a user can give the exam multiple times or not.

An `Exam` can also have an owner, which is a `User`. The owner can edit or delete the exam (this functionality is not yet implemented). If the exam does not have an owner, it is a public exam.

## Further details

It'll be difficult to explain in more detail. So if you know django, you can go ahead and read [models.py](../main/models.py).
