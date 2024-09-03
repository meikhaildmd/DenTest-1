from django.contrib.auth.models import User
from django.db import models


class Classification(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"
        ordering = ['name']


class Subject(models.Model):
    classification = models.ForeignKey(
        Classification, related_name='subjects', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['name']


class Quiz(models.Model):
    subject = models.ForeignKey(
        Subject, related_name='quizzes', on_delete=models.CASCADE, default=1)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Quiz"
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    option1 = models.CharField(max_length=100)
    option2 = models.CharField(max_length=100)
    option3 = models.CharField(max_length=100)
    option4 = models.CharField(max_length=100)
    CORRECT_OPTION_CHOICES = [
        ('option1', 'Option 1'),
        ('option2', 'Option 2'),
        ('option3', 'Option 3'),
        ('option4', 'Option 4'),
    ]
    correct_option = models.CharField(
        max_length=100, choices=CORRECT_OPTION_CHOICES)
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['quiz']


class QuestionImage(models.Model):
    question = models.ForeignKey(
        Question, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='question_images/')

    def __str__(self):
        return f"Image for {self.question.text}"


class QuestionChart(models.Model):
    question = models.ForeignKey(
        Question, related_name='charts', on_delete=models.CASCADE)
    chart = models.ImageField(upload_to='question_charts/')

    def __str__(self):
        return f"Chart for {self.question.text}"


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(null=True, blank=True)
    answered_questions = models.ManyToManyField(Question, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}"

    class Meta:
        verbose_name = "Quiz Attempt"
        verbose_name_plural = "Quiz Attempts"
        ordering = ['-completed_at']
        unique_together = ('quiz', 'user', 'completed_at')
