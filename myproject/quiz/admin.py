from django.contrib import admin
from .models import Classification, Subject, Quiz, Question, QuestionImage, QuestionChart, QuizAttempt


class QuestionImageInline(admin.TabularInline):
    model = QuestionImage


class QuestionChartInline(admin.TabularInline):
    model = QuestionChart


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'correct_option')
    search_fields = ('text',)
    list_filter = ('quiz',)
    ordering = ('quiz',)
    inlines = [QuestionImageInline, QuestionChartInline]


admin.site.register(Classification)
admin.site.register(Subject)
admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizAttempt)
