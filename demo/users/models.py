from django.db import models
from django.contrib.auth.models import Permission, User
from django.shortcuts import render
from django.utils import timezone


class studentsubmissions(models.Model):
	"""
	This model contains all the information and field of data associated with submissions made by students to various assignments.

	:param username: This variable contains the username of the student who has made this submission
	:type username: str
	:param solution: This variable contains the solution file uploaded by the student
	:type solution: models.FileField
	:param file_name: This variable stores the name of the file uploaded by the student
	:type file_name: str
	:param feedback: This variable contains the feedback given by teacher(or autograder) to the student for this assignment submission
	:type feedback: str
	:param marks: This variable contains the marks given by teacher(or autograder) to the student for this assignment submission
	:type marks: int
	:param created_at: This variable contains the information about the date and time on which the submission was done
	:type created_at: models.DateTimeField
	:param status: This variable contains the status of the submission(whether it was submitted before deadline or after deadline)
	:type status: str
	"""
	
	username = models.CharField(max_length = 50 )
	solution = models.FileField(upload_to ='uploads/')
	file_name = models.CharField(max_length = 300, default = "x")
	feedback = models.CharField(max_length = 300)
	marks = models.IntegerField(blank= True, null = True)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	status = models.CharField( max_length=100, default="pending") #late if submitted after deadline else success

class assignments(models.Model):
	"""
	This model contains all the information and fields of data associated with assignments which we are storing.\n
	:param assignmentfile: This variable stores the assignment file uploaded by the teacher
	:type assignmentfile: models.FileField
	:param Treestructure: This variable stores the tree structure file that is supposed to be matched by the user for .zip and .tgz files
	:type Treestructure: models.FileField
	:param title: This variable stores the title of the assignment file uploaded by the teacher
	:type title: str
	:param deadline: This variable stores the deadline of the assignment to be submitted
	:type deadline: models.DateTimeField
	:param s: This variable stores all the information about the submissions made by students to this assignment
	:type s: list(users.models.studentsubmissions)
	:param upload_type: This variable stores the acceptable file/folder format type(extension) of the student submission.
	:type upload_type: str
	"""
	assignmentfile = models.FileField(upload_to ='uploads/')
	Treestructure = models.FileField(upload_to ='uploads/', null=True, blank = True)
	title = models.CharField( max_length = 50, unique=True)
	FILE_TYPES =(
		('.zip','.zip'),
		('.tgz','.tgz'),
		('.cpp','.cpp'),
		('.py','.py'),
		('.pdf', '.pdf'),
		('.sh', '.sh')
	)
	autograder = models.FileField(upload_to ='uploads', null=True, blank = True)
	deadline = models.DateTimeField()
	s =  models.ManyToManyField(studentsubmissions)
	upload_type = models.CharField(choices=FILE_TYPES,max_length=20,default=".py")

class courses(models.Model):
	"""
	This model contains all the information and field of data associated with the courses which we are storing.\n

	:param assignments: This variable stores all the assignments objects uploaded by the teacher to this course.
	:type assignments: list(users.models.assignments)
	:param title: This variable contains the title of the course
	:type title: str
	:param code: This variable contains the code related to course which is used for registration of the course
	:type code: str
	"""
	assignments = models.ManyToManyField(assignments)
	title = models.CharField( max_length = 50)
	code = models.CharField(max_length = 50)
	prof = models.CharField( max_length = 50, default = "Kavi")
	# ids = models.IntegerField(unique = True)
	# ass_n = models.IntegerField(default = 1)
class messages(models.Model):
	msg = models.CharField(max_length = 200, null = True, blank = True)
	prof = models.CharField(max_length = 50,  null = True, blank = True)
class UserProfile(models.Model):
	"""
	This model contains all the information and fields of the data of the user we are storing.\n

	:param user: This helps in matching our model to the pre defined User Django model.
	:type user: models.User
	:param user_name: This variable stores the user name of the user we are storing
	:type user_name: str
	:param identity: This variable stores the identity i.e. whether the user is a student or a teacher
	:type identity: str
	:param courses_registered: This variable stores all the courses for which this user is registered
	:type courses_registered: list(users.models.courses)
	:param full_name: This variable stores the full name of the user
	:type full_name: str
	:param roll_no: This variable stores the roll number of the user
	:type roll_no: str
	"""

	user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="u")
	IDENTITY_CHOICE=(
		('teacher','teacher'), 
		('student', 'student'),
		('assistant','assistant'),
	)
	messages = models.ManyToManyField(messages)
	user_name = models.CharField(max_length = 100, default="")
	identity=models.CharField(choices=IDENTITY_CHOICE,max_length=100,default="student")
	courses_registered=models.ManyToManyField(courses, default="")
	full_name = models.CharField(max_length = 100)
	#year = models.IntegerField(choices=YEAR_IN_COLLEGE_CHOICES, default=1)
	roll_no = models.CharField(max_length = 9, unique=True)
	email = models.EmailField( default = "pbhavana5454@gmail.com")
	#created = models.DateField(editable=False, null=True)

	def __str__(self):
		"""| This method returns the string representation of this node class.
        | It is called when str or print is invoked on the object.
        | In this function, it simply returns the Roll number of user
        
        :return: Returns the roll number of user.
        :rtype: str
		"""
		return self.roll_no

	def save(self):
		"""| This method overwrites the inherited save method from model.Model
		| It is used to save the data 
		"""
		if not self.id:
			self.roll_no = self.user.username
			#self.created = datetime.date.today()
		super(UserProfile, self).save()


