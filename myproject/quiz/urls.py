# urls.py
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

    # Custom Quiz Detail View (with optional question_id)
    path('custom-quiz-detail/', views.custom_quiz_detail,
         name='custom_quiz_detail'),
    path('custom-quiz-detail/<int:question_id>/',
         views.custom_quiz_detail, name='custom_quiz_detail'),

    # Quiz Result
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),

    # Custom Quiz Result (no quiz_id needed)
    # New URL for custom quiz results
    path('custom-quiz-result/', views.quiz_result, name='custom_quiz_result'),

    # Detailed Explanation view with string-based question_id
    path('explanation/<str:question_id>/',
         views.detailed_explanation, name='detailed_explanation'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
