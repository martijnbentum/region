from django.contrib import admin
import inspect
import catalogue.models as models

object_list = 'Audience,Book,Fragment,Genre,Illustration,Periodical'
object_list += ',LocationType,LocationLocationRelation'
object_list += ',Person,Publication,PublisherManager,Publisher'
object_list += ',PersonWorkRelation,PersonWorkRelationRole,TextTextRelationType'
object_list = object_list.split(',')


for name, obj in inspect.getmembers(models):
	if inspect.isclass(obj) and name in object_list:
		admin.site.register(obj)

class LocationLocationRelationContainer(admin.TabularInline):
	model = models.LocationLocationRelation
	extra = 1
	fk_name = 'container'

class LocationLocationRelationContained(admin.TabularInline):
	model = models.LocationLocationRelation
	extra = 1
	fk_name = 'contained'

class LocationAdmin(admin.ModelAdmin):
	inlines = (LocationLocationRelationContainer,LocationLocationRelationContained)


class TextTextRelationPrimary(admin.TabularInline):
	model = models.TextTextRelation
	extra = 1
	fk_name = 'primary'

class TextTextRelationSecondary(admin.TabularInline):
	model = models.TextTextRelation
	extra = 1
	fk_name = 'secondary'

class TextAdmin(admin.ModelAdmin):
	inlines = (TextTextRelationPrimary,TextTextRelationSecondary)


admin.site.register(models.Location, LocationAdmin)
admin.site.register(models.Text, TextAdmin)

# Register your models here.
