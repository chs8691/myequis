from django.urls import path
from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage

from . import views

app_name = 'myequis'
urlpatterns = [
    # ex: /myequis/
    path('', views.index, name='index-url'),

    path('export', views.export_data, name='export-url'),

    path('import', views.ImportView.as_view(), name='import-url'),


    # ### BICYCLES ##############################

    # ex: myequis/bicycles/5/
    path('bicycles/<int:bicycle_id>/', views.list_bicycle_detail, name='bicycle-detail-url'),

    # ex: myequis/bicycles/5/records
    path('bicycles/<int:bicycle_id>/records', views.list_records, name='list-records-url'),

    # ex: myequis/bicycles/5/parts
    path('bicycles/<int:bicycle_id>/parts', views.list_bicycle_parts, name='list-bicycle-parts-url'),

    # ex: myequis/bicycles/5/history
    path('bicycles/<int:bicycle_id>/history', views.list_bicycle_history, name='list-bicycle-history-url'),

    # ex: myequis/bicycles/5/history
    path('bicycles/<int:bicycle_id>/timeline', views.list_bicycle_timeline, name='list-bicycle-timeline-url'),

    # ex: myequis/bicycles/5/part/4/mount
    path('bicycles/<int:bicycle_id>/part/<int:part_id>/mount', views.MountMaterialView.as_view(),
         name='mount-material-url'),

    # ex: myequis/bicycles/5/part/4/delete-mounting
    path('bicycles/<int:bicycle_id>/part/<int:part_id>/delete-mounting', views.DeleteMountingView.as_view(),
         name='delete-mounting-url'),

    # ex: myequis/bicycles/5/part/4/exchange
    path('bicycles/<int:bicycle_id>/part/<int:part_id>/exchange', views.ExchangeMaterialView.as_view(),
         name='exchange-material-url'),

    # ex: myequis/bicycles/5/part/4/dismount
    path('bicycles/<int:bicycle_id>/part/<int:part_id>/dismount', views.DismountMaterialView.as_view(),
         name='dismount-material-url'),

    # ### RECORDS ##############################

    # ex: myequis/records/create_record?bicycle_id=1
    path('bicycles/<int:bicycle_id>/create-record', views.CreateRecordView.as_view(), name='create-record-url'),

    # ex: myequis/records/4
    path('records/<int:record_id>/', views.EditRecordView.as_view(), name='edit-record-url'),

    # ### MATERIALS ##############################
    # ex: myequis/materials
    path('materials/active', views.list_active_materials, name='list-active-materials-url'),

    # ex: myequis/materials
    path('materials/stored', views.list_stored_materials, name='list-stored-materials-url'),

    # ex: myequis/materials/disposed
    path('materials/disposed', views.list_disposed_materials, name='list-disposed-materials-url'),

    # ex: myequis/materials/create
    path('materials/create', views.CreateMaterialView.as_view(), name='create-material-url'),

    # ex: myequis/materials/4
    path('materials/<int:material_id>/', views.EditMaterialView.as_view(), name='edit-material-url'),

    # ex: myequis/materials/4/detail
    path('materials/<int:material_id>/detail/', views.list_material_detail, name='material-detail-url'),

    # ### DALs ####################################
    url(
        'manufacture-autocomplete/$',
        views.ManufactureAutocomplete.as_view(),
        name='manufacture-autocomplete',
    ),

    url(
        'material-autocomplete/$',
        views.MaterialAutocomplete.as_view(),
        name='material-autocomplete',
    ),

    url(
        'type-autocomplete/$',
        views.TypeAutocomplete.as_view(create_field='name'),
        name='type-autocomplete',
    ),

]
