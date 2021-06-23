from django import forms
from django.forms import Select

from myequis.models import Record, Material
from datetime import datetime, timedelta
from django.utils.translation import ugettext as _
from bootstrap_datepicker_plus import DatePickerInput

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create Material
class ImportForm(forms.Form):

    importData = forms.FileField(label="Data File (ZIP)", required=False)

    # Will be set to true in POST, if save button pressed
    is_save = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # logger.warning("__init__() args={}".format(args[0]))

        self.is_save = 'save' in args[0]

    # Form class stores get data and clean will will called, every time data have been changed.
    def clean(self):
        # logger.warning("clean() self={}".format(str(self)))
        super(ImportForm, self).clean()


        # Only if save button pressed
        if self.is_save:
            self.check_data()

    #   Check if the give record values against the existing ones
    def check_data(self):
        logger.warning("import: check_data() clean_data={}".format(self.cleaned_data))

        # get the actual form data we have to check
        importData = self.cleaned_data['importData']

        if importData is None :
            raise forms.ValidationError(
                _("A file must be specified"),
                code="file_empty",
            )


# Create Material
class EditMaterialForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(
        attrs={'max_length': '50'}), required=False, label="Name")

    manufacture = forms.CharField(widget=forms.TextInput(
        attrs={'max_length': '30'}), required=False, label="Manufacture")

    size = forms.CharField(widget=forms.TextInput(
        attrs={'max_length': '20'}), required=False, label="Size")

    weight = forms.IntegerField(widget=forms.NumberInput(
        attrs={'size': '5'}), required=False,
        label="Weight [g]", min_value=0, max_value=99999)

    price = forms.DecimalField(widget=forms.NumberInput(
        attrs={'size': '8', 'decimal_places': '2'}), required=False,
        label="Price [€]", min_value=0, max_value=999999)

    comment = forms.CharField(widget=forms.TextInput(
        attrs={'max_length': '500'}), required=False, label="Comment")

    # Will be set to true in POST, if save button pressed
    is_save = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # logger.warning("__init__() args={}".format(args[0]))

        self.is_save = 'save' in args[0]

    # Form class stores get data and clean will will called, every time data have been changed.
    def clean(self):
        logger.warning("clean() self={}".format(str(self)))
        super(EditMaterialForm, self).clean()

        # Only if save button pressed
        if self.is_save:
            self.check_data()

    #   Check if the give record values against the existing ones
    def check_data(self):
        logger.warning("check_edit_material() clean_data={}".format(self.cleaned_data))

        # get the actual form data we have to check
        name = self.cleaned_data['name']
        manufacture = self.cleaned_data['manufacture']
        size = self.cleaned_data['size']
        weight = self.cleaned_data['weight']
        price = self.cleaned_data['price']
        comment = self.cleaned_data['comment']

        if len(name) < 1 :
            raise forms.ValidationError(
                _("A name must be specified"),
                code="material_name_empty",
                params={'name': name},
            )

        if len(manufacture) < 1 :
            raise forms.ValidationError(
                _("A manufacture must be specified"),
                code="material_manufacture_empty",
                params={'manufacture': manufacture},
            )

class CreateMaterialForm(forms.Form):

    name = forms.CharField(widget=forms.TextInput(
        attrs={'max_length': '50'}), required=False, label="Name")

    manufacture = forms.CharField(widget=forms.TextInput(
        attrs={'max_length': '30'}), required=False, label="Manufacture")

    size = forms.CharField(widget=forms.TextInput(
        attrs={'max_length': '20'}), required=False, label="Size")

    weight = forms.IntegerField(widget=forms.NumberInput(
        attrs={'size': '5'}), required=False,
        label="Weight [g]", min_value=0, max_value=99999)

    price = forms.DecimalField(widget=forms.NumberInput(
        attrs={'size': '8', 'decimal_places': '2'}), required=False,
        label="Price [€]", min_value=0, max_value=999999)

    comment = forms.CharField(widget=forms.TextInput(
        attrs={'max_length': '500'}), required=False, label="Comment")

    # Will be set to true in POST, if save button pressed
    is_save = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # logger.warning("__init__() args={}".format(args[0]))

        self.is_save = 'save' in args[0]

    # Form class stores get data and clean will will called, every time data have been changed.
    def clean(self):
        logger.warning("clean() self={}".format(str(self)))
        super(CreateMaterialForm, self).clean()

        # Only if save button pressed
        if self.is_save:
            self.check_data()

    #   Check if the give record values against the existing ones
    def check_data(self):
        logger.warning("check_create_material() clean_data={}".format(self.cleaned_data))

        # get the actual form data we have to check
        name = self.cleaned_data['name']
        manufacture = self.cleaned_data['manufacture']
        size = self.cleaned_data['size']
        weight = self.cleaned_data['weight']
        price = self.cleaned_data['price']
        comment = self.cleaned_data['comment']

        if len(name) < 1 :
            raise forms.ValidationError(
                _("A name must be specified"),
                code="material_name_empty",
                params={'name': name},
            )

        if len(manufacture) < 1 :
            raise forms.ValidationError(
                _("A manufacture must be specified"),
                code="material_manufacture_empty",
                params={'manufacture': manufacture},
            )


# Create Record
class CreateRecordForm(forms.Form):
    date = forms.DateField(
        input_formats=['%Y/%m/%d'],

        # See https://pypi.org/project/django-bootstrap-datepicker-plus/
        widget=DatePickerInput(format='%Y/%m/%d'),

        label="Date"
    )

    km = forms.IntegerField(widget=forms.NumberInput(
        attrs={'size': '10'}), label="KM", min_value=0, max_value=9999999)

    bicycle_id = forms.IntegerField(label='bicycle_id', widget=forms.HiddenInput())

    # Form class stores get data and clean will will called, every time data have been changed.
    def clean(self):
        logger.warning("clean() self={}".format(str(self)))
        super(CreateRecordForm, self).clean()
        self.check_data()

    #   Check if the give record values against the existing ones
    def check_data(self):
        # logger.warning("check_create_record() clean_data={}".format(self.cleaned_data))

        # get the actual form data we have to check
        date = self.cleaned_data['date']
        km = self.cleaned_data['km']

        # logger.warning("Check new record: date={} km={}".format(str(date), str(km)))
        # bicycle's existing records
        records = Record.objects.filter(bicycle_id=self.cleaned_data['bicycle_id'])

        for r in records:
            # logger.warning("Found record: id={} date={} km={}".format(str(r.id), str(r.date), str(r.km)))
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


class DeleteMountingForm(forms.Form):
    bicycle_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    mounting_id = forms.CharField(widget=forms.HiddenInput(), required=False)


class MountForm(forms.Form):

    record_select = forms.ChoiceField(label="Record", required=False, widget=Select())
    selected_material = forms.CharField(widget=forms.HiddenInput(), required=False)
    bicycle_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Will be set to true in POST, if save button pressed
    is_save = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # logger.warning("__init__() args={}".format(args[0]))
        records = Record.objects.filter(bicycle_id=args[0]['bicycle_id']).order_by('-date')
        # import pdb; pdb.set_trace()
        tuples = []
        for record in records:
            key = record.id
            value = "{} / {:,} km".format(record.date, record.km)
            t = (key, value)
            tuples.append(t)

        self.fields['record_select'].choices = tuples

        self.is_save = 'save' in args[0]

    def clean(self):
        logger.warning("clean() is_save={}".format(str(self.is_save)))
        # logger.warning("data={}".format(str(self.data)))
        # logger.warning("\nself={}\nENDSELF".format(str(self)))
        super(MountForm, self).clean()

        # Only if save button pressed
        if self.is_save:
            self.check_data()

    def check_data(self):

        if len(self.cleaned_data['selected_material']) == 0:
            raise forms.ValidationError(
                _("No material selected"),
                code="no_material_selected"
            )


class ExchangeMountingForm(forms.Form):

    selected_record = forms.CharField(widget=forms.HiddenInput(), required=False)
    bicycle_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    mounting_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    selected_material = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Will be set to true in POST, if save button pressed
    is_save = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # logger.warning("__init__() args={}".format(args[0]))

        self.is_save = 'save' in args[0]

    def clean(self):
        logger.warning("clean() is_save={}".format(str(self.is_save)))
        # logger.warning("data={}".format(str(self.data)))
        # logger.warning("\nself={}\nENDSELF".format(str(self)))
        super(ExchangeMountingForm, self).clean()

        # Only if save button pressed
        if self.is_save:
            self.check_data()

    def check_data(self):
        # logger.warning("data={}".format(str(self.data)))
        # logger.warning("cleaned_data={}".format(str(self.cleaned_data)))

        if len(self.cleaned_data['selected_record']) == 0:
            raise forms.ValidationError(
                _("No record selected"),
                code="no_record_selected"
            )

        if len(self.cleaned_data['selected_material']) == 0:
            raise forms.ValidationError(
                _("No material selected"),
                code="no_material_selected"
            )


class DismountForm(forms.Form):

    selected_record = forms.CharField(widget=forms.HiddenInput(), label='Records', required=False)
    bicycle_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    mounting_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    # Will be set to true in POST, if save button pressed
    is_save = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # logger.warning("__init__() args={}".format(args[0]))

        self.is_save = 'save' in args[0]

    def clean(self):
        logger.warning("clean() is_save={}".format(str(self.is_save)))
        # logger.warning("data={}".format(str(self.data)))
        # logger.warning("\nself={}\nENDSELF".format(str(self)))
        super(DismountForm, self).clean()

        # Only if save button pressed
        if self.is_save:
            self.check_data()

    def check_data(self):

        if len(self.cleaned_data['selected_record']) == 0:
            raise forms.ValidationError(
                _("No record selected"),
                code="no_record_selected"
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
        attrs={'size': '10'}), label="KM", min_value=0, max_value=9999999)

    # id = forms.IntegerField(label='id', widget=forms.HiddenInput())
    # bicycle_id = forms.IntegerField(label='bicycle_id', widget=forms.HiddenInput())
    id = forms.IntegerField(label='id', widget=forms.HiddenInput())

    def clean(self):
        # logger.warning("data={}".format(str(self.data)))
        # logger.warning("clean() self={}".format(str(self)))
        super(EditRecordForm, self).clean()
        self.check_edit_record()

    #   Check if the give record values against the existing ones
    def check_edit_record(self):
        # logger.warning("check_edit_record")

        # get the actual form data we have to check
        id = self.cleaned_data['id']
        date = self.cleaned_data['date']
        km = self.cleaned_data['km']

        # Persisted Record under edit
        record = Record.objects.get(pk=id)

        # raise forms.ValidationError("check_edit_record")

        # bicycle's others
        records = Record.objects.filter(bicycle_id=record.bicycle.id).exclude(id=id)

        for r in records:
            # logger.warning("Found record: " + str(r))
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
