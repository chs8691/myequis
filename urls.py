from django.urls import path

from . import views

app_name = 'myequis'
urlpatterns = [
    # ex: /myequis/
    path('', views.index, name='index-url'),

    # ex: myequis/bicycles/5/
    path('bicycles/<int:bicycle_id>/', views.bicycle_detail, name='bicycle-detail-url'),
    
    # ex: myequis/bicycles/5/records
    path('bicycles/<int:bicycle_id>/records', views.list_records, name='list-records-url'),

    # ex: myequis/records/create_record?bicycle_id=1
    path('bicycles/<int:bicycle_id>/create-record', views.CreateRecordView.as_view(), name='create-record-url'),

    # ex: myequis/records/4
    path('records/<int:record_id>/', views.EditRecordView.as_view(), name='edit-record-url'),
    
    # ex: myequis/materials/5/
    path('<int:material_id>/', views.material, name='material'),
    
    # ex: myequis/newmaterials/
    path('newmaterials/', views.newmaterials, name='newmaterials'),
    ]
