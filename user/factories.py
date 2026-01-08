import factory
import random
from faker import Faker as FakerLib
from factory import Faker, post_generation, SubFactory, Sequence
from factory.django import DjangoModelFactory
from datetime import date, timedelta

from .models import (
    DoctorProfile, License, Payment, SettingsTime,
    WeekDay, SettingsService, User
)

_fake = FakerLib()


class DoctorProfileFactory(DjangoModelFactory):
    class Meta:
        model = DoctorProfile

    phone = factory.LazyFunction(
        lambda: ''.join(random.choice('0123456789') for _ in range(random.randint(10, 14)))
    )
    hotline = ''
    full_name = factory.LazyFunction(lambda: _fake.name()[:30])
    clinic_address = factory.LazyFunction(lambda: _fake.address()[:70])
    clinic_name = factory.LazyFunction(lambda: _fake.company()[:100])
    kind = factory.Iterator([k[0] for k in DoctorProfile.KIND_DOCTOR])
    is_trial = False
    time_end_trial = None
    license_ultrasound = False


class LicenseFactory(DjangoModelFactory):
    class Meta:
        model = License

    doctor = SubFactory(DoctorProfileFactory)
    license_end = Faker('date_between', start_date='+1d', end_date='+365d')


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    email = Faker('email')
    amount = "100000"
    order_desc = factory.LazyFunction(lambda: _fake.sentence(nb_words=6)[:100])
    bank_code = ""
    success = False
    status = 0
    license = "basic"
    vnpay_payment_url = ""


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = Sequence(lambda n: f'user{n}@example.com')
    is_active = True
    is_staff = False
    is_superuser = False
    is_admin = False
    doctor = SubFactory(DoctorProfileFactory)

    @post_generation
    def password(self, create, extracted, **kwargs):
        raw = extracted or 'password123'
        self.set_password(raw)
        if create:
            self.save()


class SettingsTimeFactory(DjangoModelFactory):
    class Meta:
        model = SettingsTime

    examination_period = '15'
    enable_voice = False
    doctor = SubFactory(DoctorProfileFactory)


class WeekDayFactory(DjangoModelFactory):
    class Meta:
        model = WeekDay

    day = factory.Iterator([d[0] for d in WeekDay.WEEKDAY])
    opening_time = Faker('time')
    closing_time = Faker('time')
    settingstime = SubFactory(SettingsTimeFactory)


class SettingsServiceFactory(DjangoModelFactory):
    class Meta:
        model = SettingsService

    blood_pressure = False
    weight = False
    glycemic = False
    ph_meter = False
    take_care_pregnant_baby = False
    point_based = False
    medical_ultrasonography = False
    medical_ultrasonography_cost = ''
    endoscopy = False
    medical_test = False
    password = False
    examination_online_cost = ''
    medical_examination_cost = ''
    doctor = SubFactory(DoctorProfileFactory)
