# quiz/serializers.py

from rest_framework import serializers
from .models import Section, Subject, Question, UserQuestionStatus


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name', 'exam_type']


class SubjectSerializer(serializers.ModelSerializer):
    section = SectionSerializer()

    class Meta:
        model = Subject
        fields = ['id', 'name', 'section']


class QuestionSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()

    class Meta:
        model = Question
        fields = [
            'id',
            'text',
            'option1',
            'option2',
            'option3',
            'option4',
            'correct_option',
            'explanation',
            'subject'
        ]

# serializers.py

class SectionWithSubjectsSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ['id', 'name', 'subjects']

# serializers.py (append this at the end)

class UserQuestionStatusSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source="question.id")
    correct_option = serializers.CharField(source="question.correct_option")

    class Meta:
        model = UserQuestionStatus
        fields = [
            "question_id",
            "last_answer",
            "correct_option",
            "times_seen",
            "times_correct",
            "last_was_correct",
        ]