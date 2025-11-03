from django.urls import path
from .views_api import (
    SectionList,
    SubjectListBySection,
    QuestionListBySubject,
    SectionWithSubjectsView,
    UserQuestionStatusUpdateView,
    UserQuestionStatusBySubjectView,
    LoginView,
    LogoutView,
    get_csrf_token,
    UserProgressView,
    CustomQuizView,
    CurrentUserView,
    SignupView,
)

urlpatterns = [
    path("sections/<str:exam_type>/", SectionList.as_view(), name="section-list"),
    path("sections/<int:section_id>/subjects/", SubjectListBySection.as_view(), name="subject-list"),
    path("questions/subject/<int:subject_id>/", QuestionListBySubject.as_view(), name="questions-by-subject"),
    path("sections/<int:section_id>/with-subjects/", SectionWithSubjectsView.as_view(), name="section-with-subjects"),
    path("user-question-status/update/", UserQuestionStatusUpdateView.as_view(), name="update-question-status"),
    path("user-question-status/subject/<int:subject_id>/", UserQuestionStatusBySubjectView.as_view(), name="user-question-status-by-subject"),
    path("login/", LoginView.as_view(), name="login"),
    path("csrf/", get_csrf_token, name="get-csrf"),
    path('user-progress/', UserProgressView.as_view(), name='user-progress'),
    path("custom-quiz/", CustomQuizView.as_view(), name="custom-quiz"),
    path("current-user/", CurrentUserView.as_view(), name="current-user"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("user-question-status/all/", api_views.UserQuestionStatusAllView.as_view(), name="user_question_status_all"),
]