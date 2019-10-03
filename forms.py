from django import forms
from myequis.models import Record
from datetime import datetime, timedelta
from django.utils.translation import ugettext as _
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Edit Record
class RecordForm(forms.Form):
    custom_validations = False
    date = forms.DateField(label='Date')   
    km = forms.IntegerField(label='KM', min_value=0)
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
                    code="record_date_dublicate",
                    params={'km': km, 'r_km': r.km, 'r_date': r.date}, 
                    )
            
            if delta.days < 0 and km > r.km:
                raise forms.ValidationError(
                    _("%(km)d > %(r_km)d km of record for date %(r_date)s"), 
                    code="record_date_dublicate",
                    params={'km': km, 'r_km': r.km, 'r_date': r.date}, 
                    )
            
    
    
