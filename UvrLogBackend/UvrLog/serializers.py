#!/usr/bin/env python2
#-*- coding:utf-8 -*-

'''
This module contains all the Serializers which are used from the ViewSets in the views module.
'''

from rest_framework import serializers
from models import *

__author__ = "Dominic Miglar"
__copyright__ = "Copyright 2015"
__license__ = "GPL"
__maintainer__ = "Dominic Miglar"
__email__ = "dominic.miglar@w1r3.net"

class ControllerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Controller
        fields = ['id', 'name', 'description',]
        #read_only_fields = ['id',]

class IoIdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = IoIdentifier
        fields = ['id', 'controller', 'latest_value', 'name', 'type', 'description',]
        #read_only_fields = ['id',]

class IoValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = IoValue
        fields = ['id', 'io_identifier', 'datetime',]
        #read_only_fields = ['id',]

class AnalogValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalogValue
        fields = ['id', 'io_identifier', 'datetime', 'value', 'unit',]
        #read_only_fields = ['id',]

class DigitalValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalValue
        fields = ['id', 'io_identifier', 'datetime', 'value', 'unit', 'speed',]
        #read_only_fields = ['id',]

class HeatMeterValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeatMeterValue
        fields = ['id', 'io_identifier', 'datetime', 'power', 'energy',]
        #read_only_fields = ['id',]

