from django.core.management.base import BaseCommand
import csv, os, re, unicodedata
from django.core.files import File
from django.conf import settings
from quiz.models import Question, QuestionImage, PatientChartData, Subject

def normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"[\.!\?:;,\u200b]+$", "", s)
    return s

def find_existing_by_subject_and_text(subject, raw_text):
    # Try exact first, then normalized match
    exact = Question.objects.filter(subject=subject, text=raw_text).first()
    if exact:
        return exact
    target = normalize_text(raw_text)
    if not target:
        return None
    for q in Question.objects.filter(subject=subject).only("id", "text"):
        if normalize_text(q.text) == target:
            return q
    return None

def parse_correct_option(val):
    """Map 1–4 or A–D → 'option1'..'option4' (matches model choices)."""
    if val is None:
        return None
    s = str(val).strip().upper()
    if s in {"1","2","3","4"}:
        return f"option{s}"
    return {"A":"option1","B":"option2","C":"option3","D":"option4"}.get(s, None)

class Command(BaseCommand):
    help = "Upsert questions from a CSV. Matches by (subject_id + normalized question text)."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="Path to CSV exported from Google Sheets")
        parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing to DB")

    def handle(self, *args, **kwargs):
        csv_file = kwargs["csv_file"]
        dry = kwargs["dry_run"]

        created = updated = skipped = 0

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                raw_text = (row.get("text") or "").strip()
                if not raw_text:
                    skipped += 1
                    continue

                subject_id = (row.get("subject_id") or "").strip()
                if not subject_id:
                    skipped += 1
                    continue

                try:
                    subject = Subject.objects.get(id=subject_id)
                except Subject.DoesNotExist:
                    skipped += 1
                    continue

                instance = find_existing_by_subject_and_text(subject, raw_text)
                correct_option = parse_correct_option(row.get("correct_option"))

                if instance is None:
                    # CREATE
                    if not dry:
                        instance = Question.objects.create(
                            subject=subject,
                            text=raw_text,
                            option1=row.get("option1",""),
                            option2=row.get("option2",""),
                            option3=row.get("option3",""),
                            option4=row.get("option4",""),
                            correct_option=correct_option,
                            explanation=row.get("explanation",""),
                        )
                    created += 1
                else:
                    # UPDATE
                    if not dry:
                        instance.subject = subject
                        instance.text = raw_text
                        instance.option1 = row.get("option1","")
                        instance.option2 = row.get("option2","")
                        instance.option3 = row.get("option3","")
                        instance.option4 = row.get("option4","")
                        instance.correct_option = correct_option
                        instance.explanation = row.get("explanation","")
                        instance.save()
                    updated += 1

                # Optional patient chart data
                has_chart = any([row.get("chief_complaint"),
                                 row.get("medical_history"),
                                 row.get("current_findings")])
                if has_chart and not dry:
                    pcd, _ = PatientChartData.objects.get_or_create(question=instance)
                    pcd.chief_complaint   = row.get("chief_complaint","") or ""
                    pcd.medical_history   = row.get("medical_history","") or ""
                    pcd.current_findings  = row.get("current_findings","") or ""
                    pcd.save()

                # Optional images (CSV columns: 'question_image', 'explanation_image')
                def attach_image(col, save_to_field=None, as_related_model=False):
                    rel = (row.get(col) or "").strip()
                    if not rel:
                        return
                    file_path = os.path.join(settings.MEDIA_ROOT, rel)
                    if not os.path.exists(file_path):
                        return
                    if dry:
                        return
                    with open(file_path, "rb") as imgf:
                        if as_related_model:
                            QuestionImage.objects.create(question=instance, image=File(imgf))
                        else:
                            getattr(instance, save_to_field).save(os.path.basename(file_path), File(imgf))
                            instance.save()

                # Uncomment if/when you use images:
                # attach_image("question_image", as_related_model=True)
                # attach_image("explanation_image", save_to_field="explanation_image", as_related_model=False)

        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created}, Updated: {updated}, Skipped: {skipped}"))