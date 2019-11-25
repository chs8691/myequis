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

    # ex: myequis/bicycles/5/parts
    path('bicycles/<int:bicycle_id>/parts', views.list_bicycle_parts, name='list-bicycle-parts-url'),

    # ex: myequis/bicycles/5/part/4/mount
    path('bicycles/<int:bicycle_id>/part/<int:part_id>/mount', views.MountPartView.as_view(),
         name='mount-part-url'),

    # ex: myequis/bicycles/5/part/4/edit
    path('bicycles/<int:bicycle_id>/part/<int:part_id>/edit', views.EditPartView.as_view(),
         name='edit-part-url'),

    # ex: myequis/bicycles/5/part/4/exchange
    path('bicycles/<int:bicycle_id>/part/<int:part_id>/exchange', views.ExchangePartView.as_view(),
         name='exchange-part-url'),

    # ex: myequis/bicycles/5/part/4/dismount
    path('bicycles/<int:bicycle_id>/part/<int:part_id>/dismount', views.DismountPartView.as_view(),
         name='dismount-part-url'),

    # ex: myequis/records/create_record?bicycle_id=1
    path('bicycles/<int:bicycle_id>/create-record', views.CreateRecordView.as_view(), name='create-record-url'),

    # ex: myequis/records/4
    path('records/<int:record_id>/', views.EditRecordView.as_view(), name='edit-record-url'),
    
    # ex: myequis/materials/5/
    path('<int:material_id>/', views.material, name='material'),
    
    # ex: myequis/newmaterials/
    path('newmaterials/', views.newmaterials, name='newmaterials'),
    ]
