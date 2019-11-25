import humanize
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from myequis.models import Material
from myequis.models import Bicycle
from myequis.models import Record
from myequis.models import Component
from myequis.models import Part
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .forms import CreateRecordForm, EditPartForm, MountPartForm, DismountPartForm
from .forms import EditRecordForm
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from datetime import datetime, date
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class CreateRecordView(CreateView):

    def get(self, request, *args, **kwargs):
        # logger.warning("CreateRecordView GET request: {}".format(str(request)))

        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])

        # Find the best km as default value
        record = self.create_record(bicycle)

        # If called with data, clean() will be processed!
        form = CreateRecordForm(
            {'date': record.date,
             'km': record.km,
             'bicycle_id': record.bicycle.id,
             })

        template = loader.get_template('myequis/create_record.html')
        return HttpResponse(template.render({'record': record, 'form': form}, request))

    def post(self, request, *args, **kwargs):
        # logger.warning("CreateRecordView POST request.POST: {}".format(str(request.POST)))

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Create record canceled'" % reverse('myequis:list-records-url',
                                                                args=(kwargs['bicycle_id'],)))

        form = CreateRecordForm(request.POST)
        logger.warning("form: " + str(form))
        # logger.warning("form cleaned_data: " + str(form.cleaned_data))

        record = Record()
        record.date = form.cleaned_data['date']
        record.km = form.cleaned_data['km']
        record.bicycle = get_object_or_404(Bicycle, pk=form.cleaned_data['bicycle_id'])

        if form.is_valid():
            # logger.warning("is Valid. form.cleaned_data={}".format(str(form.cleaned_data)))
            form.check_data()
            # process the data in form.cleaned_data as required

            record.save()
            logger.warning("New record saved={}".format(str(record)))

            # redirect to a new URL:
            # see https://docs.djangoproject.com/en/dev/ref/urlresolvers/#django.core.urlresolvers.reverse
            # return HttpResponseRedirect(reverse('url_records', args=(record.bicycle.id,)))
            return HttpResponseRedirect(reverse('myequis:list-records-url', args=(record.bicycle.id,)))

        else:
            logger.warning("is not valid")
            template = loader.get_template('myequis/create_record.html')
            return HttpResponse(template.render({'record': record, 'form': form, }, request))

    @staticmethod
    def create_record(bicycle):
        """
        Returns new and unsaved Record with initialized data. Has no ID
        """
        record = Record()
        # logger.warning("Create new record: " + str(record.id))
        record.date = datetime.now()
        # logger.warning("Added date: " + str(record.date))
        record.bicycle = bicycle
        # logger.warning("NEW: " + str(record))

        records = Record.objects.filter(bicycle_id=bicycle.id).filter(date__lt=record.date).order_by('-date')

        if len(records) >= 1:
            r = records[0]
            # logger.warning("Found last record: id={} date={} km={}".format(str(r.id), str(r.date), str(r.km)))
            record.km = r.km
        else:
            # logger.warning("No previous records found")
            record.km = 0

        return record


class EditPartView(UpdateView):
    """
    Input: Part.id, Bicycle.id
    """

    def get(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])
        form = EditPartForm({

        })

        template = loader.get_template('myequis/edit_part.html')
        return HttpResponse(
            template.render({'bicycle': bicycle, 'part': part}, request))

    def post(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Editing {} canceled'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        template = loader.get_template('myequis/edit_part.html')
        return HttpResponse(template.render({}, request))


class MountPartView(CreateView):
    """
    Input: Part.id, Bicycle.id
    """

    def get(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        form = MountPartForm({
                'bicycle_id': bicycle.id,
                'selected_material': "",
        })

        template = loader.get_template('myequis/mount_part.html')
        return HttpResponse(
            template.render({
                'bicycle': bicycle,
                'part': part,
                'materials': self.select_materials(),
                'form': form,
            }, request))

    def post(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Mounting {} canceled'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        form = MountPartForm(request.POST)

        if form.is_valid():
            # logger.warning("selected_material: {}".format(str(form.cleaned_data['selected_material'])))
            material_under_edit = get_object_or_404(Material, pk=form.cleaned_data['selected_material'])
            record = get_object_or_404(Record, pk=form.cleaned_data['record_select'])
            logger.warning("record_sselect: {}".format(str(record)))
            material_under_edit.mount_record = record
            material_under_edit.dismount_record = None
            material_under_edit.part = part

            material_under_edit.save()
            logger.warning("Mounted: {}".format(str(material_under_edit)))

            return HttpResponseRedirect(
                "%s?message='{} mounted'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        else:
            logger.warning("is not valid")
            template = loader.get_template('myequis/mount_part.html')
            return HttpResponse(
                template.render({
                    'bicycle': bicycle,
                    'part': part,
                    'materials': self.select_materials(),
                    'form': form,
                }, request))

    @staticmethod
    def select_materials():
        return Material.objects.filter(
            (Q(mount_record=None) & Q(dismount_record=None) |
             (Q(mount_record__isnull=False) & Q(dismount_record__isnull=False)))
        )


class DismountPartView(UpdateView):
    """
    Input: Part.id, Bicycle.id
    """

    def get(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])
        my_material = get_object_or_404(Material, mount_record__bicycle_id=bicycle.id, part_id=part.id,
                                        dismount_record=None)

        logger.warning("material={}".format(my_material))

        form = DismountPartForm({
            'bicycle_id': bicycle.id,
            'selected_record': "",
            'material_id': my_material.id,
        })

        records = Record.objects.filter(bicycle_id=bicycle.id, date__gt=my_material.mount_record.date).order_by("-date")
        record_list = []
        for record in records:
            days = record.date - my_material.mount_record.date
            # logger.warning("duration={}".format(str(days.days)))
            record_list.append(
                dict(
                    id=record.id,
                    date=record.date,
                    km=record.km,
                    duration=days.days,
                    distance=record.km - my_material.mount_record.km,
                )
            )

        template = loader.get_template('myequis/dismount_part.html')
        return HttpResponse(
            template.render({
                'bicycle': bicycle,
                'part': part,
                'material': my_material,
                'records':  record_list,
                'form': form,
            }, request))

    def post(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Dismounting {} canceled'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        form = DismountPartForm(request.POST)

        if form.is_valid():
            # logger.warning("selected_material: {}".format(str(form.cleaned_data)))
            material_under_edit = get_object_or_404(Material, pk=form.cleaned_data['material_id'])
            record = get_object_or_404(Record, pk=form.cleaned_data['selected_record'])
            material_under_edit.dismount_record = record

            material_under_edit.save()
            logger.warning("Dismounted: {}".format(str(material_under_edit)))

            return HttpResponseRedirect(
                "%s?message='{} dismounted'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        template = loader.get_template('myequis/dismount_part.html')
        return HttpResponse(template.render({}, request))


class ExchangePartView(UpdateView):
    """
    Input: Part.id, Bicycle.id
    """

    def get(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])
        form = EditPartForm({

        })

        template = loader.get_template('myequis/exchange_part.html')
        return HttpResponse(
            template.render({'bicycle': bicycle, 'part': part}, request))

    def post(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Exchanging {} canceled'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        template = loader.get_template('myequis/exchange_part.html')
        return HttpResponse(template.render({}, request))


class EditRecordView(UpdateView):

    def get(self, request, *args, **kwargs):

        # logger.warning("EditRecordView GET request: {}".format(str(request)))

        record = get_object_or_404(Record, pk=kwargs['record_id'])

        form = EditRecordForm({
            'date': record.date,
            'km': record.km,
            'id': record.id})

        mounted = len(Material.objects.filter(mount_record_id=record.id))
        dismounted = len(Material.objects.filter(dismount_record_id=record.id))

        template = loader.get_template('myequis/edit_record.html')
        return HttpResponse(
            template.render({
                'record': record,
                'form': form,
                'materials': mounted + dismounted,
            }, request))

    def post(self, request, *args, **kwargs):
        # logger.warning("EditRecordView POST request.POST: {}".format(str(request.POST)))
        record = get_object_or_404(Record, pk=kwargs['record_id'])

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Edit record canceled'" % reverse('myequis:list-records-url',
                                                              args=(record.bicycle.id,)))

        record = get_object_or_404(Record, pk=kwargs['record_id'])

        if 'delete' in request.POST:
            logger.warning("Delete Record : {}".format(str(record)))
            record.delete()
            logger.warning("Done.")
            # redirect to a new URL:
            return HttpResponseRedirect(
                "%s?message='Dataset deleted'" % reverse('myequis:list-records-url', args=(record.bicycle.id,)))

        form = EditRecordForm(request.POST)

        logger.warning("Before is_valid ")
        if form.is_valid():
            # logger.warning("is Valid ")
            form.check_edit_record()
            # process the data in form.cleaned_data as required
            record.date = form.cleaned_data['date']
            record.km = form.cleaned_data['km']
            record.save()
            logger.warning("Record saved={}".format(str(record)))

            # redirect to a new URL:
            return HttpResponseRedirect(
                "%s?message='Dataset saved'" % reverse('myequis:list-records-url', args=(record.bicycle.id,)))

        else:
            # logger.warning("is not valid" )
            template = loader.get_template('myequis/edit_record.html')
            return HttpResponse(template.render({'record': record, 'form': form}, request))

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.check_edit_record(form.id, form.data, form.km)
        return super().form_valid(form)


def list_records(request, bicycle_id):
    """
    Get can have message from previous form 
    """
    # logger.warning("list_records GET request: {}".format(str(request)))

    records = Record.objects.filter(bicycle__id=bicycle_id).order_by('-date')

    bicycle = Bicycle.objects.get(pk=bicycle_id)
    template = loader.get_template('myequis/records.html')

    if 'message' in request.GET.keys():
        context = {
            'bicycle': bicycle,
            'records': records,
            'message': request.GET['message']
        }
    else:
        context = {
            'bicycle': bicycle,
            'records': records,
        }

    return HttpResponse(template.render(context, request))


def bicycle_detail(request, bicycle_id):
    """
    bicycle_detail.html
    """

    bicycle = Bicycle.objects.get(pk=bicycle_id)
    records = Record.objects.filter(bicycle__id=bicycle_id).order_by('-date')

    # Actual mounted
    materials = Material.objects.filter(mount_record__bicycle_id=bicycle.id).filter(dismount_record=None)

    componentDataList = []

    for component in Component.objects.all():
        componentData = dict()

        componentData['component_name'] = component.name

        parts = Part.objects.filter(component__id=component.id)

        component_has_materials = False
        partDataList = []

        for part in parts:
            partMaterial = next((m for m in materials if m.part.id == part.id), None)

            distance = ""
            if not partMaterial is None:
                component_has_materials = True
                # logger.warning("part={}".format(str(part)))
                # logger.warning("partMaterial={}".format(str(partMaterial)))

                if len(records) > 0:
                    distance = (records[0].km - partMaterial.mount_record.km)

            partDataList.append(dict(part=part, material=partMaterial, distance=distance, ))

        componentData['parts'] = partDataList
        componentData['has_materials'] = component_has_materials

        componentDataList.append(componentData)

    template = loader.get_template('myequis/bicycle_detail.html')

    context = {
        'bicycle': bicycle,
        'records': records[:2],  # Last two
        'componentDataList': componentDataList,
    }

    return HttpResponse(template.render(context, request))


def list_bicycle_parts(request, bicycle_id):
    """
    bicycle_parts.html
    """

    bicycle = Bicycle.objects.get(pk=bicycle_id)
    records = Record.objects.filter(bicycle__id=bicycle_id).order_by('-date')

    # Actual mounted
    materials = Material.objects.filter(mount_record__bicycle_id=bicycle.id).filter(dismount_record=None)

    component_data_list = []

    for component in Component.objects.all():
        component_data = dict()

        component_data['component_name'] = component.name

        parts = Part.objects.filter(component__id=component.id)

        part_data_list = []

        for part in parts:
            part_material = next((m for m in materials if m.part.id == part.id), None)

            distance = ""
            if part_material is not None:
                # logger.warning("part={}".format(str(part)))
                # logger.warning("partMaterial={}".format(str(part_material)))

                if len(records) > 0:
                    distance = (records[0].km - part_material.mount_record.km)

            # logger.warning("part={}".format(str(part)))
            part_data_list.append(dict(part=part, material=part_material, distance=distance, ))

        component_data['parts'] = part_data_list

        component_data_list.append(component_data)

    template = loader.get_template('myequis/bicycle_parts.html')

    if 'message' in request.GET.keys():
        context = {
            'bicycle': bicycle,
            'records': records[:2],  # Last two
            'componentDataList': component_data_list,
            'message': request.GET['message']
        }
    else:
        context = {
            'bicycle': bicycle,
            'records': records[:2],  # Last two
            'componentDataList': component_data_list,
        }

    return HttpResponse(template.render(context, request))


def index(request):
    bicycles = Bicycle.objects.order_by('name')

    materials = Material.objects.filter(mount_record=None).order_by('name')
    # .order_by('name')

    template = loader.get_template('myequis/index.html')
    context = {
        'bicycles': bicycles,
        'materials': materials
    }

    return HttpResponse(template.render(context, request))


def newmaterials(request):
    new_material_list = Material.objects.filter(mount_record=None)
    template = loader.get_template('myequis/newmaterials.html')
    context = {
        'new_material_list': new_material_list,
    }

    return HttpResponse(template.render(context, request))


def material(request, material_id):
    material = Material.objects.get(id=material_id)

    return HttpResponse("You're looking at material %s." % material.name)
