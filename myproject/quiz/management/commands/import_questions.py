from django.core.management.base import BaseCommand
import csv
import os
from django.core.files import File
from django.conf import settings
from quiz.models import Question, QuestionImage, PatientChartData, Subject


class Command(BaseCommand):
    help = 'Imports questions with images and patient chart data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str,
                            help='The path to the CSV file to import')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']

        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Check if the question already exists based on 'question_id' or 'text'
                if Question.objects.filter(question_id=row['question_id']).exists():
                    self.stdout.write(self.style.WARNING(
                        f"Skipping duplicate question based on question_id: {row['question_id']}"))
                    continue
                elif Question.objects.filter(text=row['text']).exists():
                    self.stdout.write(self.style.WARNING(
                        f"Skipping duplicate question based on text: {row['text']}"))
                    continue

                # Find or create the subject
                subject, created = Subject.objects.get_or_create(
                    name=row['subject'])

                # Create the question with the unique 'question_id'
                question = Question.objects.create(
                    # Assign the question_id from the CSV
                    question_id=row['question_id'],
                    quiz_id=None,  # Or assign a quiz if necessary
                    text=row['text'],
                    option1=row['option1'],
                    option2=row['option2'],
                    option3=row['option3'],
                    option4=row['option4'],
                    correct_option=row['correct_option'],
                    explanation=row['explanation'],
                )

                # Handle patient chart data if available
                if row.get('chief_complaint') or row.get('medical_history') or row.get('current_findings'):
                    PatientChartData.objects.create(
                        question=question,
                        chief_complaint=row.get('chief_complaint', ''),
                        medical_history=row.get('medical_history', ''),
                        current_findings=row.get('current_findings', '')
                    )

                # Handle question image if available
                if row.get('question_image_path'):
                    question_image_path = os.path.join(
                        settings.MEDIA_ROOT, row['question_image_path'])
                    if os.path.exists(question_image_path):
                        with open(question_image_path, 'rb') as img_file:
                            question_image = QuestionImage(
                                question=question,
                                image=File(img_file)
                            )
                            question_image.save()

                # Handle explanation image if available
                if row.get('explanation_image_path'):
                    explanation_image_path = os.path.join(
                        settings.MEDIA_ROOT, row['explanation_image_path'])
                    if os.path.exists(explanation_image_path):
                        with open(explanation_image_path, 'rb') as img_file:
                            question.explanation_image.save(
                                os.path.basename(explanation_image_path), File(img_file))
                            question.save()

        self.stdout.write(self.style.SUCCESS(
            f"Successfully imported questions and images from {csv_file}"))
