from django.urls import include,path,re_path

from . import views


app_name = 'catalogue'
urlpatterns = [
	path('',views.text_list,name='text_view'),
	path('ajax_test/',views.ajax_test,name='ajax_test'),
	path('hello_world/',views.hello_world,name='hello_world'),
	path('add_illustration/', views.edit_illustration, name='add_illustration'),
	path('add_text/', views.edit_text, name='add_text'),
	path('add_periodical/', views.edit_periodical, name='add_periodical'),
	path('add_publication/', views.edit_publication, name='add_publication'),
	path('add_publisher/', views.edit_publisher, name='add_publisher'),
	path('add_illustration/<str:view>', views.edit_illustration, 
		name='add_illustration'),
	path('add_text/<str:view>', views.edit_text, name='add_text'),
	path('add_periodical/<str:view>', views.edit_periodical, name='add_periodical'),
	path('add_publication/<str:view>', views.edit_publication, 
		name='add_publication'),
	path('add_publisher/<str:view>', views.edit_publisher, name='add_publisher'),
	path('edit_text/<int:pk>', views.edit_text, name='edit_text'),
	path('edit_text/<int:pk>/<str:focus>', views.edit_text, name='edit_text'),
	path('edit_periodical/<int:pk>', views.edit_periodical, name='edit_periodical'),
	path('edit_periodical/<int:pk>/<str:focus>', views.edit_periodical, name='edit_periodical'),
	path('edit_publication/<int:pk>', views.edit_publication, name='edit_publication'),
	path('edit_publication/<int:pk>/<str:focus>', views.edit_publication, 
		name='edit_publication'),
	path('edit_publisher/<int:pk>', views.edit_publisher, name='edit_publisher'),
	path('edit_publisher/<int:pk>/<str:focus>', views.edit_publisher, name='edit_publisher'),
	path('edit_illustration/<int:pk>', views.edit_illustration, 
		name='edit_illustration'),
	path('edit_illustration/<int:pk>/<str:focus>', 
		views.edit_illustration, name='edit_illustration'),
	path('text/',views.text_list, name='text_list'),
	path('publication/',views.publication_list,name='publication_list'),
	path('publisher/',views.publisher_list,name='publisher_list'),
	path('periodical/',views.periodical_list,name='periodical_list'),
	path('illustration/',views.illustration_list,
		name='illustration_list'),
	path('delete/<int:pk>/<str:model_name>', views.delete, name='delete'),
]



def create_simple_path(name):
	'''creates a simple view based on the model name
	Assumes the form only has a name field.
	'''
	n = views.make_fname(name)
	o = []
	p = "path('add_"+n+"/', views.add_"+n+" , name='add_"+n+"')"
	o.append(eval(p))
	p = "path('add_"+n+"/<int:pk>', views.add_"+n+" , name='add_"+n+"')"
	o.append(eval(p))
	return o

names = 'Genre,TextType,CopyRight,IllustrationCategory,PublicationType'
names += ',TextTextRelationType,IllustrationIllustrationRelationType'
names += ',IllustrationType'
for name in names.split(','):
	urlpatterns.extend(create_simple_path(name))

temp = [
	path('add_texttext_relation_type',views.add_text_text_relation_type,
		name='add_texttext_relation_type'),
	path('add_illustrationillustration_relation_type',views.add_illustration_illustration_relation_type,
		name='add_illustrationillustration_relation_type'),
	path('add_illustration_type/', views.add_illustration_type, name='add_illustration_type'),
	path('add_illustration_category/', views.add_illustration_category, 
		name='add_illustration_category'),
	path('add_publication_type/', views.add_publication_type, name='add_publication_type'),
	path('add_copy_right/', views.add_copy_right, name='add_copy_right'),
	path('add_genre/', views.add_genre, name='add_genre'),
	path('add_text_type/', views.add_text_type, name='add_text_type'),

]
