from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import  passwordchange
from django.contrib.auth.models import User
from django.views import View
from django.http import HttpResponseRedirect 
from .models import assignments, UserProfile, courses, studentsubmissions
from .forms import assignment_form, UserForm, UserProfileForm, course_form, course_reg, solution, csv_form,feedback_form
from django.views.generic import ListView
from django.template import RequestContext
from django.template.loader import get_template
from django.http import HttpResponse
from zipfile import ZipFile
import os, csv
from io import BytesIO
from django.conf import settings
from django.core.mail import send_mail

def home(request):
    try:
        if(request.user.u.identity)=='student':
           
            assignment = []
            courses_reg = UserProfile.objects.get(user_name = request.user.username).courses_registered.all()
            for course in courses_reg:
                a = [course]
                app = False
                assign = course.assignments.all()
                for ass in assign:

                    if ass.status == "pending":
                        a.append(ass)
                        app = True
                
                if app == True:
                    # assignment.append(course)
                    assignment.append(a)
                    
            context = {
                'ass' : assignment,
            }
            return render(request, 'users/st_profile.html', context)
        elif(request.user.u.identity)=='teacher':
            return render(request, 'users/teach_profile.html')
    except:

        return render(request, 'users/st_profile.html')
    #return render(request, 'users/home.html')


def update(request):
    if request.method == "POST":
        form = passwordchange(request.POST)
        if form.is_valid():

    #   entered_username = request.POST['username']
    #   print(entered_username)
            #form.save()
            user_name = form.cleaned_data['user_name']
            final_password = form.cleaned_data['password_final']
            u = User.objects.get(username=user_name)
            u.set_password(f"{final_password}")
            u.save()
            return render(request, "users/passwordchanged.html")
    form = passwordchange()
    return render(request, 'users/updateprofile.html', {
        "form":form
    })

def createassignment(request, num):    
    if request.method == 'POST':
            submitted_form = assignment_form(request.POST, request.FILES)
            if submitted_form.is_valid():
                print("here")
                doc = request.FILES
                doc_name = doc["assignmentfile"]
                x = courses.objects.get(ids = num)
                # n = x.ass_n
                course_added = assignments(assignmentfile = doc_name, title = submitted_form.cleaned_data["title"], code =  submitted_form.cleaned_data["code"], deadline = submitted_form.cleaned_data['deadline'], upload_type = submitted_form.cleaned_data['upload_type'])
                course_added.save()
                x.assignments.add(course_added)
                # x.ass_n = n+1
                print(course_added.deadline, "-----")
                x.save()
                #print( current_user.usercurrent_user = request.username)
                return render(request, "users/teach_profile.html")
    submitted_form = assignment_form()
    context = {
			"form": submitted_form,
		}
    return render(request, 'users/assign.html', context)
        

def createcourse(request):
    if request.user.u.identity == "teacher":
        submitted_form = course_form(request.POST or None)
    else:
        submitted_form = course_reg(request.POST or None)
    ErrMsg = ""
    SuccMsg = ""
    print(7)
    print(request)
    if request.method == 'POST':
        print(request.user.u.identity)
        if submitted_form.is_valid():
            print(request.user.u.identity)
            courseExists = courses.objects.filter(title = submitted_form.cleaned_data['title']).exists()
            if request.user.u.identity == "teacher":
                if not courseExists:
                    course_added = courses(title = submitted_form.cleaned_data['title'], code = submitted_form.cleaned_data['code'], ids =  submitted_form.cleaned_data['ids'])
                    course_added.save()
                    current_user = request.user
                    #print( current_user.usercurrent_user = request.username)
                    c = UserProfile.objects.get(user_name = current_user.username)
                    c.courses_registered.add(course_added)
                    c.save()
                    SuccMsg = "Course successfully created"
                    context = {
                        "msg" : SuccMsg,
                    }
                    return render(request, "users/teach_profile.html", context)
                ErrMsg = "Course Already exists"

            if request.user.u.identity == "student" :
            
                if courseExists:
                    course = courses.objects.get(title = submitted_form.cleaned_data['title'])
                    if course.code == submitted_form.cleaned_data['code']:
                        c = UserProfile.objects.get(user_name = request.user.username)
                        c.courses_registered.add(course)
                        c.save()
                        SuccMsg = "Successfully registered for the course"
                        context = {
                            "msg" : SuccMsg,
                        }
                        return render(request, "users/st_profile.html", context)
                    else:
                        ErrMsg = "Incorrect code provided"
                        print("incorrect code")
                else:
                    ErrMsg = "Course does not exist"
                    print("wrong title")

                    

    context = {
			"form": submitted_form,
            "msg" : ErrMsg,
		}
    return render(request, 'users/courses.html', context)   


def assignment_views( request, num):
    if request.method == 'GET':

        x = courses.objects.get(ids = num).assignments.all()
        l = []
        for element in x:
            l.append(element)
        print(l)
        assignments = {}
        assignments["assignment"] = l
        assignments["ass"] = request.path
        if request.user.u.identity == "teacher":
            return render(request, 'users/all_assign_teach.html', assignments )
        else:
            return render(request, 'users/all_assign_std.html', assignments )
    

def allcourses_views(request):

    current_user = request.user
    
    courses = {}
    l = []
    for course in (UserProfile.objects.get(user_name= current_user.username).courses_registered.all()):
        l.append(course) 
    courses['courses_added'] = l
    return render(request, 'users/all_courses.html', courses)
   


def register_user(request):
    user_form = UserForm(request.POST or None)
        #print(3)
    profile_form = UserProfileForm(request.POST or None)
    registered = False
    if request.method == 'POST':
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.user_name = username
            profile.save()
            registered = True
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
						# login(request, user)
                    return redirect('login')
    print(3)                      
    context = {
			"pform": profile_form,
			"uform": user_form,
		}
    print(4)
    return render(request, 'users/reg.html', context)

# newly added code.

def course_page(request, num):
    l = []
    users = UserProfile.objects.all()
    for user in users:
        if user.identity == "student":
            course = user.courses_registered.all()
            print(course)
            for c in course:
                if c.ids == num:
                    l.append(user)
    context = {
        "num":num,
        "users" : l
    }
    if request.user.u.identity == "teacher":
        return render(request, 'users/course_page_teach.html', context)
    else:
        return render(request, 'users/course_page_std.html', context)
        
def solution_upload(request, num1, num2):
    if request.method == 'POST':
        submitted_form = solution(request.POST, request.FILES)
        if submitted_form.is_valid():
            doc = request.FILES
            doc_name = doc["assignment"]
            x = courses.objects.get(ids = num1)
            z = x.assignments.get(id = num2).upload_type
            if not doc_name.name.endswith(z):
                messages.error(request,'Please upload a' + str(z) + 'file')
                
            else:
                current_user = request.user
                s = studentsubmissions(solution = doc_name, username = current_user.username, file_name = submitted_form.cleaned_data['name'] )
                s.save()
                x.assignments.get(id = num2).s.add(s)
                if x.assignments.get(id = num2).deadline < s.created_at:
                    x.assignments.get(id = num2).filter(id = num2).update(status = "late")
                    print(x.assignments.get(id = num2).status)
                else:
                    x.assignments.filter(id = num2).update(status = "done")
                    print( "---", x.assignments.get(id = num2).status)

                x.save()
                if request.user.u.identity == "teacher":
                    return redirect('http://127.0.0.1:8000/allcourses/')
                else:
                    return redirect('http://127.0.0.1:8000/allcourses/')  
    current_user = request.user
    x = courses.objects.get(ids = num1)
    y = x.assignments.get(id = num2).s.filter(username = current_user.username)
    z = x.assignments.get(id = num2)
    l = []
    for s in y:
        l.append(s)                
    submitted_form = solution()
    context = {
			"form": submitted_form, 
            "sol": l,
            "ass_file":z
		} 
    return render(request, 'users/sol.html', context)

def all_submissions(request, num1, num2):
    x = courses.objects.get(ids = num1)
    y =  x.assignments.get(id = num2).s.all()
    l = []
    d = {}
    for s in y:
        if s.username in d.keys():
            if s.created_at > d[s.username].created_at :
                d[s.username] = s
        else:
            d[s.username] = s
    for i in d:
        l.append(d[i])

    if request.method == 'POST':
        if request.POST.get('form_id',False) == 'feed':
            # print(1)
            form = feedback_form(request.POST)
            if form.is_valid():
                
                print(request.POST.get('submit'))
                u = request.POST.get('submit')
                
                # x = courses.objects.get(ids = num1).assignments.get(number = num2).s.get(solution = fields[1])

                # for i in u:
                #     if(u.created_at )
                a = x.assignments.get(id = num2).s.filter(username = u)
                # print(a)
                max = a[0]
                for i in a:
                    if i.created_at > max.created_at:
                        max = i
                feedback_user = form.cleaned_data["feedback"]
                # print(feedback_user)
                marks_user = form.cleaned_data["marks"]
                # print(max.marks)
                max.feedback = feedback_user
                max.save()
                max.marks = marks_user
                max.save()
                # print(max.feedback)
                # print(max.marks)
                # print(a)
                # print(a[0].feedback)
                # f = studentsubmissions(username = u, feedback = feedback_user)
                # f.save()
                # print(f)
                # print(f.feedback)
                empty_form = feedback_form()
                X = courses.objects.get(ids = num1)
                Y =  X.assignments.get(id = num2).s.all()
                L = []
                D = {}
                for S in Y:
                    if S.username in D.keys():
                        if S.created_at > D[S.username].created_at :
                            D[S.username] = S
                    else:
                        D[S.username] = S
                for i in D:
                    L.append(D[i])
                context={
                    "sol": L,
                    "num1": num1,
                    "num2":num2,
                    "form":empty_form
                }
                return render(request, 'users/submissions.html',context)
        elif request.POST.get('form_id',False) =='download':
            filenames = []
            for f in l:
                filenames.append(f.solution.url)
            zip_subdir = "submissions"
            zip_filename = "%s.zip" % zip_subdir

            s = BytesIO()
            zf = ZipFile(s, "w")
            for fpath in filenames:
                fdir, fname = os.path.split(fpath)
                zip_path = os.path.join(zip_subdir, fname)
                fpath = "." + fpath
                zf.write(fpath, zip_path)
            zf.close()
            resp = HttpResponse(s.getvalue(), content_type = "application/x-zip-compressed")
            resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
            return resp

    form = feedback_form()
    context={
        "sol": l,
        "num1": num1,
        "num2":num2,
        "form":form
    }
    return render(request, 'users/submissions.html', context)

def export_to_csv(reuest, num1, num2):
    profiles = courses.objects.get(ids = num1).assignments.get(id = num2).s.all()
    response = HttpResponse('text/csv')
    response['Content-Disposition'] = 'attachment; filename=profile_export.csv'
    writer = csv.writer(response)
    writer.writerow(['username', 'solution', 'feedback', 'marks'])
    d = {}
    profile_fields = []
    for s in profiles:
        if s.username in d.keys():
            if s.created_at > d[s.username].created_at :
                d[s.username] = s
        else:
            d[s.username] = s
    for i in d:
        profile_fields.append((d[i].username , d[i].solution, d[i].feedback, d[i].marks ))
    # profile_fields = profiles.values_list('username', 'solution', 'feedback', 'marks' )
    for profile in profile_fields:
        print(profile)
        writer.writerow(profile)
    return response

def marks( request, num1, num2):
    if request.method == 'POST':
        submitted_form = csv_form(request.POST, request.FILES)
        if submitted_form.is_valid():
            csv_file = submitted_form.cleaned_data['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'File is not CSV type')
            else:
                file_data = csv_file.read().decode('utf-8')
                lines = file_data.split('\n')
                i = 0
                for line in lines:
                    fields = line.split(',')
                    
                    if i!=0 and len(fields) == 4:
                        print(fields)
                        x = courses.objects.get(ids = num1).assignments.get(id = num2).s.get(solution = fields[1])
                        x.feedback = fields[2]
                        x.marks = fields[3]
                        x.save()
                    i = i+1
                return render(request, 'users/teach_profile.html')
                                    
    submitted_form = csv_form()
    context = {
			"form": submitted_form,
		}
    return render(request, 'users/marks.html', context)

def email_invite(request, num):
    subject = "subject"
    message = 'mshgg'
    email_from = settings.EMAIL_HOST_USER
    print("sending ")
    recipient_list = ['arpten11@gmail.com', ]
    send_mail( subject, message, email_from, recipient_list, fail_silently=False, )
    print("  hmm maybe sent  ")
    return render( request, 'email_invite.html')

def deregister_view(request, num, uid):
    users = UserProfile.objects.get(id = uid)
    cc = users.courses_registered.get(ids = num)
    courses_reg = users.courses_registered.remove(cc.id)
    # ass_rem = 

    return render(request, 'users/userprofile.html')
