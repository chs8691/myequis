from import_export.admin import ImportExportModelAdmin

from django.contrib import admin

from .models import Component, Mounting, Species
from .models import Part
from .models import Bicycle
from .models import Record
from .models import Type
from .models import Material

class ComponentInline(admin.TabularInline):
    model = Component
    extra = 1
    ordering = ["name"]


class RecordInline(admin.TabularInline):
    model = Record
    extra = 1
    ordering = ["-date"]


@admin.register(Bicycle)
class BicycleAdmin(ImportExportModelAdmin):
    inlines = [RecordInline]
    ordering = ["name"]

@admin.register(Species)
class SpeciesAdmin(ImportExportModelAdmin):
    inlines = [ComponentInline]
    ordering = ["name"]

class PartInline(admin.TabularInline):
    model = Part
    extra = 3


@admin.register(Component)
class ComponentAdmin(ImportExportModelAdmin):
    inlines = [PartInline]
    ordering = ["name"]

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'manufacture', 'name', 'type', 'size', 'disposedAt', )
    # list_display = ('id', 'manufacture', 'name', 'size', 'disposedAt', )


class MountingAdmin(admin.ModelAdmin):
    ordering = ["mount_record__date",]
    list_display = ['id', 'part', 'material', 'mount_record', 'dismount_record',]


# admin.site.register(Bicycle, BicycleAdmin)
# admin.site.register(Species, SpeciesAdmin)
# admin.site.register(Component, ComponentAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Mounting, MountingAdmin)
admin.site.register(Type)
