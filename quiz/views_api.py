from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token

from .models import Section, Subject, Question, UserQuestionStatus
from .serializers import (
    SectionSerializer,
    SubjectSerializer,
    QuestionSerializer,
    SectionWithSubjectsSerializer,
    UserQuestionStatusSerializer,
)

# ───────── CSRF helper for frontend login ─────────
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Simple endpoint: sets csrftoken cookie and returns 200.
    Front-end hits /api/csrf/ to retrieve the cookie before login.
    """
    return JsonResponse({"detail": "CSRF cookie set"})

# ───────── Basic list / detail views ─────────

class SectionList(generics.ListAPIView):
    serializer_class = SectionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Section.objects.filter(exam_type=self.kwargs["exam_type"])


class SubjectListBySection(generics.ListAPIView):
    serializer_class = SubjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Subject.objects.filter(section_id=self.kwargs["section_id"])


class QuestionListBySubject(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Question.objects.filter(subject_id=self.kwargs["subject_id"])


class SectionWithSubjectsView(generics.RetrieveAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionWithSubjectsSerializer
    permission_classes = [AllowAny]
    lookup_url_kwarg = "section_id"

# ───────── User-question endpoints ─────────

class UserQuestionStatusBySubjectView(generics.ListAPIView):
    """Return every UserQuestionStatus for this user in the given subject."""
    serializer_class = UserQuestionStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserQuestionStatus.objects.filter(
            user=self.request.user,
            question__subject_id=self.kwargs["subject_id"],
        )

# ✅  Updated: decide correctness on the server
class UserQuestionStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        qid      = request.data.get("question_id")
        selected = request.data.get("selected")          # 'option1', 'option2', …

        try:
            question = Question.objects.get(id=qid)
        except Question.DoesNotExist:
            return Response({"detail": "Question not found."}, status=404)

        is_correct = selected == question.correct_option

        status_obj, _ = UserQuestionStatus.objects.get_or_create(
            user=request.user, question=question
        )
        status_obj.record_attempt(chosen_option=selected, correct=is_correct)

        return Response({"detail": "Saved"}, status=200)

# ✅  Updated: use last_was_correct (latest attempt)
class UserProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        progress = {}
        for s in UserQuestionStatus.objects.filter(user=request.user):
            sid = s.question.subject_id
            if sid not in progress:
                progress[sid] = {"correct": 0, "total": 0}
            progress[sid]["total"] += 1
            if s.last_was_correct:
                progress[sid]["correct"] += 1

        return Response(
            [{"subject_id": sid, **data} for sid, data in progress.items()],
            status=200,
        )

class CustomQuizView(APIView):
    """
    POST /api/custom-quiz/
    {
      "subject_ids": [1, 2, 3],                # required
      "filter": "all|correct|incorrect|unanswered",
      "limit": 20                              # default 20
    }

    • Anyone can request "all".
    • Only authenticated users may request the answer-based filters.
    """
    permission_classes = [AllowAny]  # allow guests

    def post(self, request):
        subj_ids: list[int] = request.data.get("subject_ids", [])
        filt: str           = request.data.get("filter", "all").lower()
        limit: int          = int(request.data.get("limit", 20))

        if not subj_ids:
            return Response(
                {"detail": "subject_ids required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---- guest restriction ------------------------------------------------
        if not request.user.is_authenticated and filt != "all":
            return Response(
                {"detail": "Login required for this filter"},
                status=status.HTTP_403_FORBIDDEN,
            )
        # -----------------------------------------------------------------------

        qs = Question.objects.filter(subject_id__in=subj_ids)

        # answer-based filters (require auth)
        if filt in ("correct", "incorrect", "unanswered"):
            if filt == "correct":
                qs = qs.filter(
                    user_statuses__user=request.user,
                    user_statuses__last_was_correct=True,
                )
            elif filt == "incorrect":
                qs = qs.filter(
                    user_statuses__user=request.user,
                    user_statuses__last_was_correct=False,
                )
            else:  # "unanswered"
                qs = qs.exclude(user_statuses__user=request.user)

        # randomise and cap
        questions = qs.order_by("?")[:limit]
        return Response(QuestionSerializer(questions, many=True).data)
# ───────── Simple login & CSRF helpers (unchanged) ─────────

@ensure_csrf_cookie
def get_csrf_token(request):
    """
    Sets csrftoken cookie and also returns it in JSON.
    Frontend should call this before login to get the token.
    """
    token = get_token(request)
    return JsonResponse({"csrftoken": token})


# ───────── Login view ─────────
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user = authenticate(
            request,
            username=request.data.get("username"),
            password=request.data.get("password"),
        )
        if user:
            login(request, user)
            return Response({"detail": "Login successful"})
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# ───────── Current user view ─────────
class CurrentUserView(APIView):
    """
    GET /api/current-user/   →  {"username": "meikhaildmd"}
    403 if not authenticated
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"username": request.user.username})


# ───────── Logout view ─────────
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Logged out"}, status=200)


# ───────── Signup view ─────────
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
import json


@method_decorator(csrf_exempt, name="dispatch")
class SignupView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            # --- basic validation ---
            if not username or not password:
                return JsonResponse(
                    {"error": "Username and password are required."}, status=400
                )

            if User.objects.filter(username=username).exists():
                return JsonResponse(
                    {"error": "Username already exists."}, status=400
                )

            if email and User.objects.filter(email=email).exists():
                return JsonResponse(
                    {"error": "Email already registered."}, status=400
                )

            # --- create user ---
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            user.save()

            # --- automatically log them in (optional) ---
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)

            return JsonResponse(
                {"message": "User created successfully.", "username": user.username},
                status=201,
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)