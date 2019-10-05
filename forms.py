from django import forms
from myequis.models import Record
from datetime import datetime, timedelta
from django.utils.translation import ugettext as _
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Edit Record
class RecordForm(forms.Form):
    
    # Switch for POST-only checks
    custom_validations = False
    
    date = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control datetimepicker-input',
            'data-target': '#datetimepicker1'
        }),
        label="Date"
    )
    
    km = forms.IntegerField(widget=forms.NumberInput(
                attrs={'size':'10'}), label="KM",  min_value=0, max_value=9999999)
    
    id = forms.IntegerField(label='id', widget=forms.HiddenInput())
    
    # must be called to enable custom validations with POST
    def enable_validations(self):
        self.custom_validations = True
    
    def clean(self):
        clean_data = super().clean()

        if self.custom_validations:
            self.check_edit_record()
        

#   Check if the give record values against the existing ones        
    def check_edit_record(self):
        #logger.warning("LOGGER: " + str(self.cleaned_data))
        #raise forms.ValidationError("TEST")
        #logger.warning("LOGGER: " + str("After Raise"))
        
        #get the actual form data we have to check
        id = self.cleaned_data['id']
        date = self.cleaned_data['date']
        km = self.cleaned_data['km']

        # Persisted Record under edit
        record = Record.objects.get(pk=id)

        
        #raise forms.ValidationError("check_edit_record")
        
        # bicycle's others
        records = Record.objects.filter(bicycle_id=record.bicycle.id).exclude(id=id)
        
        for r in records:
            logger.warning("LOGGER: " + str(r))
            delta = date - r.date
            
            if delta.days == 0:
                raise forms.ValidationError(
                    _("Record for date %(date)s already exists"), 
                    code="record_date_dublicate",
                    params={'date': date}, 
                    )
            
            if delta.days > 0 and km < r.km:
                raise forms.ValidationError(
                    _("%(km)d < %(r_km)d km of record for date %(r_date)s"), 
                    code="record_km_to_low",
                    params={'km': km, 'r_km': r.km, 'r_date': r.date}, 
                    )
            
            if delta.days < 0 and km > r.km:
                raise forms.ValidationError(
                    _("%(km)d > %(r_km)d km of record for date %(r_date)s"), 
                    code="record_km_to_high",
                    params={'km': km, 'r_km': r.km, 'r_date': r.date}, 
                    )
            
    
    
