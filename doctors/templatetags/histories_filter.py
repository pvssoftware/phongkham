from django import template



register = template.Library()



@register.simple_tag(takes_context=True)
def histories_filter(context,medical_record):
    histories = medical_record.medicalhistory_set.filter(date_booked__range=(context["from_date"],context["to_date"]))

    return {"histories":histories}