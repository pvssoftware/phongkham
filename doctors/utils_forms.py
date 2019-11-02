from django import forms



class ValidOpeningTimeForm(forms.ModelForm):

    def clean_mon_opening(self):
        v = self.cleaned_data["mon_opening"]
        if v == "":
            return None
        else:
            
            return v
    def clean_mon_closing(self):
        v = self.cleaned_data["mon_closing"]
        if v == "":
            return None
        else:
            
            return v
    def clean_tue_opening(self):
        v = self.cleaned_data["tue_opening"]
        print("tue",v)
        if v == "":
            
            return None
        else:
            
            return v
    def clean_tue_closing(self):
        v = self.cleaned_data["tue_closing"]
        if v == "":
            return None
        else:
            return v
    def clean_wed_opening(self):
        v = self.cleaned_data["wed_opening"]
        if v == "":
            return None
        else:
            return v
    def clean_wed_closing(self):
        v = self.cleaned_data["wed_closing"]
        if v == "":
            return None
        else:
            return v
    def clean_thu_opening(self):
        v = self.cleaned_data["thu_opening"]
        if v == "":
            return None
        else:
            return v
    def clean_thu_closing(self):
        v = self.cleaned_data["thu_closing"]
        if v == "":
            return None
        else:
            return v
    def clean_fri_opening(self):
        v = self.cleaned_data["fri_opening"]
        if v == "":
            return None
        else:
            return v
    def clean_fri_closing(self):
        v = self.cleaned_data["fri_closing"]
        if v == "":
            return None
        else:
            return v
    def clean_sat_opening(self):
        v = self.cleaned_data["sat_opening"]
        if v == "":
            return None
        else:
            return v
    def clean_sat_closing(self):
        v = self.cleaned_data["sat_closing"]
        if v == "":
            return None
        else:
            return v
    def clean_sun_opening(self):
        v = self.cleaned_data["sun_opening"]
        if v == "":
            return None
        else:
            return v
    def clean_sun_closing(self):
        v = self.cleaned_data["sun_closing"]
        if v == "":
            return None
        else:
            return v
    