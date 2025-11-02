from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import re
import unicodedata
from django.db.models import UniqueConstraint

# 1. Section model — perfect as is.
class Section(models.Model):
    class ExamType(models.TextChoices):
        INBDE = "inbde", "INBDE"
        ADAT = "adat", "ADAT"

    name = models.CharField(max_length=100)
    exam_type = models.CharField(
        max_length=10,
        choices=ExamType.choices,
        default=ExamType.INBDE
    )

    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        ordering = ["name"]

    def __str__(self):
        return f"{self.exam_type.upper()} – {self.name}"


# 2. Subject model — FIXED version
class Subject(models.Model):
    section = models.ForeignKey(  # ⬅ changed from "sections" to "section"
        Section, related_name="subjects", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ["section__name", "name"]  # ⬅ now this matches the FK name

    def __str__(self):
        return f"{self.section} – {self.name}"  # ⬅ changed to match new FK name

def normalize_for_key(s: str) -> str:
    """Robust normalization for deduping:
    - Unicode normalize (NFKC)
    - lowercase
    - collapse whitespace
    - strip trailing punctuation/zero-width chars
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"[\.!\?:;,\u200b]+$", "", s)
    return s

class Question(models.Model):
    # Human-friendly code (keep for display/search), not the dedupe key
    question_id = models.CharField(max_length=300
    , blank=True, null=True)

    subject = models.ForeignKey(
        "Subject", related_name="questions", on_delete=models.CASCADE
    )

    text = models.TextField()
    # New: normalized text key used for uniqueness within a subject
    normalized_text_key = models.CharField(
        max_length=500, editable=False, db_index=True, default=""
    )

    option1 = models.CharField(max_length=250)
    option2 = models.CharField(max_length=250)
    option3 = models.CharField(max_length=250)
    option4 = models.CharField(max_length=250)

    CORRECT_OPTION_CHOICES = [
        ("option1", _("Option 1")),
        ("option2", _("Option 2")),
        ("option3", _("Option 3")),
        ("option4", _("Option 4")),
    ]
    correct_option = models.CharField(max_length=100, choices=CORRECT_OPTION_CHOICES)

    explanation = models.TextField(blank=True, null=True)
    question_image = models.ImageField(
        upload_to="question_images/", blank=True, null=True
    )
    question_image_url = models.URLField(blank=True, null=True)
    explanation_image = models.ImageField(
        upload_to="explanation_image/", blank=True, null=True
    )

    def save(self, *args, **kwargs):
        self.normalized_text_key = normalize_for_key(self.text)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text

    class Meta:
        constraints = [
            # Enforce: no duplicate (by normalized text) inside the same subject
            UniqueConstraint(
                fields=["subject", "normalized_text_key"], name="uq_subject_normtext"
            )
        ]
# 4. QuestionImage
def get_image_filename(instance, filename):
    return f"question_image/{instance.question.question_id}_{filename}"


class QuestionImage(models.Model):
    question = models.ForeignKey(
        Question, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=get_image_filename)

    def __str__(self):
        return f"Image for {self.question.text}"


# 5. PatientChartData
class PatientChartData(models.Model):
    question = models.OneToOneField(
        Question, related_name="chart_data", on_delete=models.CASCADE
    )
    patient_details = models.CharField(max_length=255, null=True, blank=True)
    chief_complaint = models.TextField()
    medical_history = models.TextField()
    current_findings = models.TextField()

    def __str__(self):
        return f"Chart for {self.question.text}"


# 6. UserProfile
class UserProfile(models.Model):
    class SubscriptionType(models.TextChoices):
        FREE = "free", "Free"
        PREMIUM = "premium", "Premium"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="profile",
        on_delete=models.CASCADE,
    )
    subscription_type = models.CharField(
        max_length=20, choices=SubscriptionType.choices, default=SubscriptionType.FREE
    )
    subscription_start = models.DateTimeField(default=timezone.now)
    subscription_end = models.DateTimeField(null=True, blank=True)

    @property
    def is_active_subscription(self):
        if self.subscription_type == self.SubscriptionType.FREE:
            return True
        return self.subscription_end is None or timezone.now() < self.subscription_end

    def __str__(self):
        return f"{self.user.username} ({self.subscription_type})"


# 7. QuizAttempt
class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="attempts", on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject, related_name="attempts", on_delete=models.CASCADE
    )
    score = models.DecimalField(max_digits=5, decimal_places=2)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user.username} – {self.subject.name} – {self.score}"


class UserQuestionStatus(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="question_statuses",
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(
        Question, related_name="user_statuses", on_delete=models.CASCADE
    )

    times_seen = models.PositiveIntegerField(default=0)
    times_correct = models.PositiveIntegerField(default=0)
    last_answer = models.CharField(max_length=100, blank=True)
    last_was_correct = models.BooleanField(default=False)  # ✅ NEW FIELD
    last_seen_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "question")]

    def record_attempt(self, chosen_option: str, correct: bool):
        self.times_seen += 1
        if correct:
            self.times_correct += 1
        self.last_answer = chosen_option
        self.last_was_correct = correct  # ✅ NEW LINE
        self.save(
            update_fields=[
                "times_seen",
                "times_correct",
                "last_answer",
                "last_was_correct",  # ✅ NEW FIELD
                "last_seen_at",
            ]
        )

    def __str__(self):
        return f"{self.user.username} ↔ {self.question.question_id}"
    
# 9. CustomQuiz
class CustomQuiz(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="custom_quizzes",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    questions = models.ManyToManyField(
        Question, through="CustomQuizQuestion", related_name="custom_quizzes"
    )

    def __str__(self):
        return f"{self.user.username} – {self.title}"


class CustomQuizQuestion(models.Model):
    custom_quiz = models.ForeignKey(CustomQuiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        unique_together = [("custom_quiz", "question")]

    def __str__(self):
        return f"{self.custom_quiz.title} ↔ {self.question.question_id}"
    
