from django.contrib import admin

# Register your models here.
from .models import assignments,courses

admin.site.register(assignments)
admin.site.register(courses)