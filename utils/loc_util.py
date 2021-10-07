from django import db
from locations.models import Location, LocationType, LocationStatus 
from locations.models import LocationPrecision, LocationRelation
import pandas as pd
from utils.model_util import info

class city_info(info):
	def __init__(self,line):
		assert type(line) == list, 'input should be list '+ str(line)
		assert len(line) == 19, 'lenght of line should be 19 ' + str(line)
		self.line = line
		m = 'geonameid,name,asciiname,alternatenames,latitude,longitude'
		m += ',feature_class,feature_code,country_code,cc2,admin1_code'
		m += ',admin2_code,admin3_code,admin4_code,population,elevation'
		m += ',dem,timezone,modification_data'
		self.attribute_names = m.split(',')
		for i,name in enumerate(self.attribute_names):
			setattr(self,name,line[i])
		self.continent = 'NA'
		self.country='NA'

	def set_country(self,country_dict):
		try: self.country = country_dict[self.country_code]
		except: pass

	def set_continent(self, continent_dict):
		for continent in continent_dict.keys():
			if self.country in continent_dict[continent]:
				self.continent = continent

	def set_admin(self,ac1,ac2):
		code1 = self.country_code + '.' + self.admin1_code
		code2 = self.country_code + '.' + self.admin2_code
		if code1 in ac1.keys(): self.admin1_name = ac1[code1]
		else: self.admin1_name = 'NA'
		if code2 in ac2.keys(): self.admin2_name = ac2[code2]
		else: self.admin2_name = 'NA'
		

	def make_location(self):
		self.location = Location( 
			geonameid = self.geonameid,
			latitude = self.latitude,
			longitude = self.longitude,
			name = self.name,
			location_type = LocationType.objects.get(name='city'),
			location_status = LocationStatus.objects.get(name='non-fiction'),
			location_precision= LocationPrecision.objects.get(name='exact'),
			information = str(self.__dict__)
		)
		return self.location




class country_info(info):
	'''country information for one country from geonames (see below).'''
	def __init__(self,line):
		'''set information from columns into attributes and create country
		(code, name) tuple.'''
		assert type(line) == list, 'input should be list ' + str(line)
		m = 'lenght should be 19 is: ' + str(len(line)) +' '+str(line)
		assert len(line) == 19,m 
		self.line = line
		m = 'iso,iso3,iso_numeric,fips,country,captial,area_km,population'
		m += ',continent,tld,currency_code,currency_name,phone'
		m += ',postal_code_format,postal_code_regex,languages,geonameid'
		m += ',neighbours,equivalentfipscode'
		self.attribute_names = m.split(',')
		for i,name in enumerate(self.attribute_names):
			setattr(self,name,line[i])
		self.code_name = (self.iso,self.country)
		self.continent_code = self.continent
		ccd = code2continent_dict()
		self.continent = ccd[self.continent]

	def make_location(self):
		self.location = Location(
			geonameid = self.geonameid,
			name = self.country,
			location_type = LocationType.objects.get(name='country'),
			location_status = LocationStatus.objects.get(name='non-fiction'),
			location_precision= LocationPrecision.objects.get(name='exact'),
			information = str(self.__dict__),
			active = True
		)
		return self.location

class admin_info(info):
	def __init__(self,line, level):
		'''set information from columns into attributes.
		level should be set to the administration level of geonames
		higher number is a more specific region'''
		assert type(line) == list, 'input should be list '+str(line)
		m = 'lenght should be 4 is: ' +str(len(line)) +' '+str(line)
		assert len(line) == 4, m
		self.line = line
		self.level = level
		m = 'admin_code,name,name_ascii,geonameid'
		self.attribute_names = m.split(',')
		for i,name in enumerate(self.attribute_names):
			setattr(self,name,line[i])


	def __repr__(self):
		return self.name

	def __str__(self):
		return self.name


class language_info(info):
	def __init__(self,line):
		assert type(line) == list, 'input should be list'
		assert len(line) == 4, 'lenght of line should be 4'
		self.line = line
		m = 'iso639_3,iso_639_2,iso_639_1,language_name'
		self.attribute_names = m.split(',')
		for i,name in enumerate(self.attribute_names):
			setattr(self,name,line[i])
		self.code_name = (self.iso639_3,self.language_name)

	def make_language(self):
		self.language = Language(name = self.language_name, iso = self.iso639_3)
		return self.language
		

def country2continent_dict(countries):
	ccd = code2continent_dict()
	output = {} 
	for continent in ccd.values():
		m = str(continent) + ' already in '+str(output.keys())
		assert continent not in output.keys(),m 
		output[continent] = []
		for country in countries:
			name = country.country
			if country.continent == continent: output[continent].append(name)
	return output

def code2continent_dict():
	output = {
		'AF':'Africa',
		'AS':'Asia',
		'EU':'Europe',
		'NA':'North America',
		'OC':'Oceania',
		'SA':'South America',
		'AN':'Antartica',
		}
	return output
	

def open_table(f):
	return [line.split('\t') for line in open(f).read().split('\n')]

def make_languages(filename= ''):
	if filename == '':f = 'data/iso-languagecodes.txt' 
	else: f= filename
	languages = open_table(f)
	output = []
	for language in languages[1:]:
		if language == ['']: continue
		output.append(language_info(language))
	return output

def make_admin(level = 1):
	assert level in [1,2], 'level should be 1 or 2, is '+str(level)
	f = 'data/admin'+str(level)+'codes.txt'
	admins = open_table(f)
	output = []
	for admin in admins:
		if admin == ['']: continue
		output.append(admin_info(admin,level=level))
	return output

def make_admin2name_dict(level = 1):
	admins = make_admin(level = level)
	output = {}
	for admin in admins:
		if admin.admin_code in output.keys():
			raise ValueError(str(admin.admin_code)+ ' already in keys')
		output[admin.admin_code] = admin.name
	return output, admins

def make_countries(filename= ''):
	if filename == '':f = 'data/country_codes.txt'
	else: f= filename
	countries = open_table(f)
	output = []
	for country in countries:
		if country == ['']: continue
		output.append(country_info(country))
	return output

def make_country_dict(filename= ''):
	countries = make_countries(filename)
	output = []
	for country in countries:
		output.append(country.code_name)
	return dict(output), countries
		

def make_cities(filename=''):
	if filename == '': f = 'data/cities500.txt'
	cities = open_table(f)
	countries_dict, countries = make_country_dict()
	admin1_dict, admins1 = make_admin2name_dict(level=1)
	admin2_dict, admins2 = make_admin2name_dict(level=2)
	country2continent = country2continent_dict(countries)
	output = []
	for city in cities:
		if city == ['']: continue
		output.append(city_info(city))
		output[-1].set_admin(admin1_dict,admin2_dict)
		output[-1].set_country(countries_dict)
		output[-1].set_continent(country2continent)
	return output

default_countries = 'United Kingdom,France,Netherlands,Germany,Italy,Swiss,Spain'
default_countries += ',Portugal,Austria,Denmark,Norway,Sweden,Finland,Belgium'
default_countries += ',Luxembourg,Ireland,Poland,slovenia'
default_countries = default_countries.split(',')

exclud_countries = 'Antigua and Barbuda,Anguilla,Antartica,American Samoa'
exclud_countries +=',Aland Islands,Falkland Islands'
exclud_countries += ',Saint Barthelemy,Bouvet Island,Seychelles,French Polynesia'
exclud_countries += ',Cocos Islands,Cabo Verde,Christmas Island,Fiji'
exclud_countries += ',Micronesia,FaroeIslands'
exclud_countries += ',South Georgia and the South Sandwich Islands'
exclud_countries += ',Heard Island and McDonald Islands'
exclud_countries += ',British Indian Ocean Territory'
exclud_countries += ',Kiribati,Comoros,Saint Kitts and Nevis,Saint Martin'
exclud_countries += ',Marshall Islands'
exclud_countries += ',Northern Mariana Islands,Martinique,Montserrat,Mauritius'
exclud_countries += ',Maldives'
exclud_countries += ',New Caledonia,Norfolk Island,Nauru,Niue'
exclud_countries += ',Saint Pierre and Miquelon'
exclud_countries += ',Reunion,Solomon Islands,Saint Helena'
exclud_countries += ',Svalbard and Jan Mayen,San Marino'
exclud_countries += ',Sao Tome and Principe,Eswatini,Turks and Caicos Islands'
exclud_countries += ',French Southern Territories,Tokelau,Timor Leste,Tonga'
exclud_countries += ',Trinidad and Tobago'
exclud_countries += ',Tuvalu,United States Minor Outlying Islands'
exclud_countries += ',Saint Vincent and the Grenadines'
exclud_countries += ',Vanuatu,Wallis and Futuna,Samoa,Mayotte'
exclud_countries += ',Netherlands Antilles'
exclud_countries += ',Puerto Rico,British Virgin Islands'
exclud_countries += ',U.S. Virgin Islands,Saint Lucia'
exclud_countries = exclud_countries.split(',')
exclud_countries.append('Bonaire, Saint Eustatius and Saba ')

ec = exclud_countries
all_countries = [c.country for c in make_countries() if c.country not in ec]

def make_country2city_dict(countries,cities):
	cd,cld = {},{}
	city_locations = Location.filter(location_type='city')
	for country in countries:
		if country.country not in cd.keys(): cd[country.country]=[]
		for c in cities:
			if c.country == country.country: cd[country.country].append(c.name)
	for country in cd.keys():
		if country not in cld.keys(): cld[country]=[]
		for cl in city_locations:
			if cl.name in cd[country]: cld[country].append(cl)
	return cd, cld

def make_location_dict(cities,countries):
	ld = {}
	for c in cities:
		ld[c.geonameid] = c
	for c in countries:
		ld[c.geonameid] = c
	return ld



def _save_locations(locations,loctype = 'unk', verbose=True):
	saved, already_exists, error = [],[],[]
	for l in locations:
		try: l.save() 
		except db.IntegrityError: already_exists.append(l)
		except: error.append(l)
		else: saved.append(l)
	if verbose:
		print('saving location type:',loctype)
		print('saved: ',len(saved),'already_exists: ',len(already_exists),
			'error: ',len(error))
	return saved, already_exists, error

def make_locations(countries='all', min_size_cities = 1000, save = True):
	if countries == 'default':countries = default_countries
	if countries == 'all':countries = all_countries
	assert type(countries) == list
	cities = make_cities()
	print('cities made')
	cities = [c for c in cities
		if int(c.population) > min_size_cities and c.country in countries]
	city_locations = [c.make_location() for c in cities]
	print('city locations made')
	country_locations = [c.make_location() for c in make_countries()
		if c.country in countries]
	print('country locations made')
	if save:
		print('saving')
		city_results = _save_locations(city_locations,'cities')
		country_results = _save_locations(country_locations,'countries')
		glr = make_locationrelations()
	return cities, city_results, country_results, glr

def make_locationrelations():
	glr = [] 
	city_id = LocationType.objects.get(name='city').id
	country_id = LocationType.objects.get(name='country').id
	country_locations = Location.objects.filter(location_type=country_id)
	city_locations = Location.objects.filter(location_type=city_id)
	for country in country_locations:
		cloc = []
		for c in city_locations:
			try: ccountry = eval(c.information)['country']
			except: continue
			if country.name == ccountry: cloc.append(c)
		glr.extend([LocationRelation(container=country,contained=city)
			for city in cloc])
	_save_locations(glr,'locationrelation')
	return glr

def make_locationtype():
	for name in 'region,city,country,continent'.split(','):
		l = LocationType(name=name)
		try:l.save()
		except:print(name,'already exists')

def make_locationstatus():
	for name in 'fiction,non-fiction'.split(','):
		l = LocationStatus(name=name)
		try:l.save()
		except:print(name,'already exists')

def make_locationprecision():
	for name in 'exact,approximate,rough'.split(','):
		l = LocationPrecision(name=name)
		try:l.save()
		except:print(name,'already exists')


def make_database_languages():
	l = make_languages()
	o = [lang.make_language() for lang in l]
	language_results = _save_locations(o,'languages')
	

def make_database_defaults():
	make_locationtype()
	make_locationstatus()
	make_locationprecision()
	make_locations()
	make_locationrelations()
	make_database_languages()

def add_geoloactions_country(country):
	return make_geolocations([country])
	

def delete_all_geolocations():
	geolocs = Location.objects.all()
	_=[gl.delete() for gl in geolocs]
	
	
def country2admins_dict(cities):
	'''link all administrive regions to appropriate country.'''
	o = {}
	for city in cities:
		if not city.country in o.keys(): o[city.country] = []
		if city.admin1_name != 'NA': 
			if city.admin1_name not in o[city.country]:
				o[city.country].append(city.admin1_name)
		if city.admin2_name != 'NA': 
			if city.admin2_name not in o[city.country]:
				o[city.country].append(city.admin2_name)
	return o

def admin2cities_dict(cities):
	'''link all cities to appropriate administrive region.
	WIP: does not take into account double admin names.
	'''
	o = {}
	for city in cities:
		if city.admin1_name != 'NA': 
			if not city.admin1_name in o.keys(): o[city.admin1_name] = []
			o[city.admin1_name].append(city.name)
		if city.admin2_name != 'NA': 
			if not city.admin2_name in o.keys(): o[city.admin2_name] = []
			o[city.admin2_name].append(city.name)
	return o
		
def check_region_present(filename = 'data/region_names.xlsx', cities = None):
	'''check whether region in xlsx file is present in geonames data.'''
	xls = pd.ExcelFile('data/region_names.xlsx')
	countries = xls.sheet_names
	if cities == None: cities = make_cities() 
	country2admin = country2admins_dict(cities)
	missing_countries = []
	country2missing_region, country2present_region = {}, {}
	for country in countries:
		if country not in country2admin.keys(): 
			missing_countries.append(country)
			continue
		admins = country2admin[country]
		regions = [i[0] for i in xls.parse(country).values.tolist() if i]
		print(country,admins,regions)
		country2missing_region[country], country2present_region[country]=[],[]
		for region in regions:
			if region not in admins: 
				country2missing_region[country].append(region)
			else: country2present_region[country].append(region)
	return missing_countries,country2missing_region,country2present_region


# add missing region locations (only mentioned in geoinformation) to db
def find_locations_region_not_in_db():
	l = Location.objects.all()
	linked_to_region = [x for x in l if x.region and not x.contained_by_region]
	return linked_to_region

def find_locations_country_not_in_db():
	l = Location.objects.all()
	linked_to_country=[x for x in l if x.country and not x.contained_by_country]
	return linked_to_country

def add_country_and_link(country_name,location, verbose = True):
	country = Location.objects.filter(name=country_name,
		location_type__name = 'country')
	location_type = LocationType.objects.get(name = 'country')
	if len(country) < 1:
		if verbose:print('adding',country_name,'to db')
		country = Location(name= country_name, location_type=location_type)
		country.save()
	elif len(country) > 1:
		raise ValueError('found multiple entries in db',country)
	else: country = country[0]
	add_relation(container=country, contained = location, 
		container_type = 'country')
	
	

def add_region_and_link(region_name,location, verbose = True):
	'''adding a region location to database'''
	region = Location.objects.filter(name=region_name, 
		location_type__name='region')
	location_type = LocationType.objects.get(name='region')
	if len(region) < 1:
		# if the region is not in the database add it
		if verbose:print('adding',region_name,'to db')
		region= Location(name = region_name,location_type = location_type)
		region.save()
		if location.country:
			# if the location has country information add it to the region
			country = Location.objects.get(name = location.country,
				location_type__name='country')
			lr = LocationRelation(container=country, contained=region)
			lr.save()
		print('adding region country relation to db:',lr)
	elif len(region) > 1: 
		# if there are multiple regions with the same name, select one with same 
		# country
		print('found multiple regions:',region)
		r = False
		if location.country:
			for reg in region:
				if reg.country == location.country: r = reg
		else:  
			for reg in region:
				if reg.country == '': r = reg
		if not r: raise ValueError('could not match region',region)
		else: 
			print('selected region linked to country:',region.country)
			print('identical to location country:',location.country)
			region = r
	else:
		region = region[0]
		add_relation(container = region, contained = location, 
			container_type = 'region')

def add_relation(container,contained,container_type,verbose=True):
	lr_check = LocationRelation.objects.filter(container=container,
		contained=contained)
	if lr_check:
		print(container_type,'location relation already exists in db:',lr_check)
		return
	lr = LocationRelation(container=container, contained=contained)
	lr.save()
	if verbose:
		print('adding',container_type,'location relation to db:')
		print(lr)
	
def add_location_region_to_db(location,verbose = True):
	''' add region relation to this location if it is not present in the 
	database and if there is region information on this location.'''
	if location.contained_by_region: # this check database region relation
		if verbose:
			print(location,'region relation:',location.region, 'already in db')
		return
	if not location.region: 
		# this falls back to geo information and uses region info
		# potentially not in the database
		if verbose:print('no region associated with location:',location)
		return
	# there is region information not in database, adding this to database
	region_name = location.region
	add_region_and_link(region_name,location,verbose)

def add_location_country_to_db(location,verbose = True):
	if location.contained_by_country:
		if verbose:
			print(location,'country relation:',location.region, 'already in db')
		return
	if not location.region:
		if verbose:print('no country associated with location:',location)
		return
	country_name = location.country
	add_country_and_link(country_name,location,verbose)


def add_all_location_countries_to_db(verbose = True, locations = None):
	if not locations: locations =Location.objects.all()
	nlocations = locations.count()
	error = []
	for i, location in enumerate(locations):
		if not location.location_type:
			error.append(location)
			continue
		if location.location_type.name == 'city':
			print('handling',i,nlocations,location)
			add_location_country_to_db(location,verbose)
	return error
	

def add_all_location_regions_to_db(verbose = True, add_countries = False):
	''' add all region location relation to the database. '''
	locations =Location.objects.all()
	region_error, country_error = [], []
	if add_countries: 
		country_error = add_all_location_countries_to_db(verbose,locations)
	nlocations = locations.count()
	for i,location in enumerate(locations):
		if not location.location_type:
			region_error.append(location)
			continue
		if location.location_type.name == 'city':
			print('handling',location,i,nlocations)
			add_location_region_to_db(location)
		else:print('skipping',location,location)
	if add_countries: return region_error, country_error
	return region_error

# ----

		
	
	
		
		

'''
city_info attribute name legend
https://download.geonames.org/export/dump/
The main 'geoname' table has the following fields :
---------------------------------------------------
geonameid         : integer id of record in geonames database
name              : name of geographical point (utf8) varchar(200)
asciiname         : name of geographical point in plain ascii characters, varchar
					(200)
alternatenames    : alternatenames, comma separated, ascii names automatically 
					transliterated, convenience attribute from alternatename 
					table, varchar(10000)
latitude          : latitude in decimal degrees (wgs84)
longitude         : longitude in decimal degrees (wgs84)
feature class     : see http://www.geonames.org/export/codes.html, char(1)
feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
country code      : ISO-3166 2-letter country code, 2 characters
cc2               : alternate country codes, comma separated, ISO-3166 
					2-letter country code, 200 characters
admin1 code       : fipscode (subject to change to iso code), see exceptions 
					below, see file admin1Codes.txt for display names of this 
					code; varchar(20)
admin2 code       : code for the second administrative division, a county in 
					the US, see file admin2Codes.txt; varchar(80) 
admin3 code       : code for third level administrative division, varchar(20)
admin4 code       : code for fourth level administrative division, varchar(20)
population        : bigint (8 byte int) 
elevation         : in meters, integer
dem               : digital elevation model, srtm3 or gtopo30, average elevation 
					of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area 
					in meters, integer. srtm processed by cgiar/ciat.
timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
modification date : date of last modification in yyyy-MM-dd format

'''
