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

# ─── Inlines ───────────────────────────────────────────────────────────
class QuestionImageInline(admin.TabularInline):
    model = QuestionImage
    extra = 0


class CustomQuizQuestionInline(admin.TabularInline):
    model = CustomQuizQuestion
    extra = 0


# ─── Section admin ─────────────────────────────────────────────────────
@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "exam_type")
    list_filter = ("exam_type",)
    search_fields = ("name",)


# ─── Subject admin ─────────────────────────────────────────────────────
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "section")
    list_filter = ("section__exam_type", "section")
    search_fields = ("name",)


# ─── Question admin ────────────────────────────────────────────────────
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "subject", "correct_option")
    search_fields = ("text",)
    list_filter = ("subject__section__exam_type", "subject__section", "subject")
    ordering = ("subject__section__name", "subject__name")
    inlines = [QuestionImageInline]


@admin.register(QuestionImage)
class QuestionImageAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "image")
    search_fields = ("question__text",)
    ordering = ("-id",)


# ─── Patient chart admin ───────────────────────────────────────────────
@admin.register(PatientChartData)
class PatientChartDataAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "chief_complaint")
    search_fields = ("question__text", "chief_complaint")


# ─── Custom quiz admin ─────────────────────────────────────────────────
@admin.register(CustomQuiz)
class CustomQuizAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at")
    inlines = [CustomQuizQuestionInline]
    search_fields = ("title", "user__username")


# ─── Quiz attempt admin ────────────────────────────────────────────────
@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "subject", "score")
    search_fields = ("user__username",)
    ordering = ("id",)


# ─── User question status admin ────────────────────────────────────────
@admin.register(UserQuestionStatus)
class UserQuestionStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question")
    search_fields = ("user__username", "question__text")
    ordering = ("id",)


# ─── User admin (simple view for new accounts) ─────────────────────────
User = get_user_model()
admin.site.unregister(User)  # remove Django’s default registration if active

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "is_active", "date_joined")
    list_filter = ("is_active", "date_joined")
    search_fields = ("username", "email")
    ordering = ("-date_joined",)