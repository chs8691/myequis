from django.urls import path

from . import views
from myequis.views import UpdateRecordView

app_name = 'myequis'
urlpatterns = [
    # ex: /myequis/
    path('', views.index, name='index'),

    # ex: myequis/bicycles/5/
    path('bicycles/<int:bicycle_id>/', views.bicycle, name='bicycle'),
    
    # ex: myequis/bicycles/5/records
    path('bicycles/<int:bicycle_id>/records', views.records, name='records'),

    # ex: myequis/bicycles/5/create_record
    path('bicycles/<int:bicycle_id>/create_record', views.create_record, name='create_record'),
    
    # Update record
    # ex: myequis/records/4
    #path('records/<int:record_id>/', views.record, name='record'),
    path('records/<int:record_id>/', UpdateRecordView.as_view(), name='record'),
    
    # ex: myequis/materials/5/
    path('<int:material_id>/', views.material, name='material'),
    
    # ex: myequis/newmaterials/
    path('newmaterials/', views.newmaterials, name='newmaterials'),
    ]
