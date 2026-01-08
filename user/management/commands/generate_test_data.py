from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from user.models import License

try:
    from user.factories import (
        DoctorProfileFactory, UserFactory, LicenseFactory,
        SettingsTimeFactory, WeekDayFactory, SettingsServiceFactory,
        PaymentFactory
    )
    from doctors.factories import (
        BookedDayFactory, MedicalRecordFactory, MedicalHistoryFactory,
        MedicineFactory, PrescriptionDrugFactory, PrescriptionDrugOutStockFactory
    )
except Exception as e:
    raise


class Command(BaseCommand):
    help = 'Generate test data for development using factories'

    def add_arguments(self, parser):
        parser.add_argument('--doctors', type=int, default=3)
        parser.add_argument('--patients-per-doctor', type=int, default=10)
        parser.add_argument('--histories-per-patient', type=int, default=2)
        parser.add_argument('--medicines-per-doctor', type=int, default=5)
        parser.add_argument('--booked-days-per-doctor', type=int, default=2)

    def handle(self, *args, **options):
        num_doctors = options['doctors']
        patients_per = options['patients_per_doctor']
        histories_per = options['histories_per_patient']
        meds_per = options['medicines_per_doctor']
        booked_days = options['booked_days_per_doctor']

        created = {
            'doctors': 0,
            'users': 0,
            'licenses': 0,
            'settings': 0,
            'weekdays': 0,
            'booked_days': 0,
            'medicines': 0,
            'patients': 0,
            'histories': 0,
            'prescriptions': 0,
        }

        for i in range(num_doctors):
            doctor = DoctorProfileFactory.create()
            created['doctors'] += 1

            user = UserFactory.create(doctor=doctor)
            created['users'] += 1

            # license: ensure doctor has a valid license (1 year from today)
            try:
                License.objects.create(doctor=doctor, license_end=timezone.now().date() + timedelta(days=365))
            except Exception:
                # if license already exists via factory, update end date
                try:
                    lic = doctor.license
                    lic.license_end = timezone.now().date() + timedelta(days=365)
                    lic.save()
                except Exception:
                    pass
            # ensure flags on doctor/user
            doctor.is_trial = False
            doctor.license_ultrasound = False
            doctor.save()
            user.is_active = True
            user.save()
            created['licenses'] += 1

            # settings
            setting = SettingsTimeFactory.create(doctor=doctor)
            SettingsServiceFactory.create(doctor=doctor)
            created['settings'] += 2

            # create weekdays for this setting
            days = [d[0] for d in WeekDayFactory._meta.model.WEEKDAY]
            for d in days:
                WeekDayFactory.create(settingstime=setting, day=d)
                created['weekdays'] += 1

            # booked days
            BookedDayFactory.create_batch(booked_days, doctor=doctor)
            created['booked_days'] += booked_days

            # medicines for the doctor's user
            MedicineFactory.create_batch(meds_per, doctor=user)
            created['medicines'] += meds_per

            # patients and histories
            for _ in range(patients_per):
                patient = MedicalRecordFactory.create(doctor=user)
                created['patients'] += 1
                histories = MedicalHistoryFactory.create_batch(histories_per, medical_record=patient)
                created['histories'] += len(histories)

                for h in histories:
                    PrescriptionDrugFactory.create(medical_history=h)
                    PrescriptionDrugOutStockFactory.create(medical_history=h)
                    created['prescriptions'] += 2

        self.stdout.write(self.style.SUCCESS('Generated test data:'))
        for k, v in created.items():
            self.stdout.write(f'- {k}: {v}')
