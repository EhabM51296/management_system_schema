from django.urls import path
from . import views

urlpatterns = [
    path('schema/create', views.create_table, name='create_table'),
    path('schema/update', views.update_table, name='update_table'),
    path('schema/delete', views.delete_table, name='delete_table'),
    path('record/create', views.create_record, name='create_record'),
    path('record/read', views.read_records, name='read_records'),
    path('data/update', views.update_record, name='update_record'),
    path('record/delete', views.delete_record, name='delete_record'),
]