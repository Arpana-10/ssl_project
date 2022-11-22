from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import  passwordchange
from django.contrib.auth.models import User
from django.views import View
from django.http import HttpResponseRedirect 
from .models import assignments, UserProfile, courses, studentsubmissions
from .forms import assignment_form, UserForm, UserProfileForm, course_form, course_reg, solution, csv_form, feedback_form
from django.views.generic import ListView
from django.template import RequestContext
from django.template.loader import get_template
from django.http import HttpResponse
from zipfile import ZipFile
import os, csv
from io import BytesIO
from django.conf import settings
from django.core.mail import send_mail
import datetime
from time import gmtime, strftime
import subprocess

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
                    sols = ass.s.all()
                    d = False
                    for s in sols:
                        if s.username == request.user.username:
                            d=True
                    if d == False:   
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
    Errmsg = ""
    Succmsg = ""  
    if request.method == 'POST':
        submitted_form = assignment_form(request.POST, request.FILES)
        if submitted_form.is_valid():
            print("here")
            doc = request.FILES
            doc_name = doc["assignmentfile"]
            x = courses.objects.get(id = num)
            tree = submitted_form.cleaned_data['Tree']
            auto = submitted_form.cleaned_data['autograder']
            if tree.name.endswith('.txt') :
                course_added = assignments(assignmentfile = doc_name, title = submitted_form.cleaned_data["title"], deadline = submitted_form.cleaned_data['deadline'], upload_type = submitted_form.cleaned_data['upload_type'], autograder = auto, Tree = tree )
                course_added.save()
                x.assignments.add(course_added)
                # x.ass_n = n+1
                print(course_added.deadline, "-----")
                x.save()
                Succmsg = "Successfully created"
            else:
                Errmsg = "upload the tree structure in a .txt file"
            #print( current_user.usercurrent_user = request.username)
            # return render(request, "users/teach_profile.html")
        else:
            Errmsg = "invalid form"
    submitted_form = assignment_form()
    context = {
			"form": submitted_form,
            "Errmsg" : Errmsg,
            "Succmsg" : Succmsg,
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
            
            if request.user.u.identity == "teacher":
                
                code = strftime("%Y%m%d%H%M%S", gmtime())
                course_added = courses(title = submitted_form.cleaned_data['title'], code = code)
                course_added.save()
                current_user = request.user
                #print( current_user.usercurrent_user = request.username)
                c = UserProfile.objects.get(user_name = current_user.username)
                c.courses_registered.add(course_added)
                c.save()
                SuccMsg = "Course successfully created"
                context = {
                    "msg" : SuccMsg,
                    'code' : code,
                }
                # return render(request, "users/teach_profile.html", context)
                # ErrMsg = "Course Already exists"

            if request.user.u.identity == "student" :
                courseExists = courses.objects.filter(code = submitted_form.cleaned_data['code']).exists()
                if courseExists:
                    course = courses.objects.get(code = submitted_form.cleaned_data['code'])
                    c = UserProfile.objects.get(user_name = request.user.username)
                    c.courses_registered.add(course)
                    c.save()
                    SuccMsg = "Successfully registered for the course"
                    # return render(request, "users/st_profile.html", context)

                else:
                    ErrMsg = "Course does not exist"
                    print("wrong code")        

    context = {
			"form": submitted_form,
            "Errmsg" : ErrMsg,
            "Succmsg" : SuccMsg,
		}
    return render(request, 'users/courses.html', context)   


def assignment_views( request, num):
    if request.method == 'GET':

        x = courses.objects.get(id = num).assignments.all()
        l = []
        for element in x:
            l.append(element)
        print(l)
        assignments = {}
        assignments["assignment"] = l
        assignments["ass"] = request.path
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
                if c.id == num:
                    l.append(user)
    context = {
        "num":num,
        "users" : l
    }
    return render(request, 'users/course_page_teach.html', context)

        
def solution_upload(request, num1, num2):
    msg = ""
    if request.method == 'POST':
        submitted_form = solution(request.POST, request.FILES)
        if submitted_form.is_valid():
            doc = request.FILES
            doc_name = doc["assignment"]
            x = courses.objects.get(id = num1)
            z = x.assignments.get(id = num2).upload_type
            if not doc_name.name.endswith(z):
                # messages.error(request,'Please upload a' + str(z) + 'file')
                msg= 'Please upload a ' + str(z) + ' file'
                print("----------")
                
            else:
                current_user = request.user
                s = studentsubmissions(solution = doc_name, username = current_user.username, file_name = submitted_form.cleaned_data['name'] )
                s.save()
                x = courses.objects.get(id = num1)
                x.assignments.get(id = num2).s.add(s)
                if x.assignments.get(id = num2).deadline < s.created_at:
                    studentsubmissions.objects.filter(id = s.id).update(status = "late")
                else:
                    studentsubmissions.objects.filter(id = s.id).update(status = "success")
                # 20221121111714 check
                # 20221121113337 try1
                x.save()
                
                zipf = studentsubmissions.objects.get(id = s.id).solution
                autograder = x.assignments.get(id = num2).autograder
                tree = x.assignments.get(id = num2).Tree

                name = doc_name.name[:-4]
                command1 = f"unzip media/{zipf} -d ./submissions/"
                
                # print(name, command1)
                p1 = subprocess.run(command1, capture_output=True, shell=True)
                command2 = "cd submissions/;ls"
                p2 = subprocess.run(command2, capture_output=True, shell=True)
                dirname = p2.stdout.decode().strip("\n")
                command3 = "cd submissions/;tree -a "+ dirname +" > test.txt; diff test.txt "+str(tree.file)
                # print(dirname, command3, sep=", ")
                p3 = subprocess.run(command3, capture_output=True, shell=True)
                output = p3.stdout.decode()

                if output != "":
                    msg = "tree structure not matching , check again"
                    studentsubmissions.objects.filter(id = s.id).update(marks = 0)
                    studentsubmissions.objects.filter(id = s.id).update(feedback = msg)  
                else:
                    print(dir, "yayaaa")  
                    msg = "tree structer matched"
                    command = "cd submissions/;python3 "+str(autograder.file)+" "+dirname
                    obj = subprocess.run(command, capture_output=True, shell=True)
                    output = obj.stdout.decode()
                    l = []
                    list = output.splitlines()
                    for item in list:
                        a = item.split(" : ")
                        l.append(a)
                    print(l)
                    studentsubmissions.objects.filter(id = s.id).update(marks = l[0][1])
                    studentsubmissions.objects.filter(id = s.id).update(feedback = l[2][1])
                finalcomm = "cd submissions/;rm -r "+dirname+"; rm test.txt"
                subprocess.run(finalcomm,shell=True)
                # provide submission as a command line argument
                # assumptions : the autograder will not unzip the file , i am unzipping and storing it ia temporary directory 
                # running the autograder on that file and processing the output
                # finally deleting the submitted folder since zip file is already there in media/uploads/
                # provide submission as a command line argument

    current_user = request.user
    x = courses.objects.get(id = num1)
    y = x.assignments.get(id = num2).s.filter(username = current_user.username)
    z = x.assignments.get(id = num2)
    l = []
    for s in y:
        l.append(s)                
    submitted_form = solution()
    context = {
			"form": submitted_form, 
            "sol": l,
            "ass_file":z,
            'msg':msg,
		} 
    return render(request, 'users/sol.html', context)

def all_submissions(request, num1, num2):
    x = courses.objects.get(id = num1)
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
            form = feedback_form(request.POST)
            if form.is_valid():
                u = request.POST.get('submit')
                a = x.assignments.get(id = num2).s.filter(username = u)
                max = a[0]
                for i in a:
                    if i.created_at > max.created_at:
                        max = i
                feedback_user = form.cleaned_data["feedback"]
                marks_user = form.cleaned_data["marks"]
                max.feedback = feedback_user
                max.save()
                max.marks = marks_user
                max.save()
                empty_form = feedback_form()
                X = courses.objects.get(id = num1)
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
    profiles = courses.objects.get(id = num1).assignments.get(id = num2).s.all()
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
                        x = courses.objects.get(id = num1).assignments.get(id = num2).s.get(solution = fields[1])
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


def deregister_view(request, num, uid):
    users = UserProfile.objects.get(id = uid)
    cc = users.courses_registered.get(id = num)
    courses_reg = users.courses_registered.remove(cc.id)

    return render(request, 'users/userprofile.html')
