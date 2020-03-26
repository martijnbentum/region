from utilities.models import Language
from django import db
from locations.models import GeoLoc as Location
from locations.models import GeoLoc, UserLoc, LocType
from locations.models import GeoLocsRelation 
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
			location_type = 'CITY'
		)
		return self.location


class country_info(info):
	'''country information for one country from geonames (see below).'''
	def __init__(self,line):
		'''set information from columns into attributes and create country
		(code, name) tuple.'''
		assert type(line) == list, 'input should be list ' + str(line)
		assert len(line) == 19, 'lenght should be 19 is: ' + str(len(line)) +' '+str(line)
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
			location_type = 'COUNTRY'
		)
		return self.location

class admin_info(info):
	def __init__(self,line, level):
		'''set information from columns into attributes.
		level should be set to the administration level of geonames
		higher number is a more specific region'''
		assert type(line) == list, 'input should be list '+str(line)
		assert len(line) == 4, 'lenght should be 4 is: ' +str(len(line)) +' '+str(line)
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
		assert continent not in output.keys(), str(continent) + ' already in '+str(keys)
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

all_countries = [c.country for c in make_countries()]

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

def make_geolocations(countries='default', min_size_cities = 5000, save = True):
	if countries == 'default':countries = default_countries
	if countries == 'all':countries = all_countries
	assert type(countries) == list
	cities = make_cities()
	cities = [c for c in cities
		if int(c.population) > min_size_cities and c.country in countries]
	city_locations = [c.make_location() for c in cities]
	country_locations = [c.make_location() for c in make_countries()
		if c.country in countries]
	city_results = _save_locations(city_locations,'cities')
	country_results = _save_locations(country_locations,'countries')
	glr = []
	for country in country_locations:
		cloc = [c for c in cities if c.country == country.name]
		glr.extend([GeoLocsRelation(container=country,contained=city.location)
			for city in cloc])
	_save_locations(glr,'locationrelation')
	return cities, city_results, country_results, glr

def make_userlocations():
	gl = GeoLoc.objects.all()
	lts = [LocType(name = lt[1]) for lt in gl[0].LOCATION_TYPE]
	lt_results = _save_locations(lts,'LocType')
	lt_dict = dict([(lt.name,lt) for lt in LocType.objects.all()])
	for l in gl:
		ul = UserLoc(name=l.name,loc_precision='E',status='NF',
			loc_type= lt_dict[l.location_type.lower()])
		_save_locations([ul],verbose = False)
		l.user_locs.add(ul)

def make_database_languages():
	l = make_languages()
	o = [lang.make_language() for lang in l]
	language_results = _save_locations(o,'languages')
	

def make_database_defaults():
	make_geolocations()
	make_userlocations()
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
		country2missing_region[country], country2present_region[country] = [] , []
		for region in regions:
			if region not in admins: country2missing_region[country].append(region)
			else: country2present_region[country].append(region)
	return missing_countries,country2missing_region,country2present_region
		
		

'''
city_info attribute name legend
https://download.geonames.org/export/dump/
The main 'geoname' table has the following fields :
---------------------------------------------------
geonameid         : integer id of record in geonames database
name              : name of geographical point (utf8) varchar(200)
asciiname         : name of geographical point in plain ascii characters, varchar(200)
alternatenames    : alternatenames, comma separated, ascii names automatically transliterated, convenience attribute from alternatename table, varchar(10000)
latitude          : latitude in decimal degrees (wgs84)
longitude         : longitude in decimal degrees (wgs84)
feature class     : see http://www.geonames.org/export/codes.html, char(1)
feature code      : see http://www.geonames.org/export/codes.html, varchar(10)
country code      : ISO-3166 2-letter country code, 2 characters
cc2               : alternate country codes, comma separated, ISO-3166 2-letter country code, 200 characters
admin1 code       : fipscode (subject to change to iso code), see exceptions below, see file admin1Codes.txt for display names of this code; varchar(20)
admin2 code       : code for the second administrative division, a county in the US, see file admin2Codes.txt; varchar(80) 
admin3 code       : code for third level administrative division, varchar(20)
admin4 code       : code for fourth level administrative division, varchar(20)
population        : bigint (8 byte int) 
elevation         : in meters, integer
dem               : digital elevation model, srtm3 or gtopo30, average elevation of 3''x3'' (ca 90mx90m) or 30''x30'' (ca 900mx900m) area in meters, integer. srtm processed by cgiar/ciat.
timezone          : the iana timezone id (see file timeZone.txt) varchar(40)
modification date : date of last modification in yyyy-MM-dd format
'''
