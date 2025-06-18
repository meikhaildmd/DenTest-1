# quiz/views.py  (FULL FILE)

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from markdown import markdown

from .forms import CustomQuizForm
from .models import (
    Classification,
    Question,
    Quiz,
    QuizAttempt,
    QuizAttemptSubject,
    Subject,
    UserProfile,
    UserQuestionStatus,
)


# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def get_sorted_questions(quiz):
    """Return questions for a quiz in deterministic order."""
    return list(quiz.questions.order_by("id"))


def subscription_required(view_func):
    """Optional decorator in case you enable subscriptions later."""
    def wrap(request, *args, **kwargs):
        user_profile = request.user.userprofile
        if not user_profile.is_active_subscription():
            return redirect("subscribe")
        return view_func(request, *args, **kwargs)

    return wrap


# --------------------------------------------------------------------
# Dashboard / Home  –  shows subject progress + resume-quiz banner
# --------------------------------------------------------------------
@login_required
def classification_list(request):
    classifications = Classification.objects.all()
    subject_progress = {}

    # Calculate global progress (DB-backed)
    for classification in classifications:
        for subject in classification.subjects.all():
            qs = Question.objects.filter(quiz__subject=subject)
            total_attempted = qs.exclude(
                userquestionstatus__user=request.user,
                userquestionstatus__status="unanswered",
            ).count()
            total_correct = qs.filter(
                userquestionstatus__user=request.user,
                userquestionstatus__status="correct",
            ).count()
            pct = (total_correct / total_attempted *
                   100) if total_attempted else None
            subject_progress[subject.name] = pct

    context = {
        "classifications": classifications,
        "subject_progress": subject_progress,
        # Banner flags
        "resume_quiz": request.session.get("active_quiz_id"),
        "resume_custom_quiz": bool(request.session.get("custom_quiz_questions")),
    }
    return render(request, "quiz/classification_list.html", context)


# --------------------------------------------------------------------
# Simple list views
# --------------------------------------------------------------------
@login_required
def subject_list(request, classification_id):
    classification = get_object_or_404(Classification, id=classification_id)
    subjects = classification.subjects.all()
    return render(
        request,
        "quiz/subject_list.html",
        {"classification": classification, "subjects": subjects},
    )


@login_required
def quiz_list(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    quizzes = subject.quizzes.all()
    return render(request, "quiz/quiz_list.html", {"subject": subject, "quizzes": quizzes})


# --------------------------------------------------------------------
# Custom quiz creator
# --------------------------------------------------------------------
@login_required
def create_custom_quiz(request):
    if request.method == "POST":
        form = CustomQuizForm(request.POST)
        if form.is_valid():
            subjects = form.cleaned_data["subjects"]
            n_qs = form.cleaned_data["number_of_questions"]
            filter_opt = form.cleaned_data.get("filter_option", "all")

            qs = Question.objects.filter(quiz__subject__in=subjects)

            if filter_opt == "unanswered":
                qs = qs.exclude(userquestionstatus__user=request.user)
            elif filter_opt == "correct":
                qs = qs.filter(
                    userquestionstatus__user=request.user,
                    userquestionstatus__status="correct",
                )
            elif filter_opt == "incorrect":
                qs = qs.filter(
                    userquestionstatus__user=request.user,
                    userquestionstatus__status="incorrect",
                )

            qs = qs.order_by("?")[:n_qs]
            if not qs:
                messages.error(
                    request, "No questions found matching your criteria.")
                return redirect("create_custom_quiz")

            # Store question IDs + reset per-attempt answers for this custom quiz
            request.session["custom_quiz_questions"] = list(
                qs.values_list("id", flat=True))
            request.session["custom_quiz_attempt_answers"] = {}
            request.session.modified = True
            return redirect("custom_quiz_detail")
    else:
        form = CustomQuizForm()

    return render(request, "quiz/create_custom_quiz.html", {"form": form})


# --------------------------------------------------------------------
# REGULAR QUIZ DETAIL  (per-attempt tracking in session)
# --------------------------------------------------------------------
@login_required
def quiz_detail(request, quiz_id, question_id=None):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = get_sorted_questions(quiz)

    # Mark this quiz as “active” so we can resume if user leaves
    request.session["active_quiz_id"] = quiz.id

    # Session bucket for this quiz attempt
    attempt_key = "quiz_attempt_answers"
    per_attempt = request.session.setdefault(
        attempt_key, {}).setdefault(str(quiz.id), {})

    # Determine current question
    question = get_object_or_404(
        Question, id=question_id) if question_id else questions[0]
    idx = questions.index(question)
    is_last = idx == len(questions) - 1

    # Pull per-attempt answer if exists
    answered_info = per_attempt.get(str(question.id))
    answered = bool(answered_info)
    selected_option = answered_info["selected"] if answered_info else None
    is_correct = answered_info["is_correct"] if answered_info else None
    explanation_html = markdown(question.explanation) if (
        question.explanation and answered) else None

    # --------------- POST ---------------
    if request.method == "POST":
        selected_option = request.POST.get("selected_option")
        action = request.POST.get("action")

        if action == "check_answer" and not answered:
            is_correct = selected_option == question.correct_option
            answered = True
            explanation_html = markdown(
                question.explanation) if question.explanation else None

            # Save per-attempt
            per_attempt[str(question.id)] = {
                "selected": selected_option, "is_correct": is_correct}
            request.session.modified = True

            # Global DB update
            UserQuestionStatus.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={"status": "correct" if is_correct else "incorrect"},
            )

        elif action == "next_question" and not is_last:
            return redirect("quiz_detail", quiz_id=quiz.id, question_id=questions[idx + 1].id)

        elif action == "finish_quiz" or is_last:
            return redirect("quiz_result", quiz_id=quiz.id)

    # Sidebar colour map (global statuses)
    global_statuses = {
        uqs.question.id: uqs.status
        for uqs in UserQuestionStatus.objects.filter(user=request.user, question__in=questions)
    }

    context = {
        "quiz": quiz,
        "question": question,
        "questions": questions,
        "current_index": idx + 1,
        "total_questions": len(questions),
        "selected_option": selected_option,
        "is_correct": is_correct,
        "explanation_html": explanation_html,
        "is_last_question": is_last,
        "answered": answered,
        "option_list": ["option1", "option2", "option3", "option4"],
        "question_statuses": global_statuses,
    }
    return render(request, "quiz/quiz_detail.html", context)


# --------------------------------------------------------------------
# CUSTOM QUIZ DETAIL (very similar logic)
# --------------------------------------------------------------------
@login_required
def custom_quiz_detail(request, question_id=None):
    ids = request.session.get("custom_quiz_questions", [])
    if not ids:
        return redirect("create_custom_quiz")

    questions = list(Question.objects.filter(id__in=ids).order_by("id"))
    question = get_object_or_404(
        Question, id=question_id) if question_id else questions[0]
    idx = questions.index(question)
    is_last = idx == len(questions) - 1

    per_attempt = request.session.setdefault("custom_quiz_attempt_answers", {})

    answered_info = per_attempt.get(str(question.id))
    answered = bool(answered_info)
    selected_option = answered_info["selected"] if answered_info else None
    is_correct = answered_info["is_correct"] if answered_info else None
    explanation_html = markdown(question.explanation) if (
        question.explanation and answered) else None

    if request.method == "POST":
        selected_option = request.POST.get("selected_option")
        action = request.POST.get("action")

        if action == "check_answer" and not answered:
            is_correct = selected_option == question.correct_option
            answered = True
            explanation_html = markdown(
                question.explanation) if question.explanation else None

            per_attempt[str(question.id)] = {
                "selected": selected_option, "is_correct": is_correct}
            request.session.modified = True

            UserQuestionStatus.objects.update_or_create(
                user=request.user,
                question=question,
                defaults={"status": "correct" if is_correct else "incorrect"},
            )

        elif action == "next_question" and not is_last:
            return redirect("custom_quiz_detail", question_id=questions[idx + 1].id)

        elif action == "finish_quiz" or is_last:
            return redirect("custom_quiz_result")

    global_statuses = {
        uqs.question.id: uqs.status
        for uqs in UserQuestionStatus.objects.filter(user=request.user, question__in=questions)
    }

    context = {
        "questions": questions,
        "question": question,
        "current_index": idx + 1,
        "total_questions": len(questions),
        "selected_option": selected_option,
        "is_correct": is_correct,
        "explanation_html": explanation_html,
        "is_last_question": is_last,
        "answered": answered,
        "option_list": ["option1", "option2", "option3", "option4"],
        "question_statuses": global_statuses,
    }
    return render(request, "quiz/custom_quiz_detail.html", context)

# --------------------------------------------------------------------
# QUIZ RESULT  – regular premade quizzes
# --------------------------------------------------------------------


@login_required
def quiz_result(request, quiz_id):
    # clear per-attempt session data for this quiz
    request.session.get("quiz_attempt_answers", {}).pop(str(quiz_id), None)
    request.session.pop("active_quiz_id", None)
    request.session.modified = True

    quiz = get_object_or_404(Quiz, id=quiz_id)
    q_ids = list(quiz.questions.values_list("id", flat=True))

    # statuses for *this quiz*
    quiz_statuses = UserQuestionStatus.objects.filter(
        user=request.user, question_id__in=q_ids
    )

    correct_answers = quiz_statuses.filter(status="correct").count()
    total_questions = len(q_ids)
    overall_pct = correct_answers / total_questions * 100 if total_questions else None

    # per-subject score for this quiz
    subject_progress = {}
    for uqs in quiz_statuses:
        subj = uqs.question.quiz.subject
        row = subject_progress.setdefault(subj.name, {"score": 0, "total": 0})
        row["total"] += 1
        if uqs.status == "correct":
            row["score"] += 1
    for row in subject_progress.values():
        row["percentage"] = row["score"] / \
            row["total"] * 100 if row["total"] else 0

    # cumulative progress (all attempts) for same subjects
    cumulative_progress = {}
    for subj_name in subject_progress.keys():
        subj = Subject.objects.get(name=subj_name)
        all_statuses = UserQuestionStatus.objects.filter(
            user=request.user, question__quiz__subject=subj
        ).exclude(status="unanswered")
        total_all = all_statuses.count()
        correct_all = all_statuses.filter(status="correct").count()
        pct_all = correct_all / total_all * 100 if total_all else 0
        cumulative_progress[subj_name] = {
            "score": correct_all,
            "total": total_all,
            "percentage": pct_all,
        }

    return render(
        request,
        "quiz/quiz_result.html",
        {
            "quiz": quiz,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "overall_percentage": overall_pct,
            "subject_progress": subject_progress,       # this quiz
            "cumulative_progress": cumulative_progress,  # overall
            "latest_attempt": True,
            "is_custom_quiz": False,
        },
    )


# --------------------------------------------------------------------
# CUSTOM QUIZ RESULT
# --------------------------------------------------------------------
@login_required
def custom_quiz_result(request):
    ids = request.session.get("custom_quiz_questions", [])
    if not ids:
        return redirect("create_custom_quiz")

    # clear per-attempt session data
    request.session.pop("custom_quiz_questions", None)
    request.session.pop("custom_quiz_attempt_answers", None)
    request.session.modified = True

    quiz_statuses = UserQuestionStatus.objects.filter(
        user=request.user, question_id__in=ids
    )

    correct = quiz_statuses.filter(status="correct").count()
    total = len(ids)
    overall_pct = correct / total * 100 if total else None

    # per-subject score for this custom quiz
    subject_progress = {}
    for uqs in quiz_statuses:
        subj = uqs.question.quiz.subject
        row = subject_progress.setdefault(subj.name, {"score": 0, "total": 0})
        row["total"] += 1
        if uqs.status == "correct":
            row["score"] += 1
    for row in subject_progress.values():
        row["percentage"] = row["score"] / \
            row["total"] * 100 if row["total"] else 0

    # cumulative progress for those subjects
    cumulative_progress = {}
    for subj_name in subject_progress.keys():
        subj = Subject.objects.get(name=subj_name)
        all_statuses = UserQuestionStatus.objects.filter(
            user=request.user, question__quiz__subject=subj
        ).exclude(status="unanswered")
        total_all = all_statuses.count()
        correct_all = all_statuses.filter(status="correct").count()
        pct_all = correct_all / total_all * 100 if total_all else 0
        cumulative_progress[subj_name] = {
            "score": correct_all,
            "total": total_all,
            "percentage": pct_all,
        }

    return render(
        request,
        "quiz/quiz_result.html",
        {
            "correct_answers": correct,
            "total_questions": total,
            "overall_percentage": overall_pct,
            "subject_progress": subject_progress,       # this quiz
            "cumulative_progress": cumulative_progress,  # overall
            "quiz": None,
            "is_custom_quiz": True,
        },
    )
