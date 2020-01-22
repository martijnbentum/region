from django.urls import include,path,re_path

from . import views


app_name = 'catalogue'
urlpatterns = [
	path('', views.PersonView.as_view(), name='person_view'),
	path('add_text/', views.add_text, name='add_text'),
	path('text/',views.TextView.as_view(),name='text_view'),
	path('add_person/', views.add_person, name='add_person'),
	path('edit_person/<int:person_id>', views.edit_person, name='edit_person'),
	path('person/<int:person_id>',views.person_detail,name='person_detail'),
]
