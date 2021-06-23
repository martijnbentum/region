from django.urls import include,path,re_path

from . import views


app_name = 'utilities'
urlpatterns = [
	path('close/',views.close,name='close'),
	path('list_view/<str:model_name>/<str:app_name>/',views.list_view,name='list_view'),
	path('list_view/<str:model_name>/<str:app_name>/<int:max_entries>',views.list_view,
		name='list_view'),
	path('timeline/',views.timeline,name='timeline'),
	path('add_comment/<str:app_name>/<str:model_name>/<int:entry_pk>/',views.edit_comment,
		name='add_comment'),
]
