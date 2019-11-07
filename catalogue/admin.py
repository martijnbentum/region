from django.contrib import admin
import inspect
import catalogue.models as models

object_list = 'Audience,Book,Fragment,Genre,Illustration,Location,Periodical'
object_list += ',Person,Publication,Publisher,PublisherManager,Text'
object_list += ',PersonWorkRelation,PersonWorkRelationRole'
object_list = object_list.split(',')


for name, obj in inspect.getmembers(models):
	if inspect.isclass(obj) and name in object_list:
		admin.site.register(obj)



# Register your models here.
