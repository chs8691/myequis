from import_export import resources
from .models import Bicycle, Component, Part, Record, Material, Mounting,\
    Species, Type

class BicycleResource(resources.ModelResource):
    class Meta:
        model = Bicycle

class ComponentResource(resources.ModelResource):
    class Meta:
        model = Component

class PartResource(resources.ModelResource):
    class Meta:
        model = Part

class RecordResource(resources.ModelResource):
    class Meta:
        model = Record

class TypeResource(resources.ModelResource):
    class Meta:
        model = Type

class MaterialResource(resources.ModelResource):
    class Meta:
        model = Material

class MountingResource(resources.ModelResource):
    class Meta:
        model = Mounting

class SpeciesResource(resources.ModelResource):
    class Meta:
        model = Species
