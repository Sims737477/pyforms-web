from pyforms_web.web.Controls.ControlBase import ControlBase
from django.apps import apps
from django.db.models.constants import LOOKUP_SEP
from django.core.exceptions import FieldDoesNotExist
from django.utils.encoding import force_text
from django.utils.dateparse import parse_datetime
from django.db.models import Q
import simplejson, datetime
from django.utils import timezone
from django.conf import settings
from django.db import models
from datetime import timedelta

import locale

def get_field(model, lookup):
	# will return first non relational field's verbose_name in lookup
	parts = lookup.split(LOOKUP_SEP)
	for i, part in enumerate(parts):
		try:
			f = model._meta.get_field(part)
		except FieldDoesNotExist:
			# check if field is related
			for f in model._meta.related_objects:
				if f.get_accessor_name() == part:
					break
			else:
				raise ValueError("Invalid lookup string")

		if f.is_relation:
			model = f.related_model
			if (len(parts)-1)==i:
				return model
			else:
				continue

		return f
		

def get_verbose_name(model, lookup):
	# will return first non relational field's verbose_name in lookup
	parts = lookup.split(LOOKUP_SEP)
	for i, part in enumerate(parts):
		try:
			f = model._meta.get_field(part)
		except FieldDoesNotExist:
			# check if field is related
			for f in model._meta.related_objects:
				if f.get_accessor_name() == part:
					break
			else:
				raise ValueError("Invalid lookup string")

		if f.is_relation:
			model = f.related_model
			if (len(parts)-1)==i:
				return force_text(model._meta.verbose_name)
			else:
				continue

		return force_text(f.verbose_name)
		


class ControlQueryList(ControlBase):

	def __init__(self, label = "", defaultValue = "", helptext=''):
		self.rows_per_page 		= 10
		self._current_page 		= 1

		self.list_display 		= []
		self.list_filter 		= []
		self.search_fields  	= []

		self.search_field_key   = None
		self.filter_by 			= []
		self.sort_by 			= []
		self._selected_row_id   = -1 #row selected by the mouse

		# these informations is needed to serialize the control to the drive
		self._app 	= None
		self._model = None
		self._query = None
		####################################################################

		super(ControlQueryList, self).__init__(label, defaultValue, helptext)


	def init_form(self): return "new ControlQueryList('{0}', {1})".format( self._name, simplejson.dumps(self.serialize()) )

	def item_selection_changed_client_event(self):
		self.mark_to_update_client()
		self.item_selection_changed_event()

	def item_selection_changed_event(self): pass

	def __get_pages_2_show(self, queryset):
		if not queryset: return []

		total_rows 		= queryset.count()
		total_n_pages 	= (total_rows / self.rows_per_page) + (0 if (total_rows % self.rows_per_page)==0 else 1)
		start_page 		= self._current_page - 2
		end_page 		= self._current_page + 2

		if start_page<1:
			diff 	 	= 1 - start_page
			start_page 	= 1
			end_page 	+= diff
		if end_page>total_n_pages:
			end_page = total_n_pages
			if (end_page-4)>=1: start_page = (end_page-4)

		return [int(start_page-1) if int(start_page)>1 else -1] + list(range(int(start_page), int(end_page)+1)) + [ int(end_page+1) if int(end_page)<int(total_n_pages) else -1]



	

	@property
	def selected_row_id(self): return self._selected_row_id
	@selected_row_id.setter
	def selected_row_id(self, value): 
		self._selected_row_id = value
	
	@property
	def value(self):
		if self._app and self._model and self._query:
			# reconstruct the query ################################
			model 		= apps.get_model(self._app, self._model)
			qs 			= model.objects.all()
			qs.query 	= self._query
			for f in self.filter_by:
				qs = qs.filter(**f)

			if self.search_field_key and len(self.search_field_key)>0:
				search_filter = None
				for s in self.search_fields:
					q = Q(**{s: self.search_field_key})
					search_filter = (search_filter | q) if search_filter else q
				qs = qs.filter(search_filter)

			return qs
		else:
			return None

	@value.setter
	def value(self, value):
				
		oldvalue = self._value
		self._value = value
		if oldvalue!=value: 
			if value:
				self._model = value.model._meta.label.split('.')[-1]
				self._query = value.query
				self._app   = value.model._meta.app_label
				self._selected_row_id = -1
				
			self.mark_to_update_client()
			self.changed_event()



	def serialize(self):
		data 			= ControlBase.serialize(self)
		queryset 		= self.value

		rows 			= []
		filters_list 	= []
		headers 		= []

		if queryset:
			model 	 	 	= queryset.model
			
			row_start = self.rows_per_page*(self._current_page-1)
			row_end   = self.rows_per_page*(self._current_page)

			for sort in self.sort_by:
				direction = '-' if sort['desc'] else ''
				queryset = queryset.order_by( direction+sort['column'] )

			rows = self.queryset_to_list(queryset, self.list_display, row_start, row_end)

			if self.list_display:
				#configure the headers titles
				for column_name in self.list_display:
					headers.append({
						'label':  get_verbose_name(model, column_name),
						'column': column_name
					})
			
			filters_list = self.serialize_filters(self.list_filter, queryset)
		
		if len(self.search_fields)>0:
			data.update({'search_field_key': self.search_field_key if self.search_field_key is not None else ''})
	
		data.update({
			'filters_list': 		filters_list,
			'filter_by':			self.filter_by,
			'sort_by':				self.sort_by,
			'pages':				{'current_page': self._current_page, 'pages_list':self.__get_pages_2_show(queryset) },
			'value':				'',
			'values':				rows,
			'horizontal_headers': 	headers,
			'selected_row_id':		self._selected_row_id
		})


		return data

	






		
	def page_changed_event(self): 
		self._selected_row_id = -1
		self.mark_to_update_client()

	def sort_changed_event(self): 
		self._selected_row_id = -1
		self.mark_to_update_client()

	def filter_changed_event(self):
		self._selected_row_id = -1
		self._current_page 	  = 1
		self.mark_to_update_client()









	#####################################################################
	#####################################################################

	def format_list_column(self, col_value):		

		if isinstance(col_value, datetime.datetime ):
			return col_value.strftime('%Y-%m-%d %H:%M') if col_value else ''
		elif isinstance(col_value, datetime.date ):
			return col_value.strftime('%Y-%m-%d') if col_value else ''
		elif isinstance(col_value, bool ):
			return '<i class="check circle green icon"></i>' if col_value else '<i class="minus circle red icon"></i>'
		elif isinstance(col_value, int ):
			return locale.format("%d", col_value, grouping=True)
		elif isinstance(col_value, float ):
			return locale.format("%f", col_value, grouping=True)
		elif isinstance(col_value, int ):
			return locale.format("%d", col_value, grouping=True)
		else:
			return col_value

	def queryset_to_list(self, queryset, list_display, first_row, last_row):

		if not list_display:
			return [ [m.pk, str(m)] for m in queryset[first_row:last_row] ]
		else:
			rows = []
			queryset_list = queryset.values_list(*(['pk']+list_display) )
			for row_values in queryset_list[first_row:last_row]:
				row = [self.format_list_column(c) for c in row_values]
				rows.append(row)
			return rows


	def format_filter_column(self, col_value):
		if isinstance(col_value, datetime.datetime ):
			return col_value.strftime('%Y-%m-%d %H:%M') if col_value else ''
		elif isinstance(col_value, datetime.date ):
			return col_value.strftime('%Y-%m-%d') if col_value else ''
		elif isinstance(col_value, bool ):
			return '<i class="check circle green icon"></i>' if col_value else '<i class="minus circle red icon"></i>'
		else:
			return col_value

	def get_datetimefield_options(self, column_name):
		column_filter = "{0}__gte".format(column_name)

		now 			= timezone.now()
		today_begin		= now.replace(hour=0, minute=0, second=0, microsecond=0)
		today_end		= now.replace(hour=23, minute=59, second=59, microsecond=999)
		next_4_months 	= today_end + timedelta(days=4*30)

		month_begin		= now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		month_end		= now.replace(day=monthrange(now.year, now.month)[1], hour=23, minute=59, second=59, microsecond=999)
		
		return {
			'items': [
				("{0}__gte={1}&{0}__lte={2}".format(column_name, today_begin.isoformat(), today_end.isoformat()),  	   'Today'),
				("{0}__gte={1}&{0}__lte={2}".format(column_name, month_begin.isoformat(), month_end.isoformat()), 	   'This month'),
				("{0}__gte={1}&{0}__lte={2}".format(column_name, today_begin.isoformat(), next_4_months.isoformat()),  'Next 4 months'), 
				("{0}__year={1}".format(column_name, now.year), 'This year')
			]
		}




	def deserialize(self, properties):
		self._label   = properties.get('label','')
		self._help    = properties.get('help','')
		self._visible = properties.get('visible',True)
		
		self.search_field_key   = properties.get('search_field_key', None)
		self.sort_by 			= properties.get('sort_by', [])
		self.filter_by 			= properties.get('filter_by',[])
		self._current_page	    = int(properties['pages']['current_page'])
		self._selected_row_id 	= properties.get('selected_row_id', -1)


	def serialize_filters(self, list_filter, queryset):
		filters_list = []

		model = apps.get_model(self._app, self._model)

		#configure the filters
		for column_name in list_filter:
			field 			= get_field(model, column_name)
			column_values 	= queryset.values_list(column_name, flat=True).distinct().order_by(column_name)

			print(column_name, column_values.query)
						
			field_type 		 = 'combo'
			field_properties = {
				'field_type': 'combo',
				'label': 	get_verbose_name(model, column_name),
				'column':	column_name
			}

			if isinstance(field, models.BooleanField):
				field_properties.update({
					'items': [ ("{0}=true".format(column_name), 'True'), ("{0}=false".format(column_name), 'False')]
				})
			if isinstance(field, (models.DateField, models.DateTimeField) ):
				field_properties.update(self.get_datetimefield_options(column_name))
			else:
				filter_values = [(column_name+'='+str(column_value), column_value) for column_value in column_values]
				field_properties.update({'items': filter_values})

			filters_list.append(field_properties)


		return filters_list