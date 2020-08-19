from locations.models import UserLoc,GeoLoc,Location
from .hloc_util import make_locationtype, make_locationstatus, make_locationprecision
from locations.models import Location, LocationType, LocationStatus, LocationPrecision
from locations.models import LocationRelation 

def make():
	make_locationtype()
	make_locationstatus()
	make_locationprecision()

def userloc2Location(ul):
	gls = ul.geoloc_set.all()
	

def geoloc2location(gl, save = False):
	names = 'name,geonameid,coordinates_polygon,latitude,longitude,information'.split(',')
	kw = dict([[n,getattr(gl,n)] for n in names])
	l = Location(**kw)
	l.location_type = LocationType.objects.get(name=gl.location_type.lower())
	ul = gl.user_locs.all()
	l.active = True if ul.count() > 0 else False
	if save: l.save()
	return l





