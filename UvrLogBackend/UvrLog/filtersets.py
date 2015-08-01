#!/usr/bin/env python2
#-*- coding:utf-8 -*-

"""
This module contains all FilterSets which are used from the ViewSets in the views module.
"""


import django_filters
from models import *

__author__ = "Dominic Miglar"
__copyright__ = "Copyright 2015"
__license__ = "GPL"
__maintainer__ = "Dominic Miglar"
__email__ = "dominic.miglar@w1r3.net"

class ControllerFilter(django_filters.FilterSet):
    class Meta:
        model = Controller
        fields = ['id', 'name', 'description', 'schema_active']


class IoIdentifierFilter(django_filters.FilterSet):
    class Meta:
        model = IoIdentifier
        fields = ['id', 'controller', 'latest_value', 'name', 'type', 'description', 'is_active',]


class IoValueFilter(django_filters.FilterSet):
    date_from = django_filters.filters.DateFilter(name='datetime', lookup_type='gte')
    date_to = django_filters.filters.DateFilter(name='datetime', lookup_type='lte')

    class Meta:
        model = IoValue
        fields = ['id', 'io_identifier', 'datetime', 'date_from', 'date_to',]


class AnalogValueFilter(django_filters.FilterSet):
    date_from = django_filters.filters.DateFilter(name='datetime', lookup_type='gte')
    date_to = django_filters.filters.DateFilter(name='datetime', lookup_type='lte')

    class Meta:
        model = AnalogValue
        fields = ['id', 'io_identifier', 'datetime', 'value', 'unit', 'date_from', 'date_to',]


class DigitalValueFilter(django_filters.FilterSet):
    date_from = django_filters.filters.DateFilter(name='datetime', lookup_type='gte')
    date_to = django_filters.filters.DateFilter(name='datetime', lookup_type='lte')

    class Meta:
        model = DigitalValue
        fields = ['id', 'io_identifier', 'datetime', 'value', 'unit', 'speed', 'date_from', 'date_to',]


class HeatMeterValueFilter(django_filters.FilterSet):
    date_from = django_filters.filters.DateFilter(name='datetime', lookup_type='gte')
    date_to = django_filters.filters.DateFilter(name='datetime', lookup_type='lte')

    class Meta:
        model = HeatMeterValue
        fields = ['id', 'io_identifier', 'datetime', 'power', 'energy', 'date_from', 'date_to',]


class UploadedSchemaFilter(django_filters.FilterSet):
    class Meta:
        model = UploadedSchema
        fields = ['id', 'related_controller', 'uploaded_file', 'timestamp',]

