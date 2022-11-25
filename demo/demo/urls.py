
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from users import views as user_views
from . import settings


urlpatterns = [
    path('deregister/<int:num>/user/<int:uid>', user_views.deregister_view),
    path('<int:num1>/<int:num2>', user_views.sendmsg),
    path('<int:num1>/all', user_views.sendmsgall),
    path('seeassignments/<int:num1>/<int:num2>/feedback', user_views.export_to_csv),
    path('seeassignments/<int:num1>/<int:num2>/marks', user_views.marks),
    path('seeassignments/<int:num1>/s/<int:num2>', user_views.solution_upload ),
    path('seeassignments/<int:num1>/t/<int:num2>', user_views.all_submissions ),
    path('addassignment/<int:num>/', include("users.urls")),
    path('seeassignments/<int:num>/', user_views.assignment_views, name="ass" ),
    path('<int:num>/', user_views.course_page),
    path('allcourses/', user_views.allcourses_views, name = "Userprofile" ),
    path('admin/', admin.site.urls),
    path('', user_views.home, name='home'),
    #path('register/', user_views.register, name='register'),
    path('reg/', user_views.register_user, name = 'reg'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name = 'login'),
    path('logout/', user_views.logout_view, name = 'logout'),
    #path('assignment/', auth_views.LogoutView.as_view(template_name='users/courses.html'), name = 'courses'),
    path('updateprofile/', user_views.update , name = 'update'),
    path('assignment/', include("users.urls")),
    #path('addassignment/', user_views.selectcourse.as_view()),
    path('reg/', user_views.register_user, name = 'reg'),
    path('createcourse/',user_views.createcourse),
    path('delete/', user_views.delete),
    path('addstudent/<int:num>/',user_views.reg_student),
    
]
urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

