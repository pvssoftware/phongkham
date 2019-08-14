from django.db import models
from user.models import User

# Create your models here.



class MedicalRecord(models.Model):
    full_name = models.CharField(max_length=30)
    birth_date = models.DateField()
    address = models.CharField(max_length=50)
    sex = models.BooleanField(help_text="True is Female, False is Male")
    height = models.CharField(max_length=10,blank=True,null=True)
    identity_card = models.CharField(max_length=30,blank=True,null=True)
    doctor = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name

class MedicalHistory(models.Model):
    disease_symptom = models.TextField()
    diagnostis = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    medical_record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE)

    def __str__(self):
        return self.medical_record.full_name

class Medicine(models.Model):
    name = models.CharField(max_length=20)
    full_name = models.CharField(max_length=50)
    quantity = models.CharField(max_length=10)
    sale_price = models.CharField(max_length=50)
    import_price = models.CharField(max_length=50)
    doctor = models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ['full_name']


class PrescriptionDrug(models.Model):
    dose = models.CharField(max_length=10)
    time_take_medicine = models.CharField(max_length=30)
    quantity = models.CharField(max_length=10)
    cost = models.CharField(max_length=50)
    medicine = models.ForeignKey(Medicine,on_delete=models.CASCADE)
    medical_history = models.ForeignKey(MedicalHistory,on_delete=models.CASCADE)

    def __str__(self):
        return self.medicine.name

