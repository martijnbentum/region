from django.apps import apps
import json
from utils import location_to_linked_instances as ltli
from utils.model_util import get_all_models

class Timelines():
	def __init__(self,timeline_form = None, timelines = [], make = True,
		year_padding = 15, nyears_per_category = 3, add_background_bins = False):
		timeline_form
		self.timelines = timelines
		self.year_padding = year_padding
		self.nyears_per_category = nyears_per_category
		self.add_background_bins = add_background_bins
		if timeline_form: self._handle_form(timeline_form)
		if make: self.make()

	def _handle_form(self, form):
		if self.timelines: self.timelines = []
		if form.is_valid(): 
			self.ok = True
			for i in range(4):
				mn = form.cleaned_data['model_name' + str(i+1)]
				if not mn:continue
				app_name, self.model_name = mn.app_name, mn.model_name.lower()
				model = apps.get_model(mn.app_name,mn.model_name)
				location = form.cleaned_data['location' + str(i+1)]
				timeline = Timeline(mn.app_name,mn.model_name,location,index = i)
				if timeline: self.timelines.append(timeline)
		else: self.ok = False

	def _combine_all_dates(self):
		self.all_dates = []
		for timeline in self.timelines:
			self.all_dates.extend(timeline.all_dates)

	def _combine_year_dicts(self):
		'''creates a dictionary with years linking to each category e.g. text
		these link to a list of date lines describing an instance in that category
		not used for making bins
		'''
		self.year_dict = {}
		for timeline in self.timelines:
			yd = timeline.year_dict
			name = timeline.model_name
			for year in yd.keys():
				if year not in self.year_dict.keys():self.year_dict[year] = {}
				self.year_dict[year][name] = yd[year]
		self.year_dict = sort_year_dict(self.year_dict)

	def _handle_padding(self):
		'''pads start and end year (earliest and latest instance) to make
		it divisible between nyears_per_bin
		'''
		extra_padding = compute_extra_padding( self.nyears_per_bin, self.nyears+1)
		start_padding = int(extra_padding/2)
		end_padding = int(extra_padding/2) + extra_padding % 2
		self.start_year -= start_padding
		self.end_year += end_padding
		self.nyears = self.end_year - self.start_year

	def _make_backgroud_bin(self,start,end,index):
		if index % 2: color = '#fcfaf2'
		else: color = '#fcfbf7'
		d = {'name':'background','start':start,'end':end+1}
		d.update({'color':color})
		return d

	def _make_bin(self, bin_start,bin_end):
		'''a bin is a list of dictionaries with count of instances in a time span
		spanning bin_start to bin end for.
		there is dictionary for category in the Timelines object
		each bin is divided into equal parts to show the different categories
		side by side
		'''
		start_end=make_start_end_years(bin_start,bin_end,self.nyears_per_category)
		o = []
		for timeline, se in zip(self.timelines,start_end):
			start, end = se
			name = timeline.model_name
			instances = timeline.get_date_lines(bin_start,bin_end)
			ids = [x['id'] for x in instances]
			d = {'name':name,'start':start,'end':end+1}
			d.update({'ids':ids,'count':len(instances),'color':timeline.color})
			d.update({'start_year':bin_start,'end_year':bin_end})
			o.append(d)
			if len(instances) > self.max_bin_count: self.max_bin_count = len(instances)
		stacked_bin_count = sum([x['count'] for x in o])
		if stacked_bin_count> self.max_stacked_bin_count: 
			self.max_stacked_bin_count = stacked_bin_count
		return o

	def _make_bins(self):
		self.nyears_per_bin = self.nyears_per_category * self.ncategories +1
		self._handle_padding()
		self.start_end_years = make_start_end_years(self.start_year,self.end_year,
			self.nyears_per_bin)
		self.bins,self.flattened_bins = [], []
		self.max_bin_count = 0 
		self.max_stacked_bin_count = 0
		for i, start_end in enumerate(self.start_end_years):
			start, end = start_end
			if self.add_background_bins:
				background_bin = self._make_backgroud_bin(start,end,i)
				self.flattened_bins.append(background_bin)
			b = self._make_bin(start,end)
			self.bins.append(b)
			self.flattened_bins.extend(b)

	
	def make(self):
		self.names = [t.name for t in self.timelines]
		self.ncategories = len(self.names)
		self.ninstance_per_name = [x.ninstances for x in self.timelines]
		tl= self.timelines
		self.index2ninstances=dict([[str(t.index)+'_count',t.ninstances] for t in tl])
		self.index2color=dict([[str(t.index)+'_color',t.color] for t in tl])
		self._combine_all_dates()
		self._combine_year_dicts()
		padding = self.year_padding
		self.start_year = min([t.start_year for t in self.timelines]) - padding
		self.end_year = max([t.end_year for t in self.timelines]) + padding
		self.nyears = self.end_year - self.start_year
		self.max_count = max([t.max_count for t in self.timelines])
		self._make_bins()

	def make_json(self):
		d = {'start_year':self.start_year,'end_year':self.end_year}
		d.update({'max_bin_count':self.max_bin_count,'names':self.names})
		d.update({'max_stacked_bin_count':self.max_stacked_bin_count})
		d.update({'bins':self.flattened_bins})
		d.update({'ninstances':sum(self.ninstance_per_name)})
		d.update(self.index2ninstances)
		d.update(self.index2color)
		self.dict = d
		return json.dumps(self.dict)

		

class Timeline():
	def __init__(self,app_name = '',model_name = '',location = None, make = True,
		index = 0):
		self.app_name, self.model_name = app_name, model_name.lower()
		self.name = self.model_name + '_' + str(index)
		self.location = location
		self.ok = False
		self.index = index
		self.color = make_color_list()[index]
		if make: self.make()

	def make(self):
		if self.app_name and self.model_name:
			self.model = apps.get_model(self.app_name,self.model_name)
			self.color = make_color_list()[self.index]
			self._get_instances()
			self._make_dates()
			self._make_year_dict()
			years = list(self.year_dict.keys())
			self.start_year = years[0]
			self.end_year = years[-1]
			self.max_count = max( list(self.year_dict.values()))
			self.ninstances = len(self.instances)
			location_name = ', ' +self.location.name if self.location else ''
			self.name = self.model_name + location_name 
			self.name += ' (' + str(self.ninstances) + ')' 
			self.ok = True

	def _get_instances(self):
		get = ltli.get_instances_linked_to_locations_contained_in_location
		if self.location: self.instances = get(self.location,self.model_name) 
		else: self.instances = self.model.objects.all()

	def _make_dates(self):
		'''a date is a dict with date color, location information for one instance.
		'''
		all_dates = []
		for i,x in enumerate(self.instances):
			dates = x.get_dates
			if not dates: continue
			for d in dates:
				if not d: continue
				location = []
				if x.location_string: location.append( x.location_string )
				if self.location: location.append( self.location.name )
				location = ', '.join(location)
				year = d if type(d) == int else d.year
				t = {'id':x.identifier,'date':year,'model_name':self.model_name}
				t.update({'location':location,'color':self.color})
				all_dates.append(t)
		self.all_dates = all_dates
	
	def _make_year_dict(self):
		self.year_dict = {}
		for line in self.all_dates:
			date = line['date']
			if date in self.year_dict.keys():self.year_dict[date] += 1
			else: self.year_dict[date] = 1
		self.year_dict = sort_year_dict(self.year_dict)

	def get_date_lines(self,start_year,end_year):
		o = []
		for line in self.all_dates:
			if check_within_period(start_year,end_year,line['date']):
				o.append(line)
		return o

def make_color_list():
	return '#FAA31B,#88C6ED,#394BA0,#EF4444,#D54799,#82C341'.split(',')

def _make_timelines(n = 3):
	'''creates multiple timelines to debug Timeline and Timelines class.'''
	if n > 4: n = 4
	if n < 1: n =1
	Location = apps.get_model('locations','Location')
	france = Location.objects.get(name= 'France')
	timelines = []
	for name in 'text,publication,illustration,periodical'.split(',')[:n]:
		timelines.append(Timeline('catalogue',name,france))
	return Timelines(timelines = timelines)

		
def sort_year_dict(year_dict):
	'''sorts a dictionary with years (int) as keys in ascending order, returns dict.'''
	items = list(year_dict.items())
	items = sorted(items, key = lambda x: x[0])
	return dict(items)

def compute_extra_padding(divider, to_be_devided):
	'''computes the number to be added to to_be_devided to create equally spaced chunks.
	e.g if divider = 3 and to_be_devided = 8, to get equally spaced chunks of length 3
	it returns 1: 	1-3 4-6 7-9 
	'''
	padding = 0
	while True:
		if to_be_devided % divider == 0: break
		to_be_devided +=1
		padding +=1
	return padding

def make_start_end_years(start_year,end_year,nyears_per_bin):
	'''as list of lists with equally spaced chunks of years.
	e.g. start_year=1901,end_year=1990,nyears_per_bin=30
	returns [[1901, 1930], [1931, 1960], [1961, 1990]]
	'''
	o = []
	starts = list(range(start_year,end_year,nyears_per_bin))
	ends = list(range(start_year-1,end_year,nyears_per_bin))[1:] + [end_year]
	for start,end in zip(starts,ends):
		o.append([start,end])	
	return o

def check_within_period(start_year,end_year, year):
	return year >= start_year and year <= end_year
