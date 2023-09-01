from django.contrib import admin
from django.urls import path
from candidate import views

urlpatterns = [
    path("",views.upload_resume,name="upload_resume"),
    path('resume_report/', views.upload_resume, name='upload_resume'),
]