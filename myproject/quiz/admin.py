from django.contrib import admin
from .models import Classification, Subject, Quiz, Question, QuestionImage, QuizAttempt
from .models import PatientChartData


class QuestionImageInline(admin.TabularInline):
    model = QuestionImage


@admin.register(PatientChartData)
class PatientChartDataAdmin(admin.ModelAdmin):
    list_display = ('question', 'chief_complaint')
    search_fields = ('question__text', 'chief_complaint')
    fields = ('question', 'patient_details', 'chief_complaint',
              'medical_history', 'current_findings')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'text', 'quiz', 'correct_option')
    search_fields = ('text',)
    list_filter = ('quiz', 'quiz__subject')
    ordering = ('quiz', 'quiz__subject')
    inlines = [QuestionImageInline]
    fields = ['question_id', 'quiz', 'text', 'option1', 'option2', 'option3', 'option4', 'correct_option',
              'explanation', 'explanation_image',]


admin.site.register(Classification)
admin.site.register(Subject)
admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizAttempt)
