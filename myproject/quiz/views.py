from .models import Quiz, Question, QuizAttempt
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Classification, Subject, Quiz, Question, QuizAttempt


@login_required
def classification_list(request):
    classifications = Classification.objects.all()
    return render(request, 'quiz/classification_list.html', {'classifications': classifications})


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
@login_required
def quiz_detail(request, quiz_id, question_id=None):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.all())

    if question_id is None:
        question = questions[0]
    else:
        question = get_object_or_404(Question, id=question_id)

    explanation = None
    is_correct = None
    selected_option = None
    next_question = None

    # Use transaction.atomic() to ensure that operations are atomic
    with transaction.atomic():
        quiz_attempt, created = QuizAttempt.objects.get_or_create(
            quiz=quiz, user=request.user, completed_at__isnull=True,
            defaults={'score': 0}
        )

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        action = request.POST.get('action')

        if action == 'check_answer':
            is_correct = selected_option == question.correct_option
            explanation = question.explanation

            if is_correct:
                quiz_attempt.score += 1
                quiz_attempt.save()

        # Determine the next question
        current_index = questions.index(question)
        next_question = questions[current_index +
                                  1] if current_index + 1 < len(questions) else None

        if action == 'next_question':
            if next_question is None:
                quiz_attempt.completed_at = timezone.now()
                quiz_attempt.save()
                return redirect('quiz_result', quiz_id=quiz.id)
            else:
                return redirect('quiz_detail', quiz_id=quiz.id, question_id=next_question.id)

    return render(request, 'quiz/quiz_detail.html', {
        'quiz': quiz,
        'question': question,
        'questions': questions,
        'selected_option': selected_option,
        'is_correct': is_correct,
        'explanation': explanation,
        'next_question': next_question,
    })


@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempts = QuizAttempt.objects.filter(
        quiz=quiz, user=request.user, completed_at__isnull=False).order_by('-completed_at')
    latest_attempt = attempts.first() if attempts else None

    if latest_attempt:
        percentage = (latest_attempt.score / quiz.questions.count()) * 100
    else:
        percentage = None

    return render(request, 'quiz/quiz_result.html', {
        'quiz': quiz,
        'latest_attempt': latest_attempt,
        'attempts': attempts,
        'percentage': percentage,
    })
