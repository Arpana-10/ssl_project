
from django.urls import path
from django.conf import settings
from django.views.static import serve

from . import views

urlpatterns = [
    path("upload/", views.UploadView.as_view()),
    path("download/", serve, {'document_root': settings.MEDIA_ROOT}),
    path("courses/", views.createassignment.as_view()),
    path("index",views.index,name="index"),
    path("index1",views.index1,name="index1"),
]