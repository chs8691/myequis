from django.contrib import admin

from .models import Component, Mounting, Species
from .models import Part
from .models import Bicycle
from .models import Record
from .models import Material


class ComponentInline(admin.TabularInline):
    model = Component
    extra = 1
    ordering = ["name"]


class RecordInline(admin.TabularInline):
    model = Record
    extra = 1
    ordering = ["-date"]


class BicycleAdmin(admin.ModelAdmin):
    inlines = [RecordInline]
    ordering = ["name"]


class SpeciesAdmin(admin.ModelAdmin):
    inlines = [ComponentInline]
    ordering = ["name"]


class PartInline(admin.TabularInline):
    model = Part
    extra = 3


class ComponentAdmin(admin.ModelAdmin):
    inlines = [PartInline]
    ordering = ["name"]


class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacture', 'size',)


class MountingAdmin(admin.ModelAdmin):
    ordering = ["mount_record__date"]


admin.site.register(Bicycle, BicycleAdmin)
admin.site.register(Species, SpeciesAdmin)
admin.site.register(Component, ComponentAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Mounting, MountingAdmin)
