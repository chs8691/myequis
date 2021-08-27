import logging
import io
import zipfile


from datetime import datetime
from tablib import Dataset, UnsupportedFormat
from django.db import DatabaseError, transaction
from django.db.models import Q, OuterRef, Exists, Subquery
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic.edit import UpdateView, CreateView
from os import path
from myequis.models import Material, Mounting, Bicycle, Record, Component, Part, Species
from .forms import CreateRecordForm, CreateMaterialForm, DeleteMountingForm, MountForm, DismountForm, ExchangeMountingForm, EditRecordForm, EditMaterialForm, ImportForm

from .resources import BicycleResource, ComponentResource, MaterialResource, MountingResource, PartResource, RecordResource, SpeciesResource

# Get an instance of a logger
logger = logging.getLogger(__name__)


def zip_files(files, suffix):
    outfile = io.BytesIO()
    with zipfile.ZipFile(outfile, 'w') as zf:
        for n in files:
            zf.writestr("{}.{}".format(n["name"], suffix), n["data"])
    return outfile.getvalue()


def unzip_files(zip_file):
    """
    returs dictionary for every data type
    """

    ret = dict()

    with zipfile.ZipFile(zip_file, 'r') as z:
        logger.warning(f"ZipFile list:{z.namelist()}")

        for n in z.namelist():
            dataset = Dataset()
            (name, suffix) = path.splitext(n)
            suffix = suffix[1:]
            logger.warning(
                f"unzip_files name and suffix = {name} and {suffix}")
            with z.open(n) as myfile:
                ret[name] = dataset.load(
                    myfile.read().decode('utf-8'), format=suffix)

    # logger.warning(f"unzip_files ret = {ret}")

    return ret


class ImportView(LoginRequiredMixin, CreateView):

    def get(self, request, *args, **kwargs):
        logger.warning("ImportView GET request: {}".format(str(request)))

        # If called with data, clean() will be processed!
        form = ImportForm({})

        template = loader.get_template('myequis/import.html')
        return HttpResponse(template.render({
            'form': form,
            # 'import_disabled': "true", No good idea - give the user a chance to decide by himself
        }, request))

    def post(self, request, *args, **kwargs):
        logger.warning("ImportView POST request.POST: {} request.FILES:{}".format(
            str(request.POST), str(request.FILES)))

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Import canceled'" % reverse('myequis:index-url'))

        form = ImportForm(request.POST, request.FILES)
        # logger.warning("form: " + str(form))
        # logger.warning("form cleaned_data: " + str(form.cleaned_data))

        output = []

        if 'import' in request.POST:
            logger.warning("import")

        # logger.warning(f"importData={request.FILES['importData'].name}")

        if form.is_valid():
            logger.warning("is valid. form.cleaned_data={}".format(
                str(form.cleaned_data)))

            form.check_data()

            logger.warning(f"request={request.FILES['importData']}")
            data_count = 0
            error = False

            try:
                datasets = unzip_files(request.FILES['importData'])
                logger.warning(f"datasets={datasets}")

            except (UnsupportedFormat, MultiValueDictKeyError) as e:
                logger.error(e)
                message = str(e)
                error = True

            if error is False:

                try:
                    with transaction.atomic():
                        output.append(
                            f"Loaded file: {request.FILES['importData']}")

                        Mounting.objects.all().delete()
                        Material.objects.all().delete()
                        Record.objects.all().delete()
                        Bicycle.objects.all().delete()
                        Part.objects.all().delete()
                        Component.objects.all().delete()
                        Species.objects.all().delete()

                        species_resource = SpeciesResource()
                        species_data = datasets["Species"]
                        data_count = data_count + len(species_data)
                        logger.warning(f"species_data={species_data}")
                        output.append(
                            f"Species: {len(Species.objects.all())} <-- {len(species_data)}")
                        result_species = species_resource.import_data(
                            species_data)
                        if result_species.has_errors():
                            message = "Invalid Species data"
                        error = error or result_species.has_errors()

                        component_resource = ComponentResource()
                        component_data = datasets["Component"]
                        data_count = data_count + len(component_data)
                        logger.warning(f"component_data={component_data}")
                        output.append(
                            f"Component: {len(Component.objects.all())} <-- {len(component_data)}")
                        result_component = component_resource.import_data(
                            component_data)
                        if result_component.has_errors():
                            message = "Invalid Components data"
                        error = error or result_component.has_errors()

                        part_resource = PartResource()
                        part_data = datasets["Part"]
                        data_count = data_count + len(part_data)
                        logger.warning(f"part_data={part_data}")
                        output.append(
                            f"Part: {len(Part.objects.all())} <-- {len(part_data)}")
                        result_part = part_resource.import_data(part_data)
                        if result_part.has_errors():
                            message = "Invalid Parts data"
                        error = error or result_part.has_errors()

                        bicycle_resource = BicycleResource()
                        bicycle_data = datasets["Bicycle"]
                        data_count = data_count + len(bicycle_data)
                        logger.warning(f"bicycle_data={bicycle_data}")
                        output.append(
                            f"Bicycle: {len(Bicycle.objects.all())} <-- {len(bicycle_data)}")
                        result_bicycle = bicycle_resource.import_data(
                            bicycle_data)
                        if result_bicycle.has_errors():
                            message = "Invalid Bicycles data"
                        error = error or result_bicycle.has_errors()

                        record_resource = RecordResource()
                        record_data = datasets["Record"]
                        data_count = data_count + len(record_data)
                        logger.warning(f"record_data={record_data}")
                        output.append(
                            f"Record: {len(Record.objects.all())} <-- {len(record_data)}")
                        result_record = record_resource.import_data(
                            record_data)
                        if result_record.has_errors():
                            message = "Invalid Records data"
                        error = error or result_record.has_errors()

                        material_resource = MaterialResource()
                        material_data = datasets["Material"]
                        data_count = data_count + len(material_data)
                        logger.warning(f"material_data={material_data}")
                        output.append(
                            f"Material: {len(Material.objects.all())} <-- {len(material_data)}")
                        result_material = material_resource.import_data(
                            material_data)
                        if result_material.has_errors():
                            message = "Invalid Materials data"
                        error = error or result_material.has_errors()

                        mounting_resource = MountingResource()
                        mounting_data = datasets["Mounting"]
                        data_count = data_count + len(mounting_data)
                        logger.warning(f"mounting_data={mounting_data}")
                        output.append(
                            f"Mounting: {len(Mounting.objects.all())} <-- {len(mounting_data)}")
                        result_mounting = mounting_resource.import_data(
                            mounting_data)
                        if result_mounting.has_errors():
                            message = "Invalid Mountings data"
                        error = error or result_mounting.has_errors()

                except DatabaseError:
                    logger.warning(f"DatabaseError occurred={e}")

            if error:
                logger.warning("import failed")
                template = loader.get_template('myequis/import.html')
                return HttpResponse(template.render({
                    'form': form,
                    'output': output,
                    'message': "ERROR:" + message,
                }, request))

            # redirect to a new URL:
            # see https://docs.djangoproject.com/en/dev/ref/urlresolvers/#django.core.urlresolvers.reverse
            # return HttpResponseRedirect(reverse('url_records', args=(record.bicycle.id,)))
            return HttpResponseRedirect(
                "%s?message='{} dataset imported'".format(data_count)
                % reverse('myequis:index-url'))

        else:
            logger.warning("is not valid")
            template = loader.get_template('myequis/import.html')
            return HttpResponse(template.render({
                'form': form,
            }, request))


def xxximport_data(request):

    if request.method == 'GET':
        template = loader.get_template('myequis/import.html')
        return HttpResponse(template.render({
        }, request))

    if request.method == 'POST':

        output = []

        logger.warning(f"request={request.FILES['importData']}")

        datasets = unzip_files(request.FILES['importData'])
        logger.warning(f"datasets={datasets}")

        bicycle_resource = BicycleResource()
        bicycle_data = datasets["Bicycle"]
        logger.warning(f"bicycle_data={bicycle_data}")
        result_bicycle = bicycle_resource.import_data(bicycle_data, dry_run=dry_run
                                                      )
        output.append(
            f"Bicycle: {len(Bicycle.objects.all())} <-- {len(bicycle_data)}")
        if result_bicycle.has_errors():
            message = "Invalid Bicycles data"

        component_resource = ComponentResource()
        component_data = datasets["Component"]
        logger.warning(f"component_data={component_data}")
        result_component = component_resource.import_data(component_data, dry_run=dry_run
                                                          )
        output.append(
            f"Component: {len(Component.objects.all())} <-- {len(component_data)}")
        if result_component.has_errors():
            message = "Invalid Components data"

        material_resource = MaterialResource()
        material_data = datasets["Material"]
        logger.warning(f"material_data={material_data}")
        result_material = material_resource.import_data(material_data, dry_run=dry_run
                                                        )
        output.append(
            f"Material: {len(Material.objects.all())} <-- {len(material_data)}")
        if result_material.has_errors():
            message = "Invalid Materials data"

        mounting_resource = MountingResource()
        mounting_data = datasets["Mounting"]
        logger.warning(f"mounting_data={mounting_data}")
        result_mounting = mounting_resource.import_data(mounting_data, dry_run=dry_run
                                                        )
        output.append(
            f"Mounting: {len(Mounting.objects.all())} <-- {len(mounting_data)}")
        if result_mounting.has_errors():
            message = "Invalid Mountings data"

        part_resource = PartResource()
        part_data = datasets["Part"]
        logger.warning(f"part_data={part_data}")
        result_part = part_resource.import_data(part_data, dry_run=dry_run
                                                )
        output.append(f"Part: {len(Part.objects.all())} <-- {len(part_data)}")
        if result_part.has_errors():
            message = "Invalid Parts data"

        record_resource = RecordResource()
        record_data = datasets["Record"]
        logger.warning(f"record_data={record_data}")
        result_record = record_resource.import_data(record_data, dry_run=dry_run
                                                    )
        output.append(
            f"Record: {len(Record.objects.all())} <-- {len(record_data)}")
        if result_record.has_errors():
            message = "Invalid Records data"

        species_resource = SpeciesResource()
        species_data = datasets["Species"]
        logger.warning(f"species_data={species_data}")
        result_species = species_resource.import_data(species_data, dry_run=dry_run
                                                      )
        output.append(
            f"Species: {len(Species.objects.all())} <-- {len(species_data)}")
        if result_species.has_errors():
            message = "Invalid Species data"

        # if not result.has_errors():
            # Import now
            # species_resource.import_data(dataset, dry_run=False)

    # return render(request, 'myequis/import.html')
    template = loader.get_template('myequis/import.html')
    return HttpResponse(template.render({
        'output': output,
    }, request))


def export_data(request):
    if request.method == 'POST':

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Export closed'" % reverse('myequis:index-url'))


        # Get selected option from form
        file_format = request.POST['file-format']

        if file_format == 'CSV':

            zipped_file = zip_files([
                dict(name="Bicycle", data=BicycleResource().export().csv),
                dict(name="Component", data=ComponentResource().export().csv),
                dict(name="Material", data=MaterialResource().export().csv),
                dict(name="Mounting", data=MountingResource().export().csv),
                dict(name="Part", data=PartResource().export().csv),
                dict(name="Record", data=RecordResource().export().csv),
                dict(name="Species", data=SpeciesResource().export().csv),
                ], "csv")

            response = HttpResponse(
                zipped_file, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="exported_data_csv.zip"'

            return response

        elif file_format == 'JSON':

            zipped_file = zip_files([
                dict(name="Bicycle", data=BicycleResource().export().json),
                dict(name="Component", data=ComponentResource().export().json),
                dict(name="Material", data=MaterialResource().export().json),
                dict(name="Mounting", data=MountingResource().export().json),
                dict(name="Part", data=PartResource().export().json),
                dict(name="Record", data=RecordResource().export().json),
                dict(name="Species", data=SpeciesResource().export().json),
                ], "json")

            response = HttpResponse(
                zipped_file, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="exported_data_json.zip"'
            return response

        elif file_format == 'XLS (Excel)':

            zipped_file = zip_files([
                dict(name="Bicycle", data=BicycleResource().export().xls),
                dict(name="Component", data=ComponentResource().export().xls),
                dict(name="Material", data=MaterialResource().export().xls),
                dict(name="Mounting", data=MountingResource().export().xls),
                dict(name="Part", data=PartResource().export().xls),
                dict(name="Record", data=RecordResource().export().xls),
                dict(name="Species", data=SpeciesResource().export().xls),
                ], "xls")

            response = HttpResponse(
                zipped_file, content_type='application/octet-stream')
            response['Content-Disposition'] = 'attachment; filename="exported_data_xls.zip"'

            return response

    return render(request, 'myequis/export.html')


class EditMaterialView(LoginRequiredMixin, CreateView):

    def get(self, request, *args, **kwargs):
        logger.warning("EditMaterialView GET request: {}".format(str(request)))

        # Find the best km as default value
        material = get_object_or_404(Material, pk=kwargs['material_id'])

        mountings = Mounting.objects.filter(material=material.pk).order_by('-mount_record__date')[:1]

        if len(mountings) > 0:
            mounting_id = mountings[0].pk
            if mountings[0].active:
                mounting_info = "Material is in use since " + mountings[0].mount_record.date.strftime("%a, %d %b %Y")
            else:
                mounting_info = "Material was dismounted at " + mountings[0].dismount_record.date.strftime("%a, %d %b %Y")
        else:

            # kind of magic number
            mounting_id = 0

            mounting_info = "This is an new material."

        logger.warning("EditMaterialView GET mounting_id: {}".format(str(mounting_id)))

        # If called with data, clean() will be processed!
        form = EditMaterialForm(
            {
                'name': material.name,
                'manufacture': material.manufacture,
                'size': material.size,
                'weight': material.weight,
                'price': material.price,
                'comment': material.comment,
                'disposed': material.disposed,
                'disposedAt': material.disposedAt,
                'mounting_id': mounting_id, # in form: converted to string
             })

        template = loader.get_template('myequis/edit_material.html')
        return HttpResponse(template.render({'material': material, 'mounting_info': mounting_info, 'form': form}, request))

    def post(self, request, *args, **kwargs):
        logger.warning(
            "EditMaterialView POST request.POST: {}".format(str(request.POST)))

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Edit material canceled'" % reverse('myequis:list-materials-url'))

        form = EditMaterialForm(request.POST)
        # logger.warning("form: " + str(form))
        # logger.warning("form cleaned_data: " + str(form.cleaned_data))

        material = get_object_or_404(Material, pk=kwargs['material_id'])

        if form.is_valid():
            logger.warning("is valid. form.cleaned_data={}".format(
                str(form.cleaned_data)))
            # form.check_data()

            # process the data in form.cleaned_data as required
            material.name = form.cleaned_data['name']
            material.manufacture = form.cleaned_data['manufacture']
            material.size = form.cleaned_data['size']
            material.weight = form.cleaned_data['weight']
            material.price = form.cleaned_data['price']
            material.comment = form.cleaned_data['comment']
            material.disposed = form.cleaned_data['disposed']
            material.disposedAt = form.cleaned_data['disposedAt']

            material.save()
            logger.warning("New material saved={}".format(str(material)))

            # redirect to a new URL:
            # see https://docs.djangoproject.com/en/dev/ref/urlresolvers/#django.core.urlresolvers.reverse
            # return HttpResponseRedirect(reverse('url_records', args=(record.bicycle.id,)))
            return HttpResponseRedirect(
                "%s?message='{} updated'".format(material.name)
                % reverse('myequis:list-materials-url'))

        else:
            logger.warning("is not valid")
            template = loader.get_template('myequis/edit_material.html')
            return HttpResponse(template.render({
                'material': material,
                'form': form,
            }, request))


class CreateMaterialView(LoginRequiredMixin, CreateView):


    def get(self, request, *args, **kwargs):
        logger.warning(
            "CreateMaterialView GET request: {}".format(str(request)))

        # Find the best km as default value
        material = Material()

        # If called with data, clean() will be processed!
        form = CreateMaterialForm(
            {
                'name': material.name,
                'manufacture': material.manufacture,
                'size': material.size,
                'weight': material.weight,
                'price': material.price,
                'comment': material.comment,
             })

        template = loader.get_template('myequis/create_material.html')
        return HttpResponse(template.render({'material': material, 'form': form}, request))

    def post(self, request, *args, **kwargs):
        logger.warning(
            "CreateMaterialView POST request.POST: {}".format(str(request.POST)))

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Create material canceled'" % reverse('myequis:list-materials-url'))

        form = CreateMaterialForm(request.POST)
        # logger.warning("form: " + str(form))
        # logger.warning("form cleaned_data: " + str(form.cleaned_data))

        material = Material()

        if form.is_valid():
            logger.warning("is valid. form.cleaned_data={}".format(
                str(form.cleaned_data)))
            # form.check_data()

            # process the data in form.cleaned_data as required
            material.name = form.cleaned_data['name']
            material.manufacture = form.cleaned_data['manufacture']
            material.size = form.cleaned_data['size']
            material.weight = form.cleaned_data['weight']
            material.price = form.cleaned_data['price']
            material.comment = form.cleaned_data['comment']

            material.save()
            logger.warning("New material saved={}".format(str(material)))

            # redirect to a new URL:
            # see https://docs.djangoproject.com/en/dev/ref/urlresolvers/#django.core.urlresolvers.reverse
            # return HttpResponseRedirect(reverse('url_records', args=(record.bicycle.id,)))
            return HttpResponseRedirect(
                "%s?message='{} created'".format(material.name)
                % reverse('myequis:list-materials-url'))

        else:
            logger.warning("is not valid")
            template = loader.get_template('myequis/create_material.html')
            return HttpResponse(template.render({
                'material': material,
                'form': form,
            }, request))


class CreateRecordView(LoginRequiredMixin, CreateView):

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
        record.bicycle = get_object_or_404(
            Bicycle, pk=form.cleaned_data['bicycle_id'])

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

        records = Record.objects.filter(bicycle_id=bicycle.id).filter(
            date__lt=record.date).order_by('-date')

        if len(records) >= 1:
            r = records[0]
            # logger.warning("Found last record: id={} date={} km={}".format(str(r.id), str(r.date), str(r.km)))
            record.km = r.km
        else:
            # logger.warning("No previous records found")
            record.km = 0

        return record


class DeleteMountingView(LoginRequiredMixin, UpdateView):

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
                "%s?message='Delete mounting for Part {} canceled'".format(
                    part.name)
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


class MountMaterialView(LoginRequiredMixin, CreateView):
    """
    Input: Part.id, Bicycle.id
    """

    def get(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        form = MountForm({
                'bicycle_id': bicycle.id,
                'selected_material': "",
                'selected_record': "",
        })

        template = loader.get_template('myequis/mount_material.html')
        return HttpResponse(
            template.render({
                'bicycle': bicycle,
                'part': part,
                'materials': self.select_materials(),
                'records': self.select_records(bicycle, part),
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
            material_under_edit = get_object_or_404(
                Material, pk=form.cleaned_data['selected_material'])
            record = get_object_or_404(
                Record, pk=form.cleaned_data['selected_record'])
            logger.warning("record_select: {}".format(str(record)))

            mounting = Mounting()
            mounting.mount_record = record
            mounting.material = material_under_edit
            mounting.part = part
            mounting.comment = form.cleaned_data['comment']
            mounting.save()
            # logger.warning("Comment: {}".format(str(mounting.comment)))
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
                    'records': self.select_records(bicycle, part),
                    'form': form,
                }, request))

    @staticmethod
    def select_materials():
        return Material.objects.annotate(mounted=Exists(
            Mounting.objects.filter(dismount_record=None, material=OuterRef('pk')))) \
            .filter(mounted=False) \
            .filter(disposed=False)\
            .order_by('name')


    @staticmethod
    def select_records(bicycle, part):
        """
            Usable Records for a particular bicycle and part
        """

        # All records
        records = Record.objects.filter(
            bicycle_id=bicycle.id).order_by("-date")

        record_list = []

        # Find records that are not within any mounting period of this part
        for record in records:
            logger.warning(f"select_records checking record date={record.date}")
            if Mounting.objects.filter(part_id=part.id,
                mount_record__bicycle_id=bicycle.id)\
                    .filter(Q(mount_record__date__lte=record.date))\
                    .filter(Q(dismount_record__date__gt=record.date))\
                    .count() == 0:

                logger.warning(f"select_records nothing found, add record")

                record_list.append(
                    dict(
                        id=record.id,
                        date=record.date,
                        km=record.km,
                    ))

            else:
                logger.warning(f"select_records found mountings. Ignore record")


        return record_list

class DismountMaterialView(LoginRequiredMixin, UpdateView):
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
            'comment': my_mounting.comment,
        })

        template = loader.get_template('myequis/dismount_material.html')
        return HttpResponse(
            template.render({
                'bicycle': bicycle,
                'part': part,
                'mounting': my_mounting,
                'records':  self.select_records(bicycle, part, my_mounting),
                'form': form,
            }, request))

    def post(self, request, *args, **kwargs):
        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])
        part = get_object_or_404(Part, pk=kwargs['part_id'])

        my_mounting = get_object_or_404(Mounting, pk=Mounting.objects.filter(part_id=part.id,
                                                                             mount_record__bicycle_id=bicycle.id,
                                                                             dismount_record__isnull=True,
                                                                             )[0].id)

        logger.warning(
            f"POST: bycicle={bicycle} part={part} my_mounting={my_mounting}")

        if 'cancel' in request.POST:
            return HttpResponseRedirect(
                "%s?message='Dismounting {} canceled'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        form = DismountForm(request.POST)

        if form.is_valid():
            logger.warning("valid! cleaned_data={}".format(
                str(form.cleaned_data)))
            mounting_under_edit = get_object_or_404(
                Mounting, pk=form.cleaned_data['mounting_id'])
            record = get_object_or_404(
                Record, pk=form.cleaned_data['selected_record'])
            mounting_under_edit.dismount_record = record
            mounting_under_edit.comment = form.cleaned_data['comment']

            material_under_edit = mounting_under_edit.material

            if form.cleaned_data['disposed']:
                logger.warning("dispose material.")
                material_under_edit.disposed = True
                material_under_edit.disposedAt = record.date
                material_under_edit.save()

            mounting_under_edit.save()
            logger.warning("Dismounted: {}".format(str(mounting_under_edit)))

            return HttpResponseRedirect(
                "%s?message='{} dismounted'".format(part.name)
                % reverse('myequis:list-bicycle-parts-url',
                          args=(kwargs['bicycle_id'],)))

        else:
            logger.warning("is not valid")
            template = loader.get_template('myequis/dismount_material.html')
            return HttpResponse(
                template.render({
                    'bicycle': bicycle,
                    'mounting': my_mounting,
                    'part': part,
                    'records': self.select_records(bicycle, part, my_mounting),
                    'form': form,
                }, request))

    @staticmethod
    def select_records(bicycle, part, mounting):

        # There can be mountings afterwards for the part or for the material
        newer_mountings = Mounting.objects.filter(\
            Q(part_id=part.id) &\
            Q(mount_record__bicycle_id=bicycle.id) |\
            Q(material_id=mounting.material.id))\
            .filter(mount_record__date__gt=mounting.mount_record.date)\
            .order_by("mount_record__date")

        logger.warning(f"newer_mounting={newer_mountings}")

        if len(newer_mountings) > 0:
            logger.warning(f"newer_mounting={newer_mountings[0]}")

            # All records after mounting but before next mounting
            records = Record.objects.filter(
                bicycle_id=bicycle.id, date__gte=mounting.mount_record.date,\
                date__lte=newer_mountings[0].mount_record.date)\
                .order_by("-date")

        else:

            # All records after mounting
            records = Record.objects.filter(
                bicycle_id=bicycle.id, date__gte=mounting.mount_record.date).order_by("-date")

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


class ExchangeMaterialView(LoginRequiredMixin,  UpdateView):
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

        logger.warning("ExchangeMaterialView Mounting {}".format(str(my_mounting)))


        form = ExchangeMountingForm({
            'bicycle_id': bicycle.id,
            'selected_record': "",
            'selected_material': "",
            'mounting_id': my_mounting.id,
            'dismounting_comment': my_mounting.comment,
            'mounting_comment': "",
        })

        template = loader.get_template('myequis/exchange_material.html')
        return HttpResponse(
            template.render({
                'bicycle': bicycle,
                'part': part,
                'mounting': my_mounting,
                'records': DismountMaterialView.select_records(bicycle, part, my_mounting),
                'materials': MountMaterialView.select_materials(),
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
            selected_record = get_object_or_404(
                Record, pk=form.cleaned_data['selected_record'])
            selected_material = get_object_or_404(
                Material, pk=form.cleaned_data['selected_material'])
            # logger.warning("record_select: {}".format(str(selected_record)))

            if form.cleaned_data['disposed']:
                dis_material = dis_mounting.material
                dis_material.disposed = True
                dis_material.disposedAt = selected_record.date
                dis_material.save()

            dis_mounting.dismount_record = selected_record
            dis_mounting.part = part
            dis_mounting.comment = form.cleaned_data['dismounting_comment']
            dis_mounting.save()
            logger.warning("Mounting updated: {}".format(str(dis_mounting)))

            new_mounting = Mounting()
            new_mounting.mount_record = selected_record
            new_mounting.material = selected_material
            new_mounting.part = part
            new_mounting.comment = form.cleaned_data['mounting_comment']
            new_mounting.save()
            logger.warning(
                "New mounting created: {}".format(str(new_mounting)))

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
                    'records': DismountMaterialView.select_records(bicycle, part, dis_mounting),
                    'materials': MountMaterialView.select_materials(),
                    'form': form,
                }, request))



class EditRecordView(LoginRequiredMixin, UpdateView):

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
            mounting = next(
                (m for m in mountings if m.part.id == part.id), None)
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

            part_data_list.append(
                dict(part=part, material=part_material, mounting=mounting, distance=distance, ))

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

    logger.warning("mountings={}".format(str(mountings)))
    logger.warning("records={}".format(str(records)))

    component_data_list = []

    for component in Component.objects.filter(species_id=bicycle.species.id):
        component_data = dict()

        component_data['component_name'] = component.name

        parts = Part.objects.filter(component__id=component.id)

        part_data_list = []

        for part in parts:
            mounting = next(
                (m for m in mountings if m.part.id == part.id), None)
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
            part_data_list.append(
                dict(part=part, material=part_material, distance=distance, mounting=mounting))

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


def list_material_history(request, material_id):

    logger.warning(f"list_material_history material_id={material_id}")

    material = get_object_or_404(Material, pk=material_id)

    logger.warning(f"material={material}")

    mounting_list = []

    mountings = Mounting.objects.filter(material__id=material.id)\
        .order_by('-mount_record__date')

    total_distance = 0
    total_days = 0

    for mounting in mountings:

        mounting_data = dict()
        mounting_data["mounting"]=mounting

        if mounting.dismount_record is None:

            # newest record for this bicycle
            record = Record.objects.filter(bicycle_id=mounting.mount_record.bicycle.id).order_by('-date').first()

            mounting_data["distance"] = human_distance( mounting.mount_record.km, record.km)
            mounting_data["duration"] = human_delta(mounting.mount_record.date, record.date)

            total_distance += record.km - mounting.mount_record.km
            total_days += (record.date - mounting.mount_record.date).days

        else:
            mounting_data["distance"] = human_distance(mounting.mount_record.km, mounting.dismount_record.km)
            mounting_data["duration"] = human_delta(mounting.mount_record.date, mounting.dismount_record.date)

            total_distance += mounting.dismount_record.km - mounting.mount_record.km
            total_days += (mounting.dismount_record.date - mounting.mount_record.date).days

        mounting_list.append(mounting_data)

    data = dict(material=material, distance=total_distance, duration=human_days(total_days), mountings=mounting_list)

    logger.warning(f"data={data}")

    template = loader.get_template('myequis/material_history.html')

    if 'message' in request.GET.keys():
        context = {
            'data': data,
            'message': request.GET['message']
        }
    else:
        context = {
            'data': data,
        }

    return HttpResponse(template.render(context, request))


def list_bicycle_history(request, bicycle_id):
    """
    bicycle_history.html
    """

    bicycle = Bicycle.objects.get(pk=bicycle_id)

    # All Mountings for this bicycle
    mountings = Mounting.objects.annotate(
        bicycle_found=Exists(
            Record.objects.filter(bicycle_id=bicycle.id)
        )
    ).filter(bicycle_found=True).order_by('-mount_record__date')

    records = Record.objects.filter(bicycle_id=bicycle.id).order_by('-date')

    logger.warning(f"Found {len(mountings)} mountings")

    # logger.warning(f"Mountings:{mountings}")

    component_data_list = []

    for component in Component.objects.filter(species_id=bicycle.species.id):
        component_data = dict()

        component_data['name'] = component.name

        parts = Part.objects.filter(component__id=component.id)

        part_data_list = []

        for part in parts:
            part_mountings = [m for m in mountings if m.part.id == part.id]

            # logger.warning(f"part {part.name} part_mountings={part_mountings}")

            has_mounting = len(part_mountings) > 0
            mounting_data_list = []
            distance = ""
            timedelta = ""

            # logger.warning(f"part {part.name} has {len(part_mountings)} mountings")

            # Material can be mounted multiple times and in different bicycles
            for mounting in part_mountings:
                # logger.warning("mounting={}".format(str(mounting)))

                if mounting.dismount_record is None:
                    # actual mounted
                    distance = human_distance( mounting.mount_record.km, records.first().km)
                    delta = human_delta(mounting.mount_record.date, records.first().date)
                else:
                    # Materials history
                    distance = human_distance(mounting.mount_record.km, mounting.dismount_record.km)
                    delta = human_delta(mounting.mount_record.date, mounting.dismount_record.date)

                    logger.warning(f"mounting's delta={delta}")

                mounting_data_list.append(
                    dict(mounting=mounting, distance=distance, delta=delta ))

            part_data_list.append(
                dict(part=part, has_mounting=has_mounting, mounting_data_list=mounting_data_list ))

        component_data['part_data_list'] = part_data_list

        component_data_list.append(component_data)

    # logger.warning(f"component_data_list={component_data_list}")

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
        .filter(disposed=False)\
        .order_by('name')

    template = loader.get_template('myequis/index.html')

    if 'message' in request.GET.keys():
        logger.warning(f"index called with message={request.GET['message']}")
        context = {
            'bicycles': bicycles,
            'materials': materials,
            'message': request.GET['message'],
        }
    else:
        context = {
            'bicycles': bicycles,
            'materials': materials,
        }

    return HttpResponse(template.render(context, request))


def materials(request):

    # Existing materials without any mountings
    new_materials = Material.objects.annotate(used=Exists(
        Mounting.objects.filter(material=OuterRef('pk'))))\
        .filter(used=False)\
        .filter(disposed=False)\
        .order_by('name')

    # Existing materials which are dismounted actually
    mounted_materials = Material.objects\
        .annotate(mounted=Exists(Mounting.objects.
                                 filter(Q(dismount_record__isnull=True), material=OuterRef('pk'))))\
        .annotate(hasMountings=Exists(Mounting.objects
                                      .filter(material=OuterRef('pk'))))\
        .filter(mounted=True)\
        .filter(disposed=False)\
        .filter(hasMountings=True)\
        .annotate(mountedAt=Subquery(Mounting.objects
                                        .filter(Q(dismount_record__isnull=True), material=OuterRef('pk'))\
                                        .order_by('-mount_record__date')
                                        .values('mount_record__date')[:1]))\
        .annotate(mountingComment=Subquery(Mounting.objects
                                        .filter(Q(dismount_record__isnull=True), material=OuterRef('pk'))\
                                        .order_by('-mount_record__date')
                                        .values('comment')[:1]))

    for mounted in mounted_materials:
        logger.warning(f"mounted_material={mounted.name}, {mounted.mountedAt}, {mounted.mountingComment}")

    # Existing materials which are dismounted actually
    dismounted_materials = Material.objects\
        .annotate(mounted=Exists(Mounting.objects.
                                 filter(Q(dismount_record__isnull=True), material=OuterRef('pk'))))\
        .annotate(hasMountings=Exists(Mounting.objects
                                      .filter(material=OuterRef('pk'))))\
        .filter(mounted=False)\
        .filter(disposed=False)\
        .filter(hasMountings=True)\
        .annotate(dismountedAt=Subquery(Mounting.objects
                                        .filter(material=OuterRef('pk'))
                                        .order_by('-dismount_record__date')
                                        .values('dismount_record__date')[:1]))\
        .annotate(dismountingComment=Subquery(Mounting.objects
                                        .filter(material=OuterRef('pk'))
                                        .order_by('-dismount_record__date')
                                        .values('comment')[:1]))

    # Materials without actual mounted items
    disposed_materials = Material.objects\
        .filter(disposed=True)\
        .order_by('-disposedAt')

    template = loader.get_template('myequis/materials.html')

    if 'message' in request.GET.keys():
        context = {
            'new_materials': new_materials,
            'mounted_materials': mounted_materials,
            'dismounted_materials': dismounted_materials,
            'disposed_materials': disposed_materials,
            'message': request.GET['message']
        }
    else:
        context = {
            'new_materials': new_materials,
            'mounted_materials': mounted_materials,
            'dismounted_materials': dismounted_materials,
            'disposed_materials': disposed_materials,
        }

    return HttpResponse(template.render(context, request))


def material(request, material_id):
    material = Material.objects.get(id=material_id)

    return HttpResponse("You're looking at material %s." % material.name).order_by('name')

    # Existing materials which are dismounted actually
    dismounted_materials = Material.objects\
        .annotate(mounted=Exists(Mounting.objects.
                                 filter(Q(dismount_record__isnull=True), material=OuterRef('pk'))))\
        .annotate(hasMountings=Exists(Mounting.objects
                                      .filter(material=OuterRef('pk'))))\
        .filter(mounted=False)\
        .filter(disposed=False)\
        .filter(hasMountings=True)\
        .annotate(dismountedAt=Subquery(Mounting.objects
                                        .filter(material=OuterRef('pk'))
                                        .order_by('-dismount_record__date')
                                        .values('dismount_record__date')[:1]))

    # Materials without actual mounted items
    disposed_materials = Material.objects\
        .filter(disposed=True)\
        .order_by('-disposedAt')

    template = loader.get_template('myequis/materials.html')

    if 'message' in request.GET.keys():
        context = {
            'new_materials': new_materials,
            'dismounted_materials': dismounted_materials,
            'disposed_materials': disposed_materials,
            'message': request.GET['message']
        }
    else:
        context = {
            'new_materials': new_materials,
            'dismounted_materials': dismounted_materials,
            'disposed_materials': disposed_materials,
        }

    return HttpResponse(template.render(context, request))


def material(request, material_id):
    material = Material.objects.get(id=material_id)

    return HttpResponse("You're looking at material %s." % material.name)


def human_distance(low, high):
    """
        Readable distance as String of two integer values
    """
    return f"{(high - low):,}"


def human_delta(start, end):
    """
        Readable time delta as String of two integer values
    """
    delta = end - start

    if delta.days < 31:
        return human_time_delta(delta.days, 0, 0)

    logger.warning(f"delta={delta}")

    years = end.year - start.year
    months = end.month - start.month

    return human_time_delta(0, months, years)


def human_days(days):
    """
        Readable time delta as an approximated value as String of days
    """

    years = int(days / 365)

    days_of_year = int(days - years * 365)

    months = int(days_of_year / 30)

    days_of_month = int(days_of_year - months * 30)

    return human_time_delta(days_of_month, months, years)


def human_time_delta(days, months, years):
    """
        Readable time delta as a nice readable String with years, months and days
    """

    logger.warning(f"human_time_delta days, month, years={days}, {months}, {years}")

    if months == 0 and years == 0:
        return f"{days} d"

    if months < 0:
        years -= 1
        months += 12

    if years == 0:
        return f"{months} m"

    if months == 0:
        return f"{years} y"

    res = f"{years} y {months} m"

    logger.warning(f"human_time_delta returns={res}")

    return res
