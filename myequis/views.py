import humanize
from django.db.models import Q, OuterRef, Exists, Subquery
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from myequis.models import Material, Mounting
from myequis.models import Bicycle
from myequis.models import Record
from myequis.models import Component
from myequis.models import Part
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .forms import CreateRecordForm, DeleteMountingForm, MountForm, DismountForm, ExchangeMountingForm
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


class DeleteMountingView(UpdateView):

    def get(self, request, *args, **kwargs):

        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        my_mounting = get_object_or_404(Mounting, pk=Mounting.objects.filter(part_id=part.id,
                                                                             mount_record__bicycle_id=bicycle.id,
                                                                             dismount_record__isnull=True,
                                                                             )[0].id)
        logger.warning("mounting={}".format(str(my_mounting)))
        form = DeleteMountingForm({
            'mounting_id': my_mounting.id,
            'bicycle_id': bicycle.id,
            'inactive': False,
        })

        template = loader.get_template('myequis/delete_mounting.html')
        return HttpResponse(
            template.render(
                {
                    'bicycle': bicycle,
                    'part': part,
                    'mounting': my_mounting,
                    'form': form,
                }, request))

    def post(self, request, *args, **kwargs):
        # logger.warning("post={}".format(request.POST))
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Delete mounting for Part {} canceled'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        # logger.warning("Before mounting")
        mounting = get_object_or_404(Mounting, pk=request.POST['mounting_id'])
        # logger.warning("After mounting")

        form = DeleteMountingForm(request.POST)

        if 'delete' in request.POST:
            logger.warning("Delete Mounting : {}".format(str(mounting)))
            mounting.delete()
            logger.warning("Done.")
            # redirect to a new URL:
            return HttpResponseRedirect(
                "%s?message='Mounting deleted from part {}'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        else:
            # logger.warning("delete not in POST")
            template = loader.get_template('myequis/delete_mounting.html')
            return HttpResponse(
                template.render(
                    {
                        'bicycle': bicycle,
                        'part': part,
                        'mounting': mounting,
                        'form': form,
                    }, request))

    @staticmethod
    def select_materials():
        return Material.objects.annotate(mounted=Exists(
            Mounting.objects.filter(dismount_record=None, material=OuterRef('pk')))) \
            .filter(mounted=False) \
            .order_by('name')


class MountMaterialView(CreateView):
    """
    Input: Part.id, Bicycle.id
    """

    def get(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        form = MountForm({
                'bicycle_id': bicycle.id,
                'selected_material': "",
        })

        template = loader.get_template('myequis/mount_material.html')
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

        form = MountForm(request.POST)

        if form.is_valid():
            # logger.warning("selected_material: {}".format(str(form.cleaned_data['selected_material'])))
            material_under_edit = get_object_or_404(Material, pk=form.cleaned_data['selected_material'])
            record = get_object_or_404(Record, pk=form.cleaned_data['record_select'])
            logger.warning("record_select: {}".format(str(record)))

            mounting = Mounting()
            mounting.mount_record = record
            mounting.material = material_under_edit
            mounting.part = part
            mounting.save()
            logger.warning("New mounting created: {}".format(str(mounting)))

            return HttpResponseRedirect(
                "%s?message='{} mounted'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        else:
            logger.warning("is not valid")
            template = loader.get_template('myequis/mount_material.html')
            return HttpResponse(
                template.render({
                    'bicycle': bicycle,
                    'part': part,
                    'materials': self.select_materials(),
                    'form': form,
                }, request))

    @staticmethod
    def select_materials():
        return Material.objects.annotate(mounted=Exists(
            Mounting.objects.filter(dismount_record=None, material=OuterRef('pk')))) \
            .filter(mounted=False) \
            .order_by('name')


class DismountMaterialView(UpdateView):
    """
    Input: Part.id, Bicycle.id
    """

    def get(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        my_mounting = get_object_or_404(Mounting, pk=Mounting.objects.filter(part_id=part.id,
                                                                             mount_record__bicycle_id=bicycle.id,
                                                                             dismount_record__isnull=True,
                                                                             )[0].id)
        logger.warning("mounting={}".format(str(my_mounting)))

        form = DismountForm({
            'bicycle_id': bicycle.id,
            'selected_record': "",
            'mounting_id': my_mounting.id,
        })

        records = Record.objects.filter(bicycle_id=bicycle.id, date__gte=my_mounting.mount_record.date).order_by("-date")
        record_list = []
        for record in records:
            days = record.date - my_mounting.mount_record.date
            # logger.warning("duration={}".format(str(days.days)))
            record_list.append(
                dict(
                    id=record.id,
                    date=record.date,
                    km=record.km,
                    duration=days.days,
                    distance=record.km - my_mounting.mount_record.km,
                )
            )

        template = loader.get_template('myequis/dismount_material.html')
        return HttpResponse(
            template.render({
                'bicycle': bicycle,
                'part': part,
                'mounting': my_mounting,
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

        form = DismountForm(request.POST)

        if form.is_valid():
            # logger.warning("selected_material: {}".format(str(form.cleaned_data)))
            mounting_under_edit = get_object_or_404(Mounting, pk=form.cleaned_data['mounting_id'])
            record = get_object_or_404(Record, pk=form.cleaned_data['selected_record'])
            mounting_under_edit.dismount_record = record

            mounting_under_edit.save()
            logger.warning("Dismounted: {}".format(str(mounting_under_edit)))

            return HttpResponseRedirect(
                "%s?message='{} dismounted'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        template = loader.get_template('myequis/dismount_material.html')
        return HttpResponse(template.render({}, request))


class ExchangeMaterialView(UpdateView):
    """
    Input: Part.id, Bicycle.id
    """

    def get(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        my_mounting = get_object_or_404(Mounting, pk=Mounting.objects.filter(part_id=part.id,
                                                                             mount_record__bicycle_id=bicycle.id,
                                                                             dismount_record__isnull=True,
                                                                             )[0].id)

        form = ExchangeMountingForm({
            'bicycle_id': bicycle.id,
            'selected_record': "",
            'selected_material': "",
            'mounting_id': my_mounting.id,
        })

        template = loader.get_template('myequis/exchange_material.html')
        return HttpResponse(
            template.render({
                'bicycle': bicycle,
                'part': part,
                'mounting': my_mounting,
                'records': self.select_records(bicycle, my_mounting),
                'materials': self.select_materials(),
                'form': form,
            }, request))

    def post(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Exchanging {} canceled'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        form = ExchangeMountingForm(request.POST)
        # logger.warning("form: {}".format(str(form.data)))
        dis_mounting = get_object_or_404(Mounting, pk=form.data['mounting_id'])

        if form.is_valid():
            # logger.warning("selected_material: {}".format(str(form.cleaned_data['selected_material'])))
            selected_record = get_object_or_404(Record, pk=form.cleaned_data['selected_record'])
            selected_material = get_object_or_404(Material, pk=form.cleaned_data['selected_material'])
            # logger.warning("record_select: {}".format(str(selected_record)))

            dis_mounting.dismount_record = selected_record
            dis_mounting.part = part
            dis_mounting.save()
            logger.warning("Mounting updated: {}".format(str(dis_mounting)))

            new_mounting = Mounting()
            new_mounting.mount_record = selected_record
            new_mounting.material = selected_material
            new_mounting.part = part
            new_mounting.save()
            logger.warning("New mounting created: {}".format(str(new_mounting)))

            return HttpResponseRedirect(
                "%s?message='{} mounted'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        else:
            logger.warning("is not valid")
            template = loader.get_template('myequis/exchange_material.html')
            return HttpResponse(
                template.render({
                    'bicycle': bicycle,
                    'mounting': dis_mounting,
                    'part': part,
                    'records': self.select_records(bicycle, dis_mounting),
                    'materials': self.select_materials(),
                    'form': form,
                }, request))

    @staticmethod
    def select_materials():
        return Material.objects.annotate(mounted=Exists(
            Mounting.objects.filter(dismount_record=None, material=OuterRef('pk')))) \
            .filter(mounted=False) \
            .order_by('name')

    @staticmethod
    def select_records(bicycle, mounting):
        records = Record.objects.filter(bicycle_id=bicycle.id, date__gte=mounting.mount_record.date).order_by("-date")
        record_list = []
        for record in records:
            days = record.date - mounting.mount_record.date
            # logger.warning("duration={}".format(str(days.days)))
            record_list.append(
                dict(
                    id=record.id,
                    date=record.date,
                    km=record.km,
                    duration=days.days,
                    distance=record.km - mounting.mount_record.km,
                )
            )
        return record_list


class EditRecordView(UpdateView):

    def get(self, request, *args, **kwargs):

        # logger.warning("EditRecordView GET request: {}".format(str(request)))

        record = get_object_or_404(Record, pk=kwargs['record_id'])

        form = EditRecordForm({
            'date': record.date,
            'km': record.km,
            'id': record.id})

        mounted = len(Mounting.objects.filter(mount_record_id=record.id))
        dismounted = len(Mounting.objects.filter(dismount_record_id=record.id))

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
    materials = Material.objects.annotate(mounted=Exists(
        Mounting.objects.filter(dismount_record=None, material=OuterRef('pk'))))\
        .filter(mounted=True)\
        .order_by('name')

    # All actual Mountings for this bicycle
    mountings = Mounting.objects.annotate(
        bicycle_found=Exists(
            Record.objects.filter(bicycle_id=bicycle.id)
        )
    ).filter(bicycle_found=True, dismount_record=None)
    logger.warning("mountings={}".format(str(mountings)))

    component_data_list = []

    for component in Component.objects.filter(species_id=bicycle.species.id):
        component_data = dict()

        component_data['component_name'] = component.name

        parts = Part.objects.filter(component__id=component.id)

        component_has_materials = False
        part_data_list = []

        for part in parts:
            mounting = next((m for m in mountings if m.part.id == part.id), None)
            if mounting is not None:
                part_material = mounting.material
            else:
                part_material = None

            distance = ""
            if part_material is not None:
                component_has_materials = True
                distance = 0
                # logger.warning("part={}".format(str(part)))
                # logger.warning("partMaterial={}".format(str(part_material)))

                # Material can be mounted multiple times and in different bicycles
                for mounting in Mounting.objects.filter(material_id=part_material.id):
                    if mounting.dismount_record is None:
                        # actual mounted
                        distance += records[0].km - mounting.mount_record.km
                    else:
                        # Materials history
                        distance += mounting.dismount_record.km - mounting.mount_record.km

            part_data_list.append(dict(part=part, material=part_material, mounting=mounting, distance=distance, ))

        if component_has_materials:
            component_data['parts'] = part_data_list
            component_data['has_materials'] = component_has_materials

            component_data_list.append(component_data)

    template = loader.get_template('myequis/bicycle_detail.html')

    context = {
        'bicycle': bicycle,
        'records': records[:2],  # Last two
        'componentDataList': component_data_list,
    }

    return HttpResponse(template.render(context, request))


def list_bicycle_parts(request, bicycle_id):
    """
    bicycle_parts.html
    """

    bicycle = Bicycle.objects.get(pk=bicycle_id)
    records = Record.objects.filter(bicycle__id=bicycle_id).order_by('-date')

    # All actual Mountings for this bicycle
    mountings = Mounting.objects.annotate(
        bicycle_found=Exists(
            Record.objects.filter(bicycle_id=bicycle.id)
        )
    ).filter(bicycle_found=True, dismount_record=None)

    # logger.warning("mountings={}".format(str(mountings)))

    component_data_list = []

    for component in Component.objects.filter(species_id=bicycle.species.id):
        component_data = dict()

        component_data['component_name'] = component.name

        parts = Part.objects.filter(component__id=component.id)

        part_data_list = []

        for part in parts:
            mounting = next((m for m in mountings if m.part.id == part.id), None)
            if mounting is not None:
                part_material = mounting.material
            else:
                part_material = None

            distance = ""
            if part_material is not None:
                distance = 0
                # logger.warning("part={}".format(str(part)))
                # logger.warning("partMaterial={}".format(str(part_material)))

                # Material can be mounted multiple times and in different bicycles
                for mounting in Mounting.objects.filter(material_id=part_material.id):
                    if mounting.dismount_record is None:
                        # actual mounted
                        distance += records[0].km - mounting.mount_record.km
                    else:
                        # Materials history
                        distance += mounting.dismount_record.km - mounting.mount_record.km

            # logger.warning("part={}".format(str(part)))
            part_data_list.append(dict(part=part, material=part_material, distance=distance, mounting=mounting))

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


def list_bicycle_history(request, bicycle_id):
    """
    bicycle_history.html
    """

    bicycle = Bicycle.objects.get(pk=bicycle_id)

    # All actual Mountings for this bicycle
    mountings = Mounting.objects.annotate(
        bicycle_found=Exists(
            Record.objects.filter(bicycle_id=bicycle.id)
        )
    ).filter(bicycle_found=True, dismount_record=None)

    # logger.warning("mountings={}".format(str(mountings)))

    component_data_list = []

    for component in Component.objects.filter(species_id=bicycle.species.id):
        component_data = dict()

        component_data['component_name'] = component.name

        parts = Part.objects.filter(component__id=component.id)

        part_data_list = []

        for part in parts:
            mounting = next((m for m in mountings if m.part.id == part.id), None)
            if mounting is not None:
                part_material = mounting.material
            else:
                part_material = None

            distance = ""
            if part_material is not None:
                distance = 0
                # logger.warning("part={}".format(str(part)))
                # logger.warning("partMaterial={}".format(str(part_material)))

                # Material can be mounted multiple times and in different bicycles
                for mounting in Mounting.objects.filter(material_id=part_material.id):
                    if mounting.dismount_record is None:
                        logger.warning("mounting={}".format(str(mounting)))
                        # actual mounted
                        # distance += records[0].km - mounting.mount_record.km
                    else:
                        # Materials history
                        distance += mounting.dismount_record.km - mounting.mount_record.km

            # logger.warning("part={}".format(str(part)))
            part_data_list.append(dict(part=part, material=part_material, distance=distance, mounting=mounting))

        component_data['parts'] = part_data_list

        component_data_list.append(component_data)

    template = loader.get_template('myequis/bicycle_history.html')

    if 'message' in request.GET.keys():
        context = {
            'bicycle': bicycle,
            'componentDataList': component_data_list,
            'message': request.GET['message']
        }
    else:
        context = {
            'bicycle': bicycle,
            'componentDataList': component_data_list,
        }

    return HttpResponse(template.render(context, request))


def index(request):
    bicycles = Bicycle.objects.order_by('name')

    # Materials without actual mounted items
    materials = Material.objects.annotate(mounted=Exists(
        Mounting.objects.filter(dismount_record=None, material=OuterRef('pk'))))\
        .filter(mounted=False)\
        .order_by('name')

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
