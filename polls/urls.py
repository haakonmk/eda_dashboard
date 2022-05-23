from django.urls import path

from . import views
from eda.dash_apps.finished_apps import plot_EDA, plot_RAD, dashboard, tables, comparison_rad, comparison_temp, comparison_co2, comparison_rh

urlpatterns = [
    path('', views.index, name='index'),
    path('tables/', views.tables, name='tables'),
    path('radiation/', views.radiation, name='radiation'),
    path('environmental/', views.environmental, name='environmental'),
    path('comparison_radiation/', views.comparison_rad, name='comparison_rad'),
    path('comparison_temperature/', views.comparison_temp, name='comparison_temp'),
    path('comparison_co2/', views.comparison_co2, name='comparison_co2'),
    path('comparison_rh/', views.comparison_rh, name='comparison_rh'),

]
