from django.urls import include,path,re_path

from . import views


app_name = 'locations'
urlpatterns = [
	path('map/',views.map, name='map'),
	path('map_draw/',views.map_draw, name='map_draw'),
	path('geojson_file/<str:filename>/',views.geojson_file, name='geojson_file'),
	path('geojson_file/geojson/<str:filename>/',views.geojson_file, name='geojson_file'),
	path('show_links/<str:app_name>/<str:model_name>/<int:pk>/',views.show_links,name='show_links'),
	path('map/<str:location_name>/',views.mapp, name='mapp'),
	path('',views.location_list,name='location_list'),
	path('delete/<int:pk>/<str:model_name>', views.delete, name='delete'),
	path('location/', views.location_list, name='location_list'),
	path('add_location/', views.edit_location, name='add_location'),
	path('add_location/<str:view>', views.edit_location, name='add_location'),
	path('edit_location/<int:pk>', views.edit_location, name='edit_location'),
	path('edit_location/<int:pk>/<str:focus>', views.edit_location, name='edit_location'),
	path('add_location_status/',views.add_location_status, name='add_location_status'),
	path('add_location_precision/',views.add_location_precision, name='add_location_precision'),
	path('add_location_type/',views.add_location_type, name='add_location_type'),
	path('style/', views.style_list, name='style_list'),
	path('add_style/', views.edit_style, name='add_style'),
	path('add_style/<str:view>', views.edit_style, name='add_style'),
	path('edit_style/<int:pk>', views.edit_style, name='edit_style'),
	path('edit_style/<int:pk>/<str:focus>', views.edit_style, name='edit_style'),
	path('figure/', views.figure_list, name='figure_list'),
	path('add_figure/', views.edit_figure, name='add_figure'),
	path('add_figure/<str:view>', views.edit_figure, name='add_figure'),
	path('edit_figure/<int:pk>', views.edit_figure, name='edit_figure'),
	path('edit_figure/<int:pk>/<str:focus>', views.edit_figure, name='edit_figure'),
]
