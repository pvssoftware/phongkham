import factory
from faker import Faker as FakerLib
from factory import Faker, SubFactory, Sequence
from factory.django import DjangoModelFactory

from .models import (
    BookedDay, MedicalRecord, MedicalHistory, Medicine,
    PrescriptionDrug, PrescriptionDrugOutStock, AppWindow, BackgroundColor
)
from user.factories import UserFactory, DoctorProfileFactory
from datetime import date, timedelta

_fake = FakerLib()


class BookedDayFactory(DjangoModelFactory):
    class Meta:
        model = BookedDay

    doctor = SubFactory(DoctorProfileFactory)
    date = Faker('date_between', start_date='today', end_date='+10d')
    max_patients = '20'
    current_patients = '0'


class MedicalRecordFactory(DjangoModelFactory):
    class Meta:
        model = MedicalRecord

    full_name = factory.LazyFunction(lambda: _fake.name()[:30])
    birth_date = Faker('date_of_birth')
    address = factory.LazyFunction(lambda: _fake.address()[:50])
    sex = True
    phone = factory.LazyFunction(lambda: ''.join([c for c in _fake.phone_number() if c.isdigit()])[:20])
    password = 'pass123'
    doctor = SubFactory(UserFactory)
    total_point_based = '0'


class MedicalHistoryFactory(DjangoModelFactory):
    class Meta:
        model = MedicalHistory

    service = 'khám phụ sản'
    disease_symptom = Faker('sentence')
    diagnostis = Faker('sentence')
    PARA = 'A-B-C-D'
    contraceptive = 'Khong'
    blood_pressure = ''
    weight = ''
    glycemic = ''
    ph_meter = ''
    take_care_pregnant_baby = ''
    medical_record = SubFactory(MedicalRecordFactory)
    is_waiting = False


class MedicineFactory(DjangoModelFactory):
    class Meta:
        model = Medicine

    name = factory.LazyFunction(lambda: _fake.word()[:50])
    full_name = factory.LazyFunction(lambda: _fake.word()[:50])
    quantity = '100'
    sale_price = '10000'
    import_price = '8000'
    doctor = SubFactory(UserFactory)
    unit = 'viên'


class PrescriptionDrugFactory(DjangoModelFactory):
    class Meta:
        model = PrescriptionDrug

    dose = '1 viên'
    time_take_medicine = 'sáng'
    quantity = '10'
    cost = '100000'
    medicine = SubFactory(MedicineFactory)
    medical_history = SubFactory(MedicalHistoryFactory)


class PrescriptionDrugOutStockFactory(DjangoModelFactory):
    class Meta:
        model = PrescriptionDrugOutStock

    name = factory.LazyFunction(lambda: _fake.word()[:50])
    dose = ''
    time_take_medicine = 'sáng'
    quantity = '1'
    cost = '0'
    medical_history = SubFactory(MedicalHistoryFactory)
    unit = 'viên'


class AppWindowFactory(DjangoModelFactory):
    class Meta:
        model = AppWindow

    version = Sequence(lambda n: f'0.0.{n}')


class BackgroundColorFactory(DjangoModelFactory):
    class Meta:
        model = BackgroundColor

    navbar = '#009688'
    doctor = SubFactory(DoctorProfileFactory)
