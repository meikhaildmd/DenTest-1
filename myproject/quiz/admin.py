from django.contrib import admin
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
    list_display = ("name", "exam_type")
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
    list_display = ("question_id", "text", "subject", "correct_option")
    search_fields = ("text", "question_id")
    list_filter = ("subject__section__exam_type", "subject__section", "subject")
    ordering = ("subject__section__name", "subject__name")
    inlines = [QuestionImageInline]
    fieldsets = (
        (None, {
            "fields": (
                "question_id",
                "subject",
                "text",
                ("option1", "option2"),
                ("option3", "option4"),
                "correct_option",
                "explanation",
                "explanation_image",
            )
        }),
    )

# ─── Patient chart admin ───────────────────────────────────────────────
@admin.register(PatientChartData)
class PatientChartDataAdmin(admin.ModelAdmin):
    list_display = ("question", "chief_complaint")
    search_fields = ("question__text", "chief_complaint")
    fields = (
        "question",
        "patient_details",
        "chief_complaint",
        "medical_history",
        "current_findings",
    )

# ─── Custom quiz admin ─────────────────────────────────────────────────
@admin.register(CustomQuiz)
class CustomQuizAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at")
    inlines = [CustomQuizQuestionInline]
    search_fields = ("title", "user__username")

# ─── Simple registrations ─────────────────────────────────────────────
admin.site.register(QuizAttempt)
admin.site.register(UserQuestionStatus)