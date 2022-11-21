from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, courses, assignments


class csv_form(forms.Form):
    csv_file = forms.FileField()
    
class solution(forms.Form):
    assignment = forms.FileField()
    name = forms.CharField(max_length=100)

class passwordchange(forms.Form):
    user_name = forms.CharField(max_length=100)
    password_final = forms.CharField(max_length=100)
    
class feedback_form(forms.Form):
    feedback = forms.CharField(max_length=300)
    marks = forms.IntegerField()

class assignment_form(forms.ModelForm, forms.Form):
    time = forms.TimeField()
    class Meta:
        model = assignments
        fields = ['assignmentfile','title','code','deadline' ,'upload_type']
        widgets = {
            'deadline' : forms.SelectDateWidget
        }

class course_form(forms.ModelForm):
    class Meta:
        model = courses
        fields =  ['title', ]
        
class course_reg(forms.Form):
    code = forms.CharField( max_length = 50)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        help_texts = {
	    	'username': 'Enter your College Roll No.',
		} 
        fields = ['username', 'email', 'password']
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("password does not match")

class UserProfileForm(forms.ModelForm):
	class Meta:
		model = UserProfile
		fields = ['full_name', 'roll_no','identity', ]