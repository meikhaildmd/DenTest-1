from .models import Question, UserQuestionStatus
from .models import Quiz, Question, UserQuestionStatus, Subject
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, UserQuestionStatus
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


# views.py
@login_required
def create_custom_quiz(request):
    if request.method == 'POST':
        form = CustomQuizForm(request.POST)
        if form.is_valid():
            selected_subjects = form.cleaned_data['subjects']
            number_of_questions = form.cleaned_data['number_of_questions']
            filter_option = form.cleaned_data.get('filter_option', 'all')

            # Base queryset
            questions = Question.objects.filter(
                quiz__subject__in=selected_subjects)

            # Apply status filtering
            if filter_option == 'unanswered':
                questions = questions.exclude(
                    userquestionstatus__user=request.user)
            elif filter_option == 'correct':
                questions = questions.filter(
                    userquestionstatus__user=request.user,
                    userquestionstatus__status='correct'
                )
            elif filter_option == 'incorrect':
                questions = questions.filter(
                    userquestionstatus__user=request.user,
                    userquestionstatus__status='incorrect'
                )
            # Else 'all' - no filtering

            # Randomize and limit the number of questions
            questions = questions.order_by('?')[:number_of_questions]

            if not questions.exists():
                messages.error(
                    request, "No questions found matching your criteria.")
                return redirect('create_custom_quiz')

            # Store question IDs in session for navigation
            request.session['custom_quiz_questions'] = list(
                questions.values_list('id', flat=True))

            return redirect('custom_quiz_detail')
    else:
        form = CustomQuizForm()

    return render(request, 'quiz/create_custom_quiz.html', {'form': form})


@login_required
def quiz_detail(request, quiz_id, question_id=None):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = list(quiz.questions.all())
    question = get_object_or_404(
        Question, id=question_id) if question_id else questions[0]

    # Initialize variables
    explanation = None
    explanation_html = None
    selected_option = None
    is_correct = None
    answered = False

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        action = request.POST.get('action')

        if action == 'check_answer':
            is_correct = (selected_option == question.correct_option)
            answered = True

            # Update or create UserQuestionStatus
            UserQuestionStatus.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={'status': 'correct' if is_correct else 'incorrect'}
            )

            # Set the explanation
            explanation = question.explanation
            explanation_html = markdown(explanation) if explanation else None

        elif action == 'next_question':
            current_index = questions.index(question)
            if current_index + 1 < len(questions):
                next_question = questions[current_index + 1]
                return redirect('quiz_detail', quiz_id=quiz.id, question_id=next_question.id)
            else:
                return redirect('quiz_result', quiz_id=quiz.id)

        elif action == 'finish_quiz':
            return redirect('quiz_result', quiz_id=quiz.id)

    else:
        # GET request
        # Allow re-attempts by not marking the question as answered
        answered = False

    # Determine if this is the last question
    is_last_question = (questions.index(question) == len(questions) - 1)

    # Define the list of options
    option_list = ['option1', 'option2', 'option3', 'option4']

    # Get statuses for all questions to pass to the template
    user_question_statuses = UserQuestionStatus.objects.filter(
        user=request.user, question__in=questions
    )
    question_statuses = {
        uqs.question.id: uqs.status for uqs in user_question_statuses}

    return render(request, 'quiz/quiz_detail.html', {
        'quiz': quiz,
        'question': question,
        'questions': questions,
        'selected_option': selected_option,
        'is_correct': is_correct,
        'explanation_html': explanation_html,
        'is_last_question': is_last_question,
        'answered': answered,
        'option_list': option_list,
        'question_statuses': question_statuses,
    })


@login_required
def custom_quiz_detail(request, question_id=None):
    question_ids = request.session.get('custom_quiz_questions', [])
    if not question_ids:
        return redirect('create_custom_quiz')

    questions = list(Question.objects.filter(id__in=question_ids))
    question = get_object_or_404(
        Question, id=question_id) if question_id else questions[0]

    # Initialize variables
    explanation = None
    explanation_html = None
    selected_option = None
    is_correct = None
    answered = False

    if request.method == 'POST':
        selected_option = request.POST.get('selected_option')
        action = request.POST.get('action')

        if action == 'check_answer':
            is_correct = (selected_option == question.correct_option)
            answered = True

            # Update or create UserQuestionStatus
            UserQuestionStatus.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={'status': 'correct' if is_correct else 'incorrect'}
            )

            # Set the explanation
            explanation = question.explanation
            explanation_html = markdown(explanation) if explanation else None

        elif action == 'next_question':
            current_index = questions.index(question)
            if current_index + 1 < len(questions):
                next_question = questions[current_index + 1]
                return redirect('custom_quiz_detail', question_id=next_question.id)
            else:
                return redirect('custom_quiz_result')

        elif action == 'finish_quiz':
            return redirect('custom_quiz_result')

    else:
        # GET request
        # Allow re-attempts by not marking the question as answered
        answered = False

    # Determine if this is the last question
    is_last_question = (questions.index(question) == len(questions) - 1)

    # Define the list of options
    option_list = ['option1', 'option2', 'option3', 'option4']

    # Get statuses for all questions to pass to the template
    user_question_statuses = UserQuestionStatus.objects.filter(
        user=request.user, question__in=questions
    )
    question_statuses = {
        uqs.question.id: uqs.status for uqs in user_question_statuses}

    return render(request, 'quiz/custom_quiz_detail.html', {
        'questions': questions,
        'question': question,
        'selected_option': selected_option,
        'is_correct': is_correct,
        'explanation_html': explanation_html,
        'is_last_question': is_last_question,
        'answered': answered,
        'option_list': option_list,
        'question_statuses': question_statuses,
    })


@login_required
def quiz_result(request, quiz_id=None):
    if quiz_id is None:
        # Handle custom quiz results
        question_ids = request.session.get('custom_quiz_questions', [])
        if not question_ids:
            return redirect('create_custom_quiz')

        # Fetch UserQuestionStatus records for these questions
        user_question_statuses = UserQuestionStatus.objects.filter(
            user=request.user, question_id__in=question_ids
        )

        correct_answers = user_question_statuses.filter(
            status='correct').count()
        total_questions = len(question_ids)

        overall_percentage = (correct_answers / total_questions) * \
            100 if total_questions > 0 else None

        # Calculate subject progress
        subject_progress = {}
        for uqs in user_question_statuses:
            subject = uqs.question.quiz.subject
            if subject.name not in subject_progress:
                subject_progress[subject.name] = {'score': 0, 'total': 0}
            subject_progress[subject.name]['total'] += 1
            if uqs.status == 'correct':
                subject_progress[subject.name]['score'] += 1

        # Add percentage calculation
        for subject_name, progress in subject_progress.items():
            progress['percentage'] = (
                progress['score'] / progress['total']) * 100 if progress['total'] > 0 else 0

        return render(request, 'quiz/quiz_result.html', {
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'overall_percentage': overall_percentage,
            'subject_progress': subject_progress,
            'quiz': None,  # No specific quiz for custom quizzes
            'is_custom_quiz': True
        })

    else:
        # Handle regular quiz results

        quiz = get_object_or_404(Quiz, id=quiz_id)
        attempts = QuizAttempt.objects.filter(
            quiz=quiz, user=request.user, completed_at__isnull=False).order_by('-completed_at')
        latest_attempt = attempts.first() if attempts else None

        subject_progress = {}
        total_questions = 0
        total_score = 0
        overall_percentage = None

        if latest_attempt:
            subject_scores = latest_attempt.subject_scores.all()

            # Calculate the total number of questions and total score
            total_questions = sum(
                [sub.total_questions for sub in subject_scores])
            total_score = sum([sub.score for sub in subject_scores])

            # Calculate the overall percentage
            if total_questions > 0:
                overall_percentage = (total_score / total_questions) * 100

            # Calculate the percentage for each subject
            subject_progress = {}
            for sub in subject_scores:
                percentage = (sub.score / sub.total_questions) * \
                    100 if sub.total_questions > 0 else 0
                subject_progress[sub.subject.name] = {
                    'score': sub.score,
                    'total': sub.total_questions,
                    'percentage': percentage
                }

        return render(request, 'quiz/quiz_result.html', {
            'quiz': quiz,
            'latest_attempt': latest_attempt,
            'overall_percentage': overall_percentage,
            'total_questions': total_questions,
            'total_score': total_score,  # Ensure total_score is passed
            'subject_progress': subject_progress,
            'is_custom_quiz': False
        })


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
