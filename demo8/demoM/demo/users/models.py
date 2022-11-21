from django.db import models
from django.contrib.auth.models import Permission, User
from django.shortcuts import render
from django.utils import timezone


class studentsubmissions(models.Model):
	username = models.CharField(max_length = 50 )
	solution = models.FileField(upload_to ='uploads/')
	file_name = models.CharField(max_length = 300, default = "x")
	feedback = models.CharField(max_length = 300)
	marks = models.IntegerField(blank= True, null = True)
	created_at = models.DateTimeField(auto_now_add=True, editable=False)
	status = models.CharField( max_length=100, default="pending") #late if submitted after deadline else success

class assignments(models.Model):
	assignmentfile = models.FileField(upload_to ='uploads/')
	title = models.CharField( max_length = 50, unique=True)
	FILE_TYPES =(
		('.zip','.zip'),
		('.tgz','.tgz'),
		('.cpp','.cpp'),
		('.py','.py'),
	)
	# status = models.CharField( max_length=100, default="pending")
	deadline = models.DateTimeField()
	s =  models.ManyToManyField(studentsubmissions)
	upload_type = models.CharField(choices=FILE_TYPES,max_length=20,default=".zip")

class courses(models.Model):
	assignments = models.ManyToManyField(assignments)
	title = models.CharField( max_length = 50)
	code = models.CharField(max_length = 50)
	# ids = models.IntegerField(unique = True)
	# ass_n = models.IntegerField(default = 1)

class UserProfile(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="u")
	IDENTITY_CHOICE=(
		('teacher','teacher'),
		('student', 'student'),
		('assistant','assistant'),
	)
	user_name = models.CharField(max_length = 100, default="")
	identity=models.CharField(choices=IDENTITY_CHOICE,max_length=100,default="student")
	courses_registered=models.ManyToManyField(courses, default="")
	full_name = models.CharField(max_length = 100)
	#year = models.IntegerField(choices=YEAR_IN_COLLEGE_CHOICES, default=1)
	roll_no = models.CharField(max_length = 9, unique=True)
	#created = models.DateField(editable=False, null=True)

	def __str__(self):
		return self.roll_no

	def save(self):
		if not self.id:
			self.roll_no = self.user.username
			#self.created = datetime.date.today()
		super(UserProfile, self).save()


