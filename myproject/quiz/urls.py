from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [
    path('', views.classification_list, name='classification_list'),
    path('classification/<int:classification_id>/',
         views.subject_list, name='subject_list'),
    path('subject/<int:subject_id>/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/question/<int:question_id>/',
         views.quiz_question_detail, name='quiz_question_detail'),
    path('quiz/<int:quiz_id>/result/', views.quiz_result, name='quiz_result'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
