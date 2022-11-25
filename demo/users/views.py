from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages as m
from .forms import  passwordchange
from django.contrib.auth.models import User
from django.views import View
from django.http import HttpResponseRedirect 
from .models import assignments, UserProfile, courses, studentsubmissions, messages
from .forms import assignment_form, UserForm, UserProfileForm, course_form, course_reg, solution, csv_form, feedback_form, register_student_for_course
from django.views.generic import ListView
from django.template import RequestContext
from django.template.loader import get_template
from django.http import HttpResponse
from zipfile import ZipFile
import os, csv
from io import BytesIO
from django.conf import settings
from django.core.mail import EmailMessage, send_mail
import datetime
from time import gmtime, strftime
import subprocess
from django.contrib.auth import logout
import smtplib

def time(u):
    """
    function which returns deadline of the assignment, which is used to sort the assignments based on their deadline.\n
    :param u: assignment for which we want deadline
    :type u: model.assignment
    """
    return u.deadline

def home(request):
    """
    This view is used for rendering the home page of users.\n
    It checks whether the user is logged in or not and also if the user who is logged in is a teacher or a student and renders the
    corresponding home pages.\n
    If the user is logged out then it simply redirectsthe user to login page.\n
    If the user was a student, it also returns an extra argument context which contains the assignments of the student. The context is used to send the variable names to the templates to display the assignments of the student.

    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :return: returns the request to render the corresponding html pages
    """
    current_user = request.user
    if current_user.id != None:
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
                        l2 = a[1:]

                        l2.sort(key = time)
                        a = [a[0]]+l2
                        assignment.append(a)
                messages = UserProfile.objects.get(user_name = request.user.username).messages.all()
                msgs = []
                for message in messages:
                    msgs.append(message)

                context = {
                    'ass' : assignment,
                    'msgs':msgs
                }
                return render(request, 'users/st_profile.html', context)
            elif(request.user.u.identity)=='teacher':
                return render(request, 'users/teach_profile.html')
        except:

            return render(request, 'users/st_profile.html')
    return HttpResponseRedirect("/login/") 
    #return render(request, 'users/home.html')


def update(request):
    """
    This view is used to update the password of user's account.\n
    It takes the user to a new page to fill out a password change form and updates the password of the user.\n
    It then redirects the user to the login page for logging in again.
    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :return: returns the request to render the corresponding html pages
    """
    current_user = request.user
    msg = ""
    if current_user.id != None:
        if request.method == "POST":
            form = passwordchange(request.POST)
            if form.is_valid():

    #   entered_username = request.POST['username']
    #   print(entered_username)
            #form.save()
                initial_password = form.cleaned_data['password_initial']
                final_password = form.cleaned_data['password_final']
                u = User.objects.get(username=request.user.username)
                if request.user.check_password(initial_password):
                    msg = "Password is successfully changed"
                    u.set_password(f"{final_password}")
                    u.save()
                    return HttpResponseRedirect("/login/") 
                else:
                    m.error(request, "Check the password again")

                
        form = passwordchange()
        return render(request, 'users/updateprofile.html', {
        "form":form
    })
    else:
        return HttpResponseRedirect("/login/") 

def createassignment(request, num): 
    """
    This view allows only a teacher to create an assignment in a course to be visible to every student enrolled in that course.\n
    It saves the data in the database taken in from the assignment form declared in forms.py.\n
    Unauthorized users and students are not able to create an assignment and they simply get redirected to login page and home page respectively

    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :param num: id of the course
    :type num: int
    :return: returns the request to render the corresponding html pages
    """

    current_user = request.user
    if current_user.id != None:
        if (request.user.u.identity)=='teacher': 
            if request.method == 'POST':
             submitted_form = assignment_form(request.POST, request.FILES)
             if submitted_form.is_valid():
                print("here")
                doc = request.FILES
                doc_name = doc["assignmentfile"]
                x = courses.objects.get(id = num)
                tree = submitted_form.cleaned_data['Treestructure']
                au = submitted_form.cleaned_data['autograder']
                up = submitted_form.cleaned_data['upload_type']
                dd = submitted_form.cleaned_data["deadline"]
                tl = submitted_form.cleaned_data["title"]
                course_added = assignments(assignmentfile = doc_name, title = tl,  deadline = dd, upload_type = up, Treestructure =  tree, autograder = au )
                course_added.save()
                x.assignments.add(course_added)
                # x.ass_n = n+1
                print(course_added.deadline, "-----")
                x.save()
                context = {
                    "msg": "Assignment is successfully created"
                }
                #print( current_user.usercurrent_user = request.username)
                return render(request, "users/assign.html", context)
        else:
                return render(request, "users/st_profile.html" )

        submitted_form = assignment_form()
        context = {
			"form": submitted_form,
		}
        return render(request, 'users/assign.html', context)
    else:
        return HttpResponseRedirect("/login/") 

        


def createcourse(request):
 """
    This view allows a teacher to create a course to which students can register and for student to register for a course created by a teacher.\n
    1)If the user is a teacher, then a course code is generated by using the time and date of creation thus causing it to be always unique and a course with a title taken from the form is generated with this code.\n
    This code is used by students to register for this course.\n
    2)If the user is a student, then it takes the course code from the course_reg form and enrolls that particular student to that course if a course with that particular code exists and also adds the course to students course lists.\n
    Otherwise, it simply prompts them to refill the form.\n

    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :return: returns the request to render the corresponding html pages
 """
 current_user = request.user
 if current_user.id != None:
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
                submitted_form = course_form(request.POST or None)
                context = {
                    "form": submitted_form,
                    "msg" : SuccMsg,
                    'code' : code,
                }
                return render(request, "users/courses.html", context)
                # ErrMsg = "Course Already exists"

            if request.user.u.identity == "student" :
                courseExists = courses.objects.filter(code = submitted_form.cleaned_data['code']).exists()
                if courseExists:
                    course = courses.objects.get(code = submitted_form.cleaned_data['code'])
                    c = UserProfile.objects.get(user_name = request.user.username)
                    c.courses_registered.add(course)
                    c.save()
                    SuccMsg = "Successfully registered for the course"
                    context = {
                        "msg" : SuccMsg,
                    }
                    return render(request, "users/courses.html", context)

                else:
                    ErrMsg = "Course does not exist"
                    print("wrong code")        

    context = {
			"form": submitted_form,
            "msg" : ErrMsg,
		}
    return render(request, 'users/courses.html', context)  
 else:
    return HttpResponseRedirect("/login/") 



def assignment_views( request, num):
 """
 This view allows the user to view all the assignments of the course he has been enrolled to by sending the context and rendering it on the html page.\n
 It searchs for the course which have id = num and view all the assignments in that course.

 :param num: id of the course we are searching the assignments for
 :type num: int
 :param request: HttpRequest object which contains the metadata about the request
 :type request: HttpRequest
 :return: returns the request to render the corresponding html pages
 """
 
 current_user = request.user
 if current_user.id != None:
    if request.method == 'GET':

        x = courses.objects.get(id = num).assignments.all()
        l = []
        for element in x:
            l.append(element)
        print(l)
        assignments = {}
        assignments["assignment"] = l
        assignments["ass"] = request.path
        if request.user.u.identity == "teacher":
            return render(request, 'users/all_assign_std.html', assignments )
        else:
            return render(request, 'users/all_assign_std.html', assignments )
 else:
    return HttpResponseRedirect("/login/") 

    

def allcourses_views(request):
 """
 This view allows the user to view all the courses he has been enrolled to.\n
 It takes the current user from the request and get all the course he has been enrolled to from UserProfile model and renders it in the html page by sending it as a context.
 If the user is not authorized, it simply redirects the user to the login page.
 :param request: HttpRequest object which contains the metadata about the request
 :type request: HttpRequest
 :return: returns the request to render the corresponding html pages
 """
 current_user = request.user
 if current_user.id != None:
    current_user = request.user
    print( request.user.u.identity)
    courses = {}
    l = []
    for course in (UserProfile.objects.get(user_name= current_user.username).courses_registered.all()):
        l.append(course) 
    courses['courses_added'] = l
    return render(request, 'users/all_courses.html', courses)
 else:
    return HttpResponseRedirect("/login/") 

   


def register_user(request):
    """
    This view is used to register a user by taking in data from the registration form.\n
    If the data filled in the form is valid, it adds the user with these details to the database and redirects to login page.\n
    Otherwise if the data filled in the form is invalid, it simply prompts the user to refill the registration form.

    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :return: returns the request to render the corresponding html pages
    """
    user_form = UserForm(request.POST or None)
        #print(3)
    profile_form = UserProfileForm(request.POST or None)
    registered = False
    if request.method == 'POST':
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            email = profile_form.cleaned_data['email']
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.user_name = username
            profile.email = email
            profile.save()
            registered = True
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
						# login(request, user)
                    m.success(request, "Successfully Registered")
                    return HttpResponseRedirect("/login/") 
    print(3)                      
    context = {
			"pform": profile_form,
			"uform": user_form,
		}
    print(4)
    return render(request, 'users/reg.html', context)

# newly added code.

def course_page(request, num):
 """
 This view is used to view all the users registered for that course so that they can be displayed on course page when opened by a teacher.\n
 It gets the course which we are currently enquiring from the 'num' variable and maintains a list of the students enrolled in that course by searching for the courses students are enrolled in by going through all the students.\n
 It adds the list of students as a context to render request so that it can be displayed on the html page.\n
 If the user is not authorized it simply redirects it to login page.

 :param num: id of the course we are searching the users for
 :type num: int
 :param request: HttpRequest object which contains the metadata about the request
 :type request: HttpRequest
 :return: returns the request to render the corresponding html pages
 """
 current_user = request.user
 if current_user.id != None:
  if request.user.u.identity == "teacher":
    l = []
    l2 = []
    users = UserProfile.objects.all()
    for user in users:
        if user.identity == "student":
            k = 0
            course = user.courses_registered.all()
            print(course)
            for c in course:
                if c.id == num:
                    l.append(user)
                    k = 1
            if k == 0:
                l2.append(user)
    
    context = {
        "num":num,
        "users" : l,
        "students":l2
    }
    return render(request, 'users/course_page_teach.html', context)
  else:
    return render(request, 'users/st_profile.html')
 else:
    
    return HttpResponseRedirect("/login/") 
        
def solution_upload(request, num1, num2):
 """
    This view is used to upload the solution for each assignment only if the submitted file format match the upload_type specified by the teacher.\n
    As soon as a submission is made, the file format is checked, if its not as specified the users gets a message.\n
    Else if the file type is ".zip" or ".tgz" it runs a subproces to match the tree structure of the uploaded file with the one provided by the teacher for that particular assignment.
    It then updates the feedback and status of the student's submission.
    If the specified file type is ".sh" it spawns a subprocess to evaluate the submission and the marks, status and feedback gets updated automatically for each submission.\n
    It requires the user with identity as student only to make a submission.
    It redirects the unauthorized users to the login page.

    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :param num1: id of the course
    :type num1: int
    :param num2: id of the assignment
    :type num2: int
    :return: returns the request to render the corresponding html pages
    """

 current_user = request.user
 if current_user.id != None:
    msg = ""
    msg2 = ""
    msg3 = ""
    if request.method == 'POST':
        
        submitted_form = solution(request.POST, request.FILES)
        if submitted_form.is_valid():
            doc = request.FILES
            doc_name = doc["assignment"]
            x = courses.objects.get(id = num1)
            z = x.assignments.get(id = num2).upload_type
            k = x.assignments.get(id = num2).Treestructure
            #print(doc_name)
            
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
                    studentsubmissions.objects.filter(id = s.id).update(status = "late submission")
                else:
                    studentsubmissions.objects.filter(id = s.id).update(status = "successfully submitted")
                # 20221121111714 check
                # 20221121113337 try1
                x.save()
                if str(z)!=".cpp" and str(z)!=".py" and str(z)!=".sh":
                    try:
                        zipf = studentsubmissions.objects.get(id = s.id).solution
                        autograder = x.assignments.get(id = num2).autograder
                        tree = x.assignments.get(id = num2).Treestructure
                        if str(z) ==".zip":
                            command1 = f"unzip media/{zipf} -d ./submissions/"
                        elif str(z) ==".tgz":
                            command1 = f"tar -xvzf media/{zipf} -C ./submissions/"
                        name = doc_name.name[:-4]
                        # print(name, command1)
                        p1 = subprocess.run(command1, capture_output=True, shell=True)
                        command2 = "cd submissions/;ls"
                        p2 = subprocess.run(command2, capture_output=True, shell=True)
                        dirname = p2.stdout.decode().strip("\n")
                        print("start")
                        print( dirname)
                        print("end")
                        command3 = "cd submissions/; tree -a "+dirname
                        print(dirname, command3, sep=", ")
                        p3 = subprocess.run(command3, capture_output=True, shell=True)
                        m = p3.stdout.decode()
                        f = open("t.txt", 'w')
                        f.write(m)
                        f.close()
                        command4 = "diff t.txt media/"+str(tree)
                        p3 = subprocess.run(command4, capture_output=True, shell=True)
                        output = p3.stdout.decode()
                        print(output, str(tree))
                        if output != "":
                            msg = "tree structure not matching , check again"
                            studentsubmissions.objects.filter(id = s.id).update(marks = 0)
                            studentsubmissions.objects.filter(id = s.id).update(feedback = msg)
                        else:
                            msg = "tree structure matched"
                            studentsubmissions.objects.filter(id = s.id).update(marks = 5)
                            studentsubmissions.objects.filter(id = s.id).update(feedback = msg)
                        
                        finalcommand = "rm -r submissions"
                        subprocess.run(finalcommand, capture_output=True, shell=True)
                    except:
                        studentsubmissions.objects.filter(id = s.id).update(marks = 0)
                        studentsubmissions.objects.filter(id = s.id).update(status = "ERROR")
                        studentsubmissions.objects.filter(id = s.id).update(feedback = "wrong submission")
                        subprocess.run("rm -r submissions", shell=True)   
                # unzip autograder
                elif str(z)==".sh":
                    try:
                        autog = courses.objects.get(id = num1).assignments.get(id = num2).autograder  
                        st_soln = studentsubmissions.objects.get(id = s.id).solution            
                        command1 = f"unzip media/{autog} -d auto_grader"
                        p1 = subprocess.run(command1, capture_output=True, shell=True)
                        print(autog)
                        command2 = "cd auto_grader/; ls"
                        p2 = subprocess.run(command2, capture_output=True, shell=True)
                        print1 = p2.stdout.decode()
                        name = print1.strip("\n")
                        print(name, "-----")
                        # command3 = "ls"
                        command3 = "cp ."+ st_soln.url + " ./auto_grader/"+name+"/decode.sh"
                        command4 = "cd auto_grader/" + name + "/;chmod +x auto_eval_*.sh; ./auto_eval_*.sh decode.sh;" 
                        p3 = subprocess.run(command3, capture_output=True, shell=True)
                        print(command3, command4, sep="\n") 
                        p3 = subprocess.run(command4, capture_output=True, shell=True)
                        # p2 = subprocess.run(command2, capture_output=True, shell=True)
                        out = p3.stdout.decode()
                        print(out)

                        lines = out.splitlines()
                        st_marks = int(lines[len(lines)-3][14:])
                        print(st_marks, type(st_marks))
                        st_status = lines[len(lines)-2]
                        st_feedback = lines[len(lines)-1]

                        studentsubmissions.objects.filter(id = s.id).update(marks = st_marks)
                        studentsubmissions.objects.filter(id = s.id).update(status = st_status)
                        studentsubmissions.objects.filter(id = s.id).update(feedback = st_feedback)

                        finalcommand = f"cd auto_grader/;rm -r {name}"
                        subprocess.run(finalcommand, capture_output=True, shell=True)   
                    except:
                        studentsubmissions.objects.filter(id = s.id).update(marks = 0)
                        studentsubmissions.objects.filter(id = s.id).update(status = "ERROR")
                        studentsubmissions.objects.filter(id = s.id).update(feedback = "code failed") 
                        subprocess.run("rm -r auto_grader/", shell=True)          
                    

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
            "msg2":msg2,
            "msg3": msg3
		} 
    return render(request, 'users/sol.html', context)
 else:
    return HttpResponseRedirect("/login/") 

def all_submissions(request, num1, num2):
 """
 This view shows the teacher all the latest submissions made to the particular assignment by every student.\n
 It searches for all the submissions made to that assignment and maintains a dictionary of the users and their corresponding latest submissions by checking for the upload time
 and date of the solution and sends this list by passing it as a context to render request so that the uploaded file, marks and other details can be displayed on the html page.\n
 It is also able to take in data from feedback form (defined in forms.py) so that the teacher has the ability to individually update the marks of every assignment.\n
 This view also allows the teacher to download all the submission made by students in a single zip folder.\n
 If the user is a student it simply redirects it to his home page.

 :param request: HttpRequest object which contains the metadata about the request
 :type request: HttpRequest
 :param num1: id of the course to which the assignment belongs
 :type num1: int
 :param num2: id of the assignment which we are interested in
 :type num2: int
 :return: returns the request to render the corresponding html pages
 """
 current_user = request.user
 if current_user.id != None:
  
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
        print(d[i].created_at, d[i].created_at )

    if request.method == 'POST':
        if request.POST.get('form_id',False) == 'feed':
            form = feedback_form(request.POST)
            print(4)
            if form.is_valid():
                print(5)
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
                    "form":empty_form,
                    "assign":x.assignments.get(id = num2),
                }
                return render(request, 'users/submissions.html',context)
        elif(request.POST.get('form_id',False) == 'download'):
            print(7)
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
        "assign": x.assignments.get(id = num2),
        "form": form
    }
    return render(request, 'users/submissions.html', context)
 else:
    
    return HttpResponseRedirect("/login/") 

def export_to_csv(reuest, num1, num2):
 """
    This view is used to get all the marks and feedback of each student in a CSV file in a specific format.\n
    It writes the students detail, name of file it uploaded, current marks and current feedback in the CSV file, for each submission made till the time.\n
    It then downloads that CSV file.\n

    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :param num1: id of the course
    :type num1: int
    :param num2: id of the assignment
    :type num2: int
    :return: returns the request to render the corresponding html pages
 """
 current_user = reuest.user
 if current_user.id != None:
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
 else:
    
    return HttpResponseRedirect("/login/") 

def marks( request, num1, num2):
 """
    This view is used to update marks and feedback of all students through a csv file.\n
    It first requires the user with identity as teacher to upload a csv file with a specific format.\n
    It then reads the file and updates the marks and feedback for the latest solutions uploaded by the students till the time.\n
    It redirects the unauthorized users to the login page

    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :param num1: id of the course
    :type num1: int
    :param num2: id of the assignment
    :type num2: int
    :return: returns the request to render the corresponding html pages
 """
 current_user = request.user
 if current_user.id != None:
 
    if request.method == 'POST':
        msg = ""
        submitted_form = csv_form(request.POST, request.FILES)
        if submitted_form.is_valid():
            csv_file = submitted_form.cleaned_data['csv_file']
            if not csv_file.name.endswith('.csv'):
                msg =  'File is not CSV type'
            else:
             try:
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
                msg = "Marks and feedback are successfully added"
             except:
                msg = "Check the coloumns and rows properly, download the csv file of the submissions and then update marks and feedback in that and upload."
            context = {

                "msg": msg

            }
            return render(request, 'users/marks.html', context)
                                    
    submitted_form = csv_form()
    context = {
			"form": submitted_form,
		}
    return render(request, 'users/marks.html', context)
 else:
    
    return HttpResponseRedirect("/login/") 


def deregister_view(request, num, uid):
 """
    This view is used to deregister students enrolled in a course by the teacher of that course.\n
    It simply removes the link of a selected student with the specific course for which that view is called.\n
    It then renders the home page of teacher.

    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :param num: id of the course
    :type num: int
    :param uid: id of the user getting deregistered
    :type uid: int
    :return: returns the request to render the corresponding html pages
 """
 current_user = request.user
 if current_user.id != None:
    users = UserProfile.objects.get(id = uid)
    cc = users.courses_registered.get(id = num)
    courses_reg = users.courses_registered.remove(cc.id)
    m.success(request, f'Successfully Deregistered {users.user_name} from this course.')
    return HttpResponseRedirect(f"/{num}/") 
 else:
    return HttpResponseRedirect("/login/") 

def logout_view(request):
    """
    This view is used to logout the user from the portal.\n
    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    """
    logout(request)
    return HttpResponseRedirect("/login/")  
def sendmsg(request, num1, num2):
    """
    This view send message from teacher to the student with id = num2, which contains the code to register for the course with id = num1.\n
    :param num1: id of the course 
    :type num1: int
    :param num2: id of the student 
    :type num1: int

    """
    users = UserProfile.objects.get(id = num2)
    course = courses.objects.get(id = num1)
    c = course.code
    t = course.title
    p = course.prof
    msg2 = f"Register for the Course {t} using code {c}"
    newmsg = messages(msg = msg2, prof = p )
    newmsg.save()
    users.messages.add(newmsg)
    users.save()
    m.success(request, f'Message is successfully sent to {users.user_name}.')
    return HttpResponseRedirect(f"/{num1}/")

def sendmsgall(request, num1):
    """
    This view send message from teacher to all the unregistered students, which contains the code to register for the course with id = num1.\n
    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :param num1: id of the course 
    :type num1: int
    
    """
    users = UserProfile.objects.all()
    course = courses.objects.get(id = num1)
    c = course.code
    t = course.title
    p = course.prof
    msg2 = f"Register for the Course {t} using code {c}"
    for user in users:
        if user.identity == "student":
            k = 0
            course = user.courses_registered.all()
            print(course)
            for c in course:
                if c.id == num1:
                    k = 1
            if k == 0:
                newmsg = messages(msg = msg2, prof = p )
                newmsg.save()
                user.messages.add(newmsg)
                user.save()
    m.success(request, f'Message is successfully sent to all unregistered students.')
    return HttpResponseRedirect(f"/{num1}/")
 
def delete(request):
    """
    This view is used to clean all the messages user recieved till now.\n
    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    """
    user = UserProfile.objects.get(user_name = request.user.username)
    user.messages.clear()
    user.save()
    return HttpResponseRedirect("/")


def reg_student(request,num):
    """
    This view is used by teachers to register new students to their course with the help of student's user name and roll number similar to how we are automatically enrolled for courses on moodle.\n
    It works by searching if a student with these user name and roll number exist in the database.\n
    If such student does not exist it will simply ask to refill the form.\n
    But if such student does exist then it searches whether this student has already been enrolled to this course or not.\n
    If no, then it just adds the student to this course.

    :param request: HttpRequest object which contains the metadata about the request
    :type request: HttpRequest
    :return: returns the request to render the corresponding html pages
    """

    msg = ""
    current_user = request.user
    if current_user.id!=None:
        if request.method == 'POST':
            # print(6)
            uform = register_student_for_course(request.POST)
            if uform.is_valid() :
                # print(7)
                stud_name  = uform.cleaned_data["user_name"]
                stud_roll = uform.cleaned_data["roll_no"]
                users = UserProfile.objects.all()
                x = False
                for user in users:
                    # print(8)
                    if(user.user_name == stud_name and user.roll_no == stud_roll):
                        # print(9)
                        x = True
                        break
                if x == False:
                    
                    msg = "Student with this name and roll number does not exist"
                    form = register_student_for_course()
                    context = {"form": form,
                        "msg":msg,}
                    return render(request, 'users/add_to_course.html',context)
                else:
                    
                    U = UserProfile.objects.get(roll_no = stud_roll)
                    stud_courses = U.courses_registered.all()
                    y = False
                    # print(type(stud_courses[0]))
                    # print(type(num))
                    for c in  stud_courses:
                        if c.id == num:
                            y = True
                            break
                    if y == True:
                        # print(12)
                        msg = "Student already enrolled for the course"
                        form = register_student_for_course()
                        context = {"form": form,
                        "msg":msg,}
                        return render(request, 'users/add_to_course.html',context)
                    else:
                        # print(13)
                        U.courses_registered.add(num)
                        U.save()
                        msg = "Student successfully registered"
                        form = register_student_for_course()
                        context = {"form": form,
                        "msg":msg,}
                        return redirect(f"http://127.0.0.1:8000/{num}/")
            
    # print(14)
        form = register_student_for_course()
        context = {"form": form,
                    "msg":msg,}
        return render(request, 'users/add_to_course.html',context)

    else:
        return redirect("http://127.0.0.1:8000/login")





    


