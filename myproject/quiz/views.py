from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, QuizAttempt


@login_required
def quiz_home(request):
    """
    View to handle the main quiz page.
    """
    return render(request, 'quiz/quiz_home.html')


@login_required
def practice_quiz(request):
    """
    View to handle the practice quiz.
    Retrieves the 'Practice Quiz' and its questions.
    Handles the quiz submission and calculates the score.
    """
    quiz = get_object_or_404(Quiz, title="Practice Quiz")
    questions = quiz.questions.all()

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_option = request.POST.get(f'question_{question.id}')
            if selected_option == question.correct_option:
                score += 1
        QuizAttempt.objects.create(quiz=quiz, user=request.user, score=score)
        return render(request, 'quiz/quiz_result.html', {'score': score, 'total': questions.count()})

    return render(request, 'quiz/practice_quiz.html', {'quiz': quiz, 'questions': questions})
