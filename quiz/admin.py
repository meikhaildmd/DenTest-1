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
    verbose_name = "Attached Image"
    verbose_name_plural = "Question Images"


class CustomQuizQuestionInline(admin.TabularInline):
    model = CustomQuizQuestion
    extra = 0
    verbose_name_plural = "Included Questions"


# ════════════════════════════════════════════════════════════════════════
# CORE CONTENT ADMINS
# ════════════════════════════════════════════════════════════════════════

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "exam_type")
    list_filter = ("exam_type",)
    search_fields = ("name",)
    ordering = ("exam_type", "name")
    list_per_page = 25


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "section", "exam_type_display")
    list_filter = ("section__exam_type", "section")
    search_fields = ("name",)
    ordering = ("section", "id")
    list_per_page = 25

    def exam_type_display(self, obj):
        return obj.section.exam_type
    exam_type_display.short_description = "Exam Type"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "short_text", "subject", "correct_option", "has_explanation")
    list_filter = ("subject__section__exam_type", "subject__section", "subject")
    search_fields = ("text",)
    ordering = ("subject__section__name", "subject__name", "id")
    inlines = [QuestionImageInline]
    list_per_page = 20

    def short_text(self, obj):
        return (obj.text[:80] + "...") if len(obj.text) > 80 else obj.text
    short_text.short_description = "Question"

    def has_explanation(self, obj):
        return bool(obj.explanation)
    has_explanation.boolean = True
    has_explanation.short_description = "Explanation?"


@admin.register(PatientChartData)
class PatientChartDataAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "chief_complaint")
    search_fields = ("question__text", "chief_complaint")
    ordering = ("-id",)
    list_per_page = 25


# ════════════════════════════════════════════════════════════════════════
# QUIZZES AND ATTEMPTS
# ════════════════════════════════════════════════════════════════════════

@admin.register(CustomQuiz)
class CustomQuizAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "created_at", "num_questions")
    search_fields = ("title", "user__username")
    ordering = ("-created_at",)
    inlines = [CustomQuizQuestionInline]
    list_per_page = 25

    def num_questions(self, obj):
        return obj.customquizquestion_set.count()
    num_questions.short_description = "Questions"


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "subject", "score")
    search_fields = ("user__username",)
    ordering = ("-id",)
    list_per_page = 25


@admin.register(UserQuestionStatus)
class UserQuestionStatusAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "question", "status_display")
    search_fields = ("user__username", "question__text")
    ordering = ("-id",)
    list_per_page = 25

    def status_display(self, obj):
        if obj.last_was_correct is True:
            return "✅ Correct"
        elif obj.last_was_correct is False:
            return "❌ Incorrect"
        return "–"
    status_display.short_description = "Last Attempt"


# ════════════════════════════════════════════════════════════════════════
# USER ADMIN (SIMPLIFIED)
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
    list_per_page = 25