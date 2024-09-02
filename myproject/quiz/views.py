from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Classification, Subject, Quiz, Question, QuizAttempt
from django.utils import timezone


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
def quiz_detail(request, quiz_id, question_id=None):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.all())

    if question_id is None:
        question = questions[0]
    else:
        question = get_object_or_404(Question, id=question_id)

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        is_correct = selected_option == question.correct_option
        explanation = question.explanation

        # Ensure we get the existing attempt or create a new one if it doesn't exist
        quiz_attempt, created = QuizAttempt.objects.get_or_create(
            quiz=quiz, user=request.user, completed_at=None,
            defaults={'score': 0}
        )

        if created:
            print(f"New QuizAttempt created: {quiz_attempt}")
        else:
            print(f"Existing QuizAttempt found: {quiz_attempt}")

        if is_correct:
            quiz_attempt.score += 1
            print(f"Correct answer. Score updated to: {quiz_attempt.score}")
        else:
            print(f"Incorrect answer. Score remains: {quiz_attempt.score}")

        current_index = questions.index(question)
        next_question = questions[current_index +
                                  1] if current_index + 1 < len(questions) else None

        if next_question is None:
            # Automatically set the completed_at field when the quiz is completed
            quiz_attempt.completed_at = timezone.now()
            print(f"Quiz completed at: {quiz_attempt.completed_at}")
            quiz_attempt.save()
        else:
            quiz_attempt.save()

        return render(request, 'quiz/question_result.html', {
            'quiz': quiz,
            'question': question,
            'selected_option': selected_option,
            'is_correct': is_correct,
            'explanation': explanation,
            'next_question': next_question,
        })

    return render(request, 'quiz/quiz_detail.html', {
        'quiz': quiz,
        'question': question,
        'questions': questions,
    })


@login_required
def quiz_question_detail(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id)
    return render(request, 'quiz/quiz_question_detail.html', {
        'quiz': quiz,
        'question': question,
    })


@login_required
def quiz_result(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempts = QuizAttempt.objects.filter(
        quiz=quiz, user=request.user, completed_at__isnull=False).order_by('-completed_at')
    latest_attempt = attempts.first() if attempts else None

    if latest_attempt is None:
        print("No attempts found for this quiz and user.")
    else:
        print(f"Latest attempt found: {latest_attempt}")

    return render(request, 'quiz/quiz_result.html', {
        'quiz': quiz,
        'latest_attempt': latest_attempt,
        'attempts': attempts,  # Ensure all attempts are passed to the template
    })
