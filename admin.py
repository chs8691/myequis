from django.contrib import admin

from .models import Component
from .models import Part
from .models import Bicycle
from .models import Record
from .models import Material
#from .models import Mounting

class RecordInline(admin.TabularInline):
    model = Record
    extra = 1
    ordering = ["-date"]

class BicycleAdmin(admin.ModelAdmin):
    inlines = [RecordInline]
    ordering = ["name"]

admin.site.register(Bicycle, BicycleAdmin)


class PartInline(admin.TabularInline):
    model = Part
    extra = 3
    
class ComponentAdmin(admin.ModelAdmin):
    inlines = [PartInline]
    ordering = ["name"]
    
admin.site.register(Component, ComponentAdmin)

class MaterialAdmin(admin.ModelAdmin):
    list_display =('name', 'manufactor', 'size', 'mounted_in_bicycle')
    
admin.site.register(Material, MaterialAdmin)


