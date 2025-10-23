from django.urls import path
from .views_api import SectionList, SubjectListBySection, QuestionListBySubject

urlpatterns = [
    path('sections/<str:exam_type>/', SectionList.as_view(), name='sections-list'),
    path('sections/<int:section_id>/subjects/', SubjectListBySection.as_view(), name='subject-list-by-section'),
    path('questions/subject/<int:subject_id>/', QuestionListBySubject.as_view(), name='questions-by-subject'),
]