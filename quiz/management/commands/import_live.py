# quiz/management/commands/import_live.py
import os
import glob
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Automatically import ALL CSV files under quiz/data (any .csv name)."

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base_dir, "data")

        if not os.path.exists(data_dir):
            self.stdout.write(self.style.ERROR(f"❌ Folder not found: {data_dir}"))
            return

        # Match ALL .csv files (any name)
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

        if not csv_files:
            self.stdout.write(self.style.WARNING(f"⚠️ No CSV files found in {data_dir}"))
            return

        self.stdout.write(self.style.SUCCESS(f"📦 Found {len(csv_files)} CSV file(s) to import.\n"))

        total_created = 0
        total_updated = 0
        total_skipped = 0

        for csv_path in csv_files:
            try:
                self.stdout.write(f"➡️  Importing from: {os.path.basename(csv_path)} ...")
                # Run your existing import_questions.py for each file
                call_command("import_questions", csv_path)
                self.stdout.write(self.style.SUCCESS(f"✅ Imported successfully: {os.path.basename(csv_path)}\n"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error importing {csv_path}: {e}\n"))

        self.stdout.write(self.style.SUCCESS("🎯 All CSV imports complete.\n"))