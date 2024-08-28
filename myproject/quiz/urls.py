from django.urls import path
from . import views

urlpatterns = [
    path('', views.quiz_home, name='quiz_home'),  # Main quiz page
    path('practice_quiz/', views.practice_quiz, name='practice_quiz'),
]
