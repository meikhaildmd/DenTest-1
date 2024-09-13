from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    # Classification List (Home Page)
    path('', views.classification_list, name='classification_list'),

    # Subjects under Classification
    path('classification/<int:classification_id>/',
         views.subject_list, name='subject_list'),

    # Quizzes under Subject
    path('subject/<int:subject_id>/', views.quiz_list, name='quiz_list'),

    # Regular Quiz Detail (with optional question_id)
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/question/<int:question_id>/',
         views.quiz_detail, name='quiz_detail'),

    # Custom Quiz Creation
    path('custom-quiz/', views.create_custom_quiz, name='create_custom_quiz'),

    # Quiz Result
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
