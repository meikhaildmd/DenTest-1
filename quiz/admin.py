# quiz/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import (
    Section,
    Subject,
    Question,
    QuestionImage,
    PatientChartData,
    QuizAttempt,
    CustomQuiz,
    CustomQuizQuestion,
    UserQuestionStatus,
)

# ════════════════════════════════════════════════════════════════════════
# INLINE MODELS
# ════════════════════════════════════════════════════════════════════════

class QuestionImageInline(admin.TabularInline):
    model = QuestionImage
    extra = 0


class CustomQuizQuestionInline(admin.TabularInline):
    model = CustomQuizQuestion
    extra = 0


# ════════════════════════════════════════════════════════════════════════
# CORE CONTENT ADMINS
# ════════════════════════════════════════════════════════════════════════

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "exam_type")
    list_filter = ("exam_type",)
    search_fields = ("name",)
    ordering = ("id",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "section")
    list_filter = ("section__exam_type", "section")
    search_fields = ("name",)
    ordering = ("section", "id")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "text", "correct_option")
    list_filter = ("subject__section__exam_type", "subject__section", "subject")
    search_fields = ("text",)
    ordering = ("subject__section__name", "subject__name", "id")
    inlines = [QuestionImageInline]


@admin.register(QuestionImage)
class QuestionImageAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "image")
    search_fields = ("question__text",)
    ordering = ("-id",)


@admin.register(PatientChartData)
class PatientChartDataAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "chief_complaint")
    search_fields = ("question__text", "chief_complaint")
    ordering = ("-id",)


# ════════════════════════════════════════════════════════════════════════
# QUIZZES AND ATTEMPTS
# ════════════════════════════════════════════════════════════════════════

@admin.register(CustomQuiz)
class CustomQuizAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at")
    search_fields = ("title", "user__username")
    ordering = ("-created_at",)
    inlines = [CustomQuizQuestionInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "subject", "score")
    search_fields = ("user__username",)
    ordering = ("-id",)


@admin.register(UserQuestionStatus)
class UserQuestionStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question")
    search_fields = ("user__username", "question__text")
    ordering = ("-id",)


# ════════════════════════════════════════════════════════════════════════
# USER ADMIN (OVERRIDE DEFAULT)
# ════════════════════════════════════════════════════════════════════════

User = get_user_model()
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_active", "date_joined")
    list_filter = ("is_active", "date_joined")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)