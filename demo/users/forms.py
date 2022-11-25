from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, courses, assignments
from django.forms import TextInput, MultiWidget, DateTimeField
from . import deadline


class csv_form(forms.Form):
    """
    This class inherits from Django's forms and simply provides a form to upload the csv file (to update marks and give feedback to students)
    :param csv_file: This variable contain the csv file to be uploaded by the teacher
    :type csv_file: forms.FileField
    """
    csv_file = forms.FileField()
    
class solution(forms.Form):
    """
    This class inherits from Django's forms and provides a form to upload the solution to a particular assignment.
    :param assignment: This variable contains the solution file uploaded by the user to the assignment
    :type assignment: forms.FileField
    :param name: This variable stores the name of the submission done by the student
    :type name: str
    """
    assignment = forms.FileField()
    name = forms.CharField(max_length=100)

class passwordchange(forms.Form):
    """
    This class inherits from Django's forms and provides a form to change password of the user
    :param password_initial: This variable stores the initial password of the user
    :type password_initial: str
    :param password_final: This variable stores the final password of the user
    :type password_final: int
    """
    password_initial = forms.CharField(max_length=100)
    password_final = forms.CharField(max_length=100)
    
class feedback_form(forms.Form):
    """
    This class inherits from Django's forms and provides a form to upload marks and feedback to a submission to the assignment
    :param feedback: This variable stores the feedback to be uploaded to the submission
    :type feedback: str
    :param marks: This variable stores the marks to be uploaded to the submission
    :type marks: int
    """
    feedback = forms.CharField(max_length=300)
    marks = forms.IntegerField()


class assignment_form(forms.ModelForm, forms.Form):
    """
    This class inherits from Django's forms and provides a form to teacher to upload an assignment
    :param assignmentfile: This variable contains the assignment file which is  uploaded by the teacher
    :type assignmentfile: forms.FileField
    :param title: This variable contains the title of the uploaded file by teacher
    :type title: str
    :param upload_type: This variable contains the type of file to be uploaded by the student 
    :type upload_type: str
    :param Treestructure: This variable contains the file which contains the structure of the directory to be matched by user while making a submission
    :type Treestructure: forms.FileField
    """
    class Meta:
        model = assignments
        fields = ['assignmentfile','title', 'upload_type', 'Treestructure', 'autograder']
    deadline = DateTimeField(widget=deadline.MinimalSplitDateTimeMultiWidget())
class course_form(forms.ModelForm):
    """
    This class inherits from Django's forms and provides a form for teacher to upload an assignment
    :param title: This variable contains the title of the course which is being created by teacher
    :type title: str
    """
    class Meta:
        model = courses
        fields =  ['title' ]
        
class course_reg(forms.Form):
    """
    This class inherits from Django's forms and provides a form for students to register for a course
    :param code: This variable contains the code of the course which the user is registering to
    :type code: str
    """
    code = forms.CharField( max_length = 50)

class UserForm(forms.ModelForm):
    """
    This class inherits from Django's forms and provides a form for users to register themselves in the database

    :param username: This variable stores the username of the user, which is unique for each user
    :type username: str
    :param email: This variable stores the email address of the user 
    :type email: str
    :param password: This variable stores the password for the user to login
    :type password: str
    """
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        help_texts = {
	    	'username': 'Enter your College Roll No.',
		} 
        fields = ['username', 'password']
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("password does not match")

class UserProfileForm(forms.ModelForm):
    """
    This class inherits from Django's forms and provides a form for users to register themselves on the database
    :param full_name: This variable contains the full name of the user
    :type full_name: str
    :param roll_no: This variable contains the roll number of the user, which is unique for each user
    :type roll_no: str
    :param identity: This variable contains the identity of the user i.e. whether the user is a student or a teacher
    :type identity: str
    """
    class Meta:
        model = UserProfile
        fields = ['full_name', 'roll_no', 'email', 'identity',]