from .models import Quiz, Question, QuizAttempt, PatientChartData, Classification, Subject, QuizAttemptSubject
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
# Assuming you'll create a form for custom quizzes
from .forms import CustomQuizForm


@login_required
def classification_list(request):
    classifications = Classification.objects.all()
    subject_progress = {}

    for classification in classifications:
        for subject in classification.subjects.all():
            subject_attempts = QuizAttemptSubject.objects.filter(
                subject=subject,
                quiz_attempt__user=request.user
            )

            avg_score = subject_attempts.aggregate(Avg('score'))['score__avg']
            total_questions = subject_attempts.aggregate(Avg('total_questions'))[
                'total_questions__avg']

            if avg_score and total_questions:
                avg_percentage = (avg_score / total_questions) * 100
            else:
                avg_percentage = None

            subject_progress[subject.name] = avg_percentage

    return render(request, 'quiz/classification_list.html', {
        'classifications': classifications,
        'subject_progress': subject_progress
    })


@login_required
def subject_list(request, classification_id):
    classification = get_object_or_404(Classification, id=classification_id)
    subjects = classification.subjects.all()
    return render(request, 'quiz/subject_list.html', {'classification': classification, 'subjects': subjects})


@login_required
def quiz_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    quizzes = subject.quizzes.all()
    return render(request, 'quiz/quiz_list.html', {'subject': subject, 'quizzes': quizzes})


@login_required
def create_custom_quiz(request):
    if request.method == 'POST':
        form = CustomQuizForm(request.POST)
        if form.is_valid():
            selected_subjects = form.cleaned_data['subjects']
            number_of_questions = form.cleaned_data['number_of_questions']
            questions = Question.objects.filter(
                quiz__subject__in=selected_subjects).order_by('?')[:number_of_questions]

            # Create a new quiz (custom, no subject or title required)
            quiz = Quiz.objects.create(
                title="Custom Quiz", description="Custom-selected quiz")

            for question in questions:
                question.quiz = quiz
                question.save()

            return redirect('quiz_detail', quiz_id=quiz.id)

    else:
        form = CustomQuizForm()

    return render(request, 'quiz/create_custom_quiz.html', {'form': form})


@login_required
def quiz_detail(request, quiz_id, question_id=None):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.all())
    question = questions[0] if question_id is None else get_object_or_404(
        Question, id=question_id)

    explanation = None
    is_correct = None
    selected_option = None
    answered = False
    next_question = None
    chart_data = None

    # Fetch or create a QuizAttempt
    with transaction.atomic():
        quiz_attempt, created = QuizAttempt.objects.get_or_create(
            quiz=quiz, user=request.user, completed_at__isnull=True,
            defaults={'score': 0}
        )

    # Check if this question is already answered
    answered_questions = quiz_attempt.answered_questions.all()
    answered = question in answered_questions

    # Fetch PatientChartData if available
    chart_data = PatientChartData.objects.filter(question=question).first()

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        action = request.POST.get('action')

        # Handle Check Answer action
        if action == 'check_answer' and not answered:
            is_correct = selected_option == question.correct_option
            explanation = question.explanation

            if is_correct:
                quiz_attempt.score += 1
            quiz_attempt.answered_questions.add(
                question)  # Mark question as answered
            quiz_attempt.save()

            # Track subject score in QuizAttemptSubject
            quiz_subject = question.quiz.subject
            attempt_subject, created = QuizAttemptSubject.objects.get_or_create(
                quiz_attempt=quiz_attempt, subject=quiz_subject)
            attempt_subject.total_questions += 1
            if is_correct:
                attempt_subject.score += 1
            attempt_subject.save()

        # Determine the next question
        current_index = questions.index(question)
        next_question = questions[current_index +
                                  1] if current_index + 1 < len(questions) else None

        # Handle Next Question action
        if action == 'next_question':
            if next_question:
                return redirect('quiz_detail', quiz_id=quiz.id, question_id=next_question.id)
            else:
                # If there is no next question, finish the quiz
                quiz_attempt.completed_at = timezone.now()
                quiz_attempt.save()
                return redirect('quiz_result', quiz_id=quiz.id)

        # Handle Finish Quiz action
        elif action == 'finish_quiz':
            quiz_attempt.completed_at = timezone.now()
            quiz_attempt.save()
            return redirect('quiz_result', quiz_id=quiz.id)

    # Determine if this is the last question
    current_index = questions.index(question)
    is_last_question = (current_index == len(questions) - 1)

    return render(request, 'quiz/quiz_detail.html', {
        'quiz': quiz,
        'question': question,
        'questions': questions,
        'selected_option': selected_option,
        'is_correct': is_correct,
        'explanation': explanation,
        'next_question': next_question,
        'answered': answered,
        'is_last_question': is_last_question,
        'chart_data': chart_data,  # Add this to the context
    })


@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempts = QuizAttempt.objects.filter(
        quiz=quiz, user=request.user, completed_at__isnull=False).order_by('-completed_at')
    latest_attempt = attempts.first() if attempts else None

    if latest_attempt:
        subject_scores = latest_attempt.subject_scores.all()
        total_questions = sum([sub.total_questions for sub in subject_scores])
        total_score = sum([sub.score for sub in subject_scores])

        subject_percentages = {
            sub.subject.name: sub.calculate_percentage() for sub in subject_scores
        }

        overall_percentage = (total_score / total_questions) * \
            100 if total_questions > 0 else 0

    else:
        overall_percentage = None
        subject_percentages = {}

    return render(request, 'quiz/quiz_result.html', {
        'quiz': quiz,
        'latest_attempt': latest_attempt,
        'attempts': attempts,
        'overall_percentage': overall_percentage,
        'subject_percentages': subject_percentages
    })
