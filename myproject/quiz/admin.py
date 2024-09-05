from django.contrib import admin
from .models import Classification, Subject, Quiz, Question, QuestionImage, QuizAttempt
from .models import PatientChartData


class QuestionImageInline(admin.TabularInline):
    model = QuestionImage


@admin.register(PatientChartData)
class PatientChartDataAdmin(admin.ModelAdmin):
    list_display = ('question', 'chief_complaint')
    search_fields = ('question__text', 'chief_complaint')
    fields = ('question', 'chief_complaint', 'medications',
              'medical_history', 'current_findings')


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'correct_option')
    search_fields = ('text',)
    list_filter = ('quiz',)
    ordering = ('quiz',)
    inlines = [QuestionImageInline]


admin.site.register(Classification)
admin.site.register(Subject)
admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizAttempt)
