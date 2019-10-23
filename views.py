from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from myequis.models import Material
from myequis.models import Bicycle
from myequis.models import Record
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .forms import CreateRecordForm
from .forms import EditRecordForm
from django.views.generic.edit import UpdateView
from django.views.generic.edit import CreateView
from datetime import datetime
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class CreateRecordView(CreateView):
    
    
    def get(self, request, *args, **kwargs):
        logger.warning("CreateRecordView GET request: {}".format(str(request)))

        bicycle = get_object_or_404(Bicycle, pk=kwargs['bicycle_id'])

        # Find the best km as default value
        record = self.createRecord(bicycle)

        # If called with data, clean() will be processed!
        form = CreateRecordForm(
            {'date': record.date, 
                'km': record.km,
                'bicycle_id': record.bicycle.id,
                })

        template = loader.get_template('myequis/create_record.html')
        return HttpResponse(template.render({ 'record': record, 'form': form }, request))


    def post(self, request, *args, **kwargs):
        logger.warning("CreateRecordView POST request.POST: {}".format(str(request.POST)))

        form = CreateRecordForm(request.POST)
        logger.warning("form: " + str(form))
        logger.warning("form cleaned_data: " + str(form.cleaned_data))
        
        record = Record()
        record.date = form.cleaned_data['date']
        record.km = form.cleaned_data['km']
        record.bicycle = get_object_or_404(Bicycle, pk=form.cleaned_data['bicycle_id'])
        #logger.warning("new record= {}".format(str(record)))

        #logger.warning("Before is_valid ")
        if form.is_valid():
            #logger.warning("is Valid. form.cleaned_data={}".format(str(form.cleaned_data)))
            form.check_create_record()
            # process the data in form.cleaned_data as required
     
            record.save()
            logger.warning("New record saved={}".format(str(record)))
            
            # redirect to a new URL:
            # see https://docs.djangoproject.com/en/dev/ref/urlresolvers/#django.core.urlresolvers.reverse
            #return HttpResponseRedirect(reverse('url_records', args=(record.bicycle.id,)))              
            return HttpResponseRedirect(reverse('myequis:list-records-url', args=(record.bicycle.id,)))              
        
        else:
            logger.warning("is not valid" )
            template = loader.get_template('myequis/create_record.html')
            return HttpResponse(template.render({ 'record': record, 'form': form, }, request))    
    
    
    def createRecord(self, bicycle):
        """
        Returns new and unsaved Record with initialized data. Has no ID
        """
        record = Record()
        #logger.warning("Create new record: " + str(record.id))
        record.date = datetime.now()
        #logger.warning("Added date: " + str(record.date))
        record.bicycle = bicycle
        #logger.warning("NEW: " + str(record))
        
        records = Record.objects.filter(bicycle_id=bicycle.id).filter(date__lt=record.date).order_by('-date')
        
        if len(records) >= 1:
            r = records[0]
            #logger.warning("Found last record: id={} date={} km={}".format(str(r.id), str(r.date), str(r.km))) 
            record.km = r.km
        else:
            #logger.warning("No previous records found")
            record.km = 0
        
        return record


class EditRecordView(UpdateView):
    
    def get(self, request, *args, **kwargs):
        logger.warning("path_info: " + str(request.path_info))
        logger.warning("kwargs: " + str(kwargs))
        
        logger.warning("Entering: {}".format(str("create_record:else")))
        record = get_object_or_404(Record, pk=kwargs['record_id'])
        logger.warning("EXISTS: " + str(record))
    
        data = {'date': record.date, 
                'km': record.km,
                'id': record.id}
        form = EditRecordForm(data)

        template = loader.get_template('myequis/edit_record.html')
        return HttpResponse(template.render({ 'record': record, 'form': form }, request))


    def post(self, request, *args, **kwargs):
        record = get_object_or_404(Record, pk=kwargs['record_id'])
        
        logger.warning("POST: " + str(record))
        form = EditRecordForm(request.POST)
        
        form.enable_validations()
        
        logger.warning("Before is_valid ")
        if form.is_valid():
            logger.warning("is Valid ")
            form.check_edit_record()
            # process the data in form.cleaned_data as required
            record.date = form.cleaned_data['date']
            record.km = form.cleaned_data['km']
            record.save()
            
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('myequis:records', args=(record.bicycle.id,)))              
        
        else:
            logger.warning("is not valid" )
            template = loader.get_template('myequis/edit_record.html')
            return HttpResponse(template.render({ 'record': record, 'form': form }, request))    
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.check_edit_record(form.id, form.data, form.km)
        return super().form_valid(form)


def list_records(request, bicycle_id):
    records = Record.objects.filter(bicycle__id=bicycle_id).order_by('-date')

    bicycle = Bicycle.objects.get(pk=bicycle_id)
    template = loader.get_template('myequis/records.html')

    context = {
        'bicycle': bicycle,
        'records': records
    }
    
    return HttpResponse(template.render(context, request))


def bicycle_detail(request, bicycle_id):
    
    bicycle = Bicycle.objects.get(pk=bicycle_id)
    records = Record.objects.filter(bicycle__id=bicycle_id).order_by('-date')[:2]
    
    template = loader.get_template('myequis/bicycle_detail.html')

    context = {
        'bicycle': bicycle,
        'records': records
    }
    
    return HttpResponse(template.render(context, request))

def index(request):
    
    bicycles = Bicycle.objects.order_by('name')
    
    materials = Material.objects.filter(mount_record=None).order_by('name')
    #.order_by('name')
    
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

    
