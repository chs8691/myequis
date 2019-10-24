from django import forms
from myequis.models import Record
from datetime import datetime, timedelta
from django.utils.translation import ugettext as _
from bootstrap_datepicker_plus import DatePickerInput

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create Record
class CreateRecordForm(forms.Form):
    
    date = forms.DateField(
        input_formats=['%Y/%m/%d'],
        
        # See https://pypi.org/project/django-bootstrap-datepicker-plus/
        widget=DatePickerInput(format='%Y/%m/%d'),
        
        label="Date"
    )
    
    km = forms.IntegerField(widget=forms.NumberInput(
                attrs={'size':'10'}), label="KM",  min_value=0, max_value=9999999)
    
    bicycle_id = forms.IntegerField(label='bicycle_id', widget=forms.HiddenInput())
    
    # Form class stores get data and clean will will called, every time data have been changed.
    def clean(self):
        logger.warning("clean() self={}".format(str(self)))
        super(CreateRecordForm, self).clean()
        self.check_create_record()
        
        
#   Check if the give record values against the existing ones        
    def check_create_record(self):
        #logger.warning("check_create_record() clean_data={}".format(self.cleaned_data))
        
        #get the actual form data we have to check
        date = self.cleaned_data['date']
        km = self.cleaned_data['km']
        
        #logger.warning("Check new record: date={} km={}".format(str(date), str(km)))
        # bicycle's existing records
        records = Record.objects.filter(bicycle_id=self.cleaned_data['bicycle_id'])
        
        for r in records:
            #logger.warning("Found record: id={} date={} km={}".format(str(r.id), str(r.date), str(r.km)))
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
    
 
            
# Edit Record
class EditRecordForm(forms.Form):

    date = forms.DateField(
        input_formats=['%Y/%m/%d'],
        
        # See https://pypi.org/project/django-bootstrap-datepicker-plus/
        widget=DatePickerInput(format='%Y/%m/%d'),
        
        label="Date"
    )
    
    km = forms.IntegerField(widget=forms.NumberInput(
                attrs={'size':'10'}), label="KM",  min_value=0, max_value=9999999)
    
    #id = forms.IntegerField(label='id', widget=forms.HiddenInput())
    #bicycle_id = forms.IntegerField(label='bicycle_id', widget=forms.HiddenInput())
    id = forms.IntegerField(label='id', widget=forms.HiddenInput())
    
    
    def clean(self):
        logger.warning("clean() self={}".format(str(self)))
        super(EditRecordForm, self).clean()
        self.check_edit_record()
        

#   Check if the give record values against the existing ones        
    def check_edit_record(self):
        logger.warning("check_edit_record")
        
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
            logger.warning("Found record: " + str(r))
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
    
    
