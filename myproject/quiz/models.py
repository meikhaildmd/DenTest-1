from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now
import uuid
import os


# Function to randomize image file names
def get_image_filename(instance, filename):
    ext = filename.split('.')[-1]
    return f'{uuid.uuid4()}.{ext}'


# User Profile Model for subscription management
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_type = models.CharField(
        max_length=100, choices=[('free', 'Free'), ('premium', 'Premium')]
    )
    subscription_start = models.DateTimeField(default=now)
    subscription_end = models.DateTimeField(
        null=True, blank=True)  # Can store expiration date

    def is_active_subscription(self):
        if self.subscription_end:
            return now() < self.subscription_end
        return False

    def __str__(self):
        return f"{self.user.username} - {self.subscription_type} Subscription"


# Classification Model
class Classification(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Classification"
        verbose_name_plural = "Classifications"
        ordering = ['name']


# Subject Model
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


# Quiz Model
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


# Detailed Explanation Model for storing long explanations
class DetailedExplanation(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()  # This will store the long explanation (can be Markdown)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f"/explanations/{self.id}/"


class Question(models.Model):
    question_id = models.CharField(max_length=100, unique=True)
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

    # Short explanation and link for "read more"
    explanation = models.TextField(blank=True, null=True)
    detailed_explanation = models.ForeignKey(
        'DetailedExplanation', null=True, blank=True, on_delete=models.SET_NULL)
    read_more_link = models.URLField(blank=True, null=True)

    # Explanation image field
    explanation_image = models.ImageField(
        upload_to='explanation_image/', blank=True, null=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['quiz']


# Question Image Model
class QuestionImage(models.Model):
    question = models.ForeignKey(
        Question, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_image_filename)

    def __str__(self):
        return f"Image for {self.question.text}"


# Patient Chart Data Model
class PatientChartData(models.Model):
    question = models.OneToOneField(
        Question, related_name='chart_data', on_delete=models.CASCADE)
    patient_details = models.CharField(
        max_length=255, null=True, blank=True)  # For sex and age
    chief_complaint = models.TextField()
    medical_history = models.TextField()  # This will now include medications
    current_findings = models.TextField()

    def __str__(self):
        return f"Chart for {self.question.text}"


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    completed_at = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(null=True, blank=True)
    answered_questions = models.ManyToManyField(Question, blank=True)

    def track_question_progress(self, question, is_correct):
        """Track the progress of each question in the quiz attempt."""
        if not self.answered_questions.filter(id=question.id).exists():
            self.answered_questions.add(question)
            if is_correct:
                self.score += 1
            self.save()

            # Track subject score by subject
            quiz_subject = question.quiz.subject
            attempt_subject, created = QuizAttemptSubject.objects.get_or_create(
                quiz_attempt=self, subject=quiz_subject
            )
            attempt_subject.total_questions += 1
            if is_correct:
                attempt_subject.score += 1
            attempt_subject.save()

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} - {self.score}"


# Quiz Attempt Subject Model
class QuizAttemptSubject(models.Model):
    quiz_attempt = models.ForeignKey(
        QuizAttempt, related_name='subject_scores', on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject, related_name='quiz_attempts', on_delete=models.CASCADE
    )
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)

    def calculate_percentage(self):
        if self.total_questions > 0:
            return (self.score / self.total_questions) * 100
        return 0

    def __str__(self):
        return f"{self.quiz_attempt} - {self.subject}"


class UserQuestionStatus(models.Model):
    STATUS_CHOICES = [
        ('unanswered', 'Unanswered'),
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='unanswered')

    class Meta:
        # Ensures one status per user per question
        unique_together = ('user', 'question')

    def __str__(self):
        return f"{self.user.username} - {self.question.text[:50]} - {self.status}"
