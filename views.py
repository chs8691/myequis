from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import loader
from myequis.models import Material
from myequis.models import Bicycle
from myequis.models import Record
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from .forms import RecordForm
from django.views.generic.edit import UpdateView
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

class UpdateRecordView(UpdateView):
    
    def get(self, request, *args, **kwargs):
        record = get_object_or_404(Record, pk=kwargs['record_id'])
        data = {'date': record.date, 
                'km': record.km,
                'id': record.id}
        form = RecordForm(data)

        template = loader.get_template('myequis/record.html')
        return HttpResponse(template.render({ 'record': record, 'form': form }, request))


    def post(self, request, *args, **kwargs):
        record = get_object_or_404(Record, pk=kwargs['record_id'])
        
        logger.warning("LOGGER: " + str(record))
        form = RecordForm(request.POST)
        
        
        form.enable_validations()
        
        logger.warning(str(record))
        
        if form.is_valid():
            form.check_edit_record()
            # process the data in form.cleaned_data as required
            record.date = form.cleaned_data['date']
            record.km = form.cleaned_data['km']
            record.save()
            
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('myequis:records', args=(record.bicycle.id,)))              
        
        else:
            template = loader.get_template('myequis/record.html')
            return HttpResponse(template.render({ 'record': record, 'form': form }, request))    
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        form.check_edit_record(form.id, form.data, form.km)
        return super().form_valid(form)


def create_record(request, bicycle_id):

    record = Record(date="2019-07-08", km=0)
    record.bicycle = Bicycle.objects.get(pk=bicycle_id)
        
     # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RecordForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            record.date = form.cleaned_data['date']
            record.km = form.cleaned_data['km']
            record.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('myequis:records', args=(record.bicycle.id,)))     
    
    # if a GET (or any other method) we'll create a blank form
    else:
        data = {'date': record.date, 
                'km': record.km,
                'id': record.id}
        form = RecordForm(data)

    template = loader.get_template('myequis/create_record.html')
    return HttpResponse(template.render({ 'record': record, 'form': form }, request))


def records(request, bicycle_id):
    records = Record.objects.filter(bicycle__id=bicycle_id).order_by('-date')

    bicycle = Bicycle.objects.get(pk=bicycle_id)
    template = loader.get_template('myequis/records.html')

    context = {
        'bicycle': bicycle,
        'records': records
    }
    
    return HttpResponse(template.render(context, request))

def bicycle(request, bicycle_id):
    
    bicycle = Bicycle.objects.get(pk=bicycle_id)
    records = Record.objects.filter(bicycle__id=bicycle_id).order_by('-date')
    
    template = loader.get_template('myequis/bicycle.html')

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

    
