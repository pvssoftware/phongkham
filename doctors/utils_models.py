import pytz,os




# locate upload file ultrasound 1
def locate_medical_ultrasonography_upload(instance,filename):
    # extension = re.sub(r".*\/","",instance.type_file_medical_ultrasonography)
    filename = ("%s_%s_%s.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone, instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"))
    
    return os.path.join("{}/{}/medical_ultrasonography/".format(instance.medical_record.pk,instance.pk),filename)
# locate upload file ultrasound 2
def locate_medical_ultrasonography_upload_2(instance,filename):
    # extension = re.sub(r".*\/","",instance.type_file_medical_ultrasonography)
    filename = ("%s_%s_%s_2.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone, instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"))
    
    return os.path.join("{}/{}/medical_ultrasonography/".format(instance.medical_record.pk,instance.pk),filename)
# locate upload file ultrasound 3
def locate_medical_ultrasonography_upload_3(instance,filename):
    # extension = re.sub(r".*\/","",instance.type_file_medical_ultrasonography)
    filename = ("%s_%s_%s_3.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone, instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"))
    
    return os.path.join("{}/{}/medical_ultrasonography/".format(instance.medical_record.pk,instance.pk),filename)


# locate upload file endoscopy
def locate_endoscopy_upload(instance,filename):
    # extension = re.sub(r".*\/","",instance.type_file_endoscopy)
    filename = ("%s_%s_%s.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone,instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"))
    return os.path.join("{}/{}/endoscopy/".format(instance.medical_record.pk,instance.pk),filename)

# locate upload file medical test
def locate_medical_test_upload(instance,filename):
    # extension = re.sub(r".*\/","",instance.type_file_endoscopy)
    filename = ("%s_%s_%s.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone,instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"))
    return os.path.join("{}/{}/medical_test/".format(instance.medical_record.pk,instance.pk),filename)
# locate upload file medical test 2
def locate_medical_test_upload_2(instance,filename):
    # extension = re.sub(r".*\/","",instance.type_file_endoscopy)
    filename = ("%s_%s_%s_2.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone,instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"))
    return os.path.join("{}/{}/medical_test/".format(instance.medical_record.pk,instance.pk),filename)
# locate upload file medical test 3
def locate_medical_test_upload_3(instance,filename):
    # extension = re.sub(r".*\/","",instance.type_file_endoscopy)
    filename = ("%s_%s_%s_3.pdf")% ((instance.medical_record.full_name).replace(" ","_"),instance.medical_record.phone,instance.date_booked.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Ho_Chi_Minh")).strftime("%d-%m-%y--%H-%M"))
    return os.path.join("{}/{}/medical_test/".format(instance.medical_record.pk,instance.pk),filename)