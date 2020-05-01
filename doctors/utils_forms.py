from django import forms
from django.conf import settings



def clean_upload_file(file):
    if file:
        content_type = file.content_type.split("/")[1]
        if content_type in settings.CONTENT_TYPES:
            
            if file.size > settings.MAX_UPLOAD_SIZE:
                raise forms.ValidationError("File upload của bạn trên 5M. Làm ơn chọn file dưới 5M!")
            else:
                
                return file
        else:
            raise forms.ValidationError("Bạn nên upload định dạng PDF")

    return file




    