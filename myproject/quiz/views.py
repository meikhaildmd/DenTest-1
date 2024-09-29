from .models import Quiz, Question, QuizAttempt, PatientChartData, Classification, Subject, QuizAttemptSubject, UserProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from markdown import markdown
from .forms import CustomQuizForm

# Subscription check decorator (optional, not applied yet)


def subscription_required(view_func):
    def wrap(request, *args, **kwargs):
        user_profile = request.user.userprofile
        if not user_profile.is_active_subscription():
            # Redirect to subscription page if not subscribed
            return redirect('subscribe')
        return view_func(request, *args, **kwargs)
    return wrap


@login_required
def classification_list(request):
    classifications = Classification.objects.all()
    subject_progress = {}

    # Fetch session-based custom quiz progress
    custom_progress = request.session.get('custom_quiz_progress', {})

    for classification in classifications:
        for subject in classification.subjects.all():
            # Regular quiz progress from the database
            subject_attempts = QuizAttemptSubject.objects.filter(
                subject=subject,
                quiz_attempt__user=request.user
            )

            avg_score = subject_attempts.aggregate(Avg('score'))['score__avg']
            total_questions = subject_attempts.aggregate(Avg('total_questions'))[
                'total_questions__avg']

            if avg_score is not None and total_questions is not None and total_questions > 0:
                db_percentage = (avg_score / total_questions) * 100
            else:
                db_percentage = None

            # Custom quiz progress from the session
            custom_subject_progress = custom_progress.get(subject.name, None)
            if custom_subject_progress:
                correct = custom_subject_progress['correct']
                total = custom_subject_progress['total']
                custom_percentage = (correct / total) * \
                    100 if total > 0 else None
            else:
                custom_percentage = None

            # Combine progress from both sources (database and session)
            if db_percentage is not None and custom_percentage is not None:
                combined_percentage = (db_percentage + custom_percentage) / 2
            elif db_percentage is not None:
                combined_percentage = db_percentage
            else:
                combined_percentage = custom_percentage

            subject_progress[subject.name] = combined_percentage

    return render(request, 'quiz/classification_list.html', {
        'classifications': classifications,
        'subject_progress': subject_progress
    })


# Subject list view
@login_required
def subject_list(request, classification_id):
    classification = get_object_or_404(Classification, id=classification_id)
    subjects = classification.subjects.all()
    return render(request, 'quiz/subject_list.html', {'classification': classification, 'subjects': subjects})


# Quiz list view
@login_required
def quiz_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    quizzes = subject.quizzes.all()
    return render(request, 'quiz/quiz_list.html', {'subject': subject, 'quizzes': quizzes})


# Create custom quiz view
@login_required
def create_custom_quiz(request):
    if request.method == 'POST':
        form = CustomQuizForm(request.POST)
        if form.is_valid():
            selected_subjects = form.cleaned_data['subjects']
            number_of_questions = form.cleaned_data['number_of_questions']
            questions = Question.objects.filter(
                quiz__subject__in=selected_subjects).order_by('?')[:number_of_questions]

            if not questions:
                return redirect('subject_list', classification_id=selected_subjects.first().classification.id)

            # Store the quiz questions in the session
            request.session['custom_quiz_questions'] = [
                q.id for q in questions]
            return redirect('custom_quiz_detail')

    else:
        form = CustomQuizForm()

    return render(request, 'quiz/create_custom_quiz.html', {'form': form})


# Quiz detail view (for regular quizzes)
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
            quiz_attempt.track_question_progress(question, is_correct)
            explanation = question.explanation

        # Determine the next question
        current_index = questions.index(question)
        next_question = questions[current_index +
                                  1] if current_index + 1 < len(questions) else None

        # Handle Next Question action
        if action == 'next_question':
            if next_question:
                return redirect('quiz_detail', quiz_id=quiz.id, question_id=next_question.id)
            else:
                quiz_attempt.completed_at = timezone.now()
                quiz_attempt.save()
                return redirect('quiz_result', quiz_id=quiz.id)

        # Handle Finish Quiz action
        elif action == 'finish_quiz':
            quiz_attempt.completed_at = timezone.now()
            quiz_attempt.save()
            return redirect('quiz_result', quiz_id=quiz.id)

    # Convert explanation to HTML using Markdown
    explanation_html = markdown(
        question.explanation) if question.explanation else None

    # Determine if this is the last question
    current_index = questions.index(question)
    is_last_question = (current_index == len(questions) - 1)

    return render(request, 'quiz/quiz_detail.html', {
        'quiz': quiz,
        'question': question,
        'questions': questions,
        'selected_option': selected_option,
        'is_correct': is_correct,
        'explanation_html': explanation_html,
        'next_question': next_question,
        'answered': answered,
        'is_last_question': is_last_question,
        'chart_data': chart_data
    })


@login_required
def custom_quiz_detail(request, question_id=None):
    question_ids = request.session.get('custom_quiz_questions', [])
    if not question_ids:
        return redirect('create_custom_quiz')

    questions = Question.objects.filter(id__in=question_ids)
    question = questions[0] if question_id is None else get_object_or_404(
        Question, id=question_id)

    explanation = None
    is_correct = None
    selected_option = None
    answered = False

    # Determine the current index of the question
    current_index = list(questions).index(question)
    next_question = questions[current_index +
                              1] if current_index + 1 < len(questions) else None

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        action = request.POST.get('action')

        # Check answer logic
        if action == 'check_answer' and not answered:
            is_correct = selected_option == question.correct_option
            explanation = question.explanation

            # Track progress in session data for custom quizzes
            subject = question.quiz.subject
            custom_progress = request.session.get('custom_quiz_progress', {})

            if subject.name not in custom_progress:
                custom_progress[subject.name] = {'correct': 0, 'total': 0}

            custom_progress[subject.name]['total'] += 1
            if is_correct:
                custom_progress[subject.name]['correct'] += 1

            # Save custom quiz progress in the session
            request.session['custom_quiz_progress'] = custom_progress

            correct_questions = request.session.get(
                'custom_quiz_correct_questions', [])
            if is_correct and question.id not in correct_questions:
                correct_questions.append(question.id)
                request.session['custom_quiz_correct_questions'] = correct_questions

        # Handle Next Question action
        if action == 'next_question':
            if next_question:
                return redirect('custom_quiz_detail', question_id=next_question.id)
            else:
                return redirect('custom_quiz_result')

        # Handle Finish Quiz action
        elif action == 'finish_quiz':
            correct_answers = sum(1 for q in questions if q.id in request.session.get(
                'custom_quiz_correct_questions', []))
            total_questions = len(questions)
            request.session['custom_quiz_correct_answers'] = correct_answers
            request.session['custom_quiz_total_questions'] = total_questions

            return redirect('custom_quiz_result')

    explanation_html = markdown(explanation) if explanation else None
    is_last_question = current_index == len(questions) - 1

    return render(request, 'quiz/custom_quiz_detail.html', {
        'questions': questions,
        'question': question,
        'selected_option': selected_option,
        'is_correct': is_correct,
        'explanation_html': explanation_html,
        'is_last_question': is_last_question,
        'next_question': next_question
    })


# Quiz result view for both regular and custom quizzes
@login_required
def quiz_result(request, quiz_id=None):
    if quiz_id is None:
        # Handle custom quiz results
        correct_answers = request.session.get('custom_quiz_correct_answers', 0)
        total_questions = request.session.get('custom_quiz_total_questions', 0)
        overall_percentage = (correct_answers / total_questions) * \
            100 if total_questions > 0 else None

        # Fetch subject progress for the custom quiz
        question_ids = request.session.get('custom_quiz_questions', [])
        questions = Question.objects.filter(id__in=question_ids)

        subject_progress = {}
        for question in questions:
            subject = question.quiz.subject
            if subject.name not in subject_progress:
                subject_progress[subject.name] = {'score': 0, 'total': 0}
            subject_progress[subject.name]['total'] += 1
            if question.id in request.session.get('custom_quiz_correct_questions', []):
                subject_progress[subject.name]['score'] += 1

        for subject_name, progress in subject_progress.items():
            progress['percentage'] = (
                progress['score'] / progress['total']) * 100 if progress['total'] > 0 else 0

        return render(request, 'quiz/quiz_result.html', {
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'overall_percentage': overall_percentage,
            'subject_progress': subject_progress,
            'quiz': None,
            'is_custom_quiz': True  # Differentiates custom quiz from regular quiz
        })

    # Handle regular quiz results
    quiz = get_object_or_404(Quiz, id=quiz_id)
    attempts = QuizAttempt.objects.filter(
        quiz=quiz, user=request.user, completed_at__isnull=False).order_by('-completed_at')
    latest_attempt = attempts.first() if attempts else None

    subject_progress = {}
    if latest_attempt:
        subject_scores = latest_attempt.subject_scores.all()
        total_questions = sum([sub.total_questions for sub in subject_scores])
        total_score = sum([sub.score for sub in subject_scores])

        overall_percentage = (total_score / total_questions) * \
            100 if total_questions > 0 else None

        subject_progress = {
            sub.subject.name: {
                'score': sub.score,
                'total': sub.total_questions,
                'percentage': sub.calculate_percentage()
            } for sub in subject_scores
        }
    else:
        overall_percentage = None

    return render(request, 'quiz/quiz_result.html', {
        'quiz': quiz,
        'latest_attempt': latest_attempt,
        'overall_percentage': overall_percentage,
        'subject_progress': subject_progress,
        'is_custom_quiz': False  # Regular quiz flag
    })


# Detailed Explanation view
@login_required
def detailed_explanation(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)

    if question.detailed_explanation:
        detailed_explanation_content = question.detailed_explanation.content
        detailed_explanation_html = markdown(detailed_explanation_content)
    else:
        detailed_explanation_html = None

    return render(request, 'quiz/detailed_explanation.html', {
        'question': question,
        'detailed_explanation': detailed_explanation_html
    })
