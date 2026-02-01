from django.core.management.base import BaseCommand
from doctors.models import MedicalHistory
from doctors.services.invoice_service import get_invoice


class Command(BaseCommand):
    """
    Cronjob Usage on server without docker:
    ```
    $ */1 * * * * cd /home/healthy_care/Healthy_Care/ && source /home/healthy_care/virtualenv/healthy_care/bin/activate && python3 manage.py sync_pending_invoices --limit 3
    ```
    """
    help = "Sync pending invoice data by calling invoice service for histories waiting for tax code"

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=0, help='Limit number of histories to process (0 = all)')

    def handle(self, *args, **options):
        limit = options.get('limit') or 0
        qs = MedicalHistory.objects.waiting_approve_tax_code()
        total = qs.count()
        self.stdout.write(self.style.NOTICE(f'Found {total} pending histories'))
        if limit > 0:
            qs = qs[:limit]
            self.stdout.write(self.style.NOTICE(f'Limiting to {limit} items'))

        processed = 0
        errors = 0
        for history in qs:
            processed += 1
            try:
                r_result = get_invoice(history.pk)
                result = r_result.get("data")
                # result is a dict-like from base_service; print summary
                message = result.get('message')
                self.stdout.write(f'[{processed}/{total}] history={history.pk} -> message={message}')
            except Exception as exc:
                errors += 1
                self.stderr.write(f'Error processing history {history.pk}: {exc}')

        self.stdout.write(self.style.SUCCESS(f'Done. Processed={processed}, errors={errors}'))
