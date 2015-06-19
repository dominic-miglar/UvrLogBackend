#!/usr/bin/env python2
#-*- coding:utf-8 -*-

'''
This module contains all database models with their specific business logic.
'''

import logging
from django.db import models
from django.db.models.signals import post_save

__author__ = "Dominic Miglar"
__copyright__ = "Copyright 2015"
__license__ = "GPL"
__maintainer__ = "Dominic Miglar"
__email__ = "dominic.miglar@w1r3.net"

logger = logging.getLogger(__name__)

class Controller(models.Model):
    name = models.CharField('Name', max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)

    #def save(self, *args, **kwargs):
    #    if self.pk is None:
    #        pass
    #    super(Controller, self).save(*args, **kwargs)

    def get_io_identifiers(self):
        return IoIdentifier.objects.filter(controller=self)

    def __str__(self):
        return self.name


class IoIdentifier(models.Model):
    TYPE_DIGITAL = 'digital'
    TYPE_ANALOG = 'analog'
    TYPE_HEATMETER = 'energy'
    IO_TYPE_CHOICES = (
        (TYPE_DIGITAL, 'Digital'),
        (TYPE_ANALOG, 'Analog'),
        (TYPE_HEATMETER, 'HeatMeter'),
    )
    controller = models.ForeignKey('Controller')
    latest_value = models.ForeignKey('IoValue', null=True, blank=True)
    name = models.CharField('Name', max_length=10)
    type = models.CharField('Type', max_length=10, choices=IO_TYPE_CHOICES)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return '%s (%s)' % (self.name, self.controller.name)


class IoValue(models.Model):
    io_identifier = models.ForeignKey('IoIdentifier')
    datetime = models.DateTimeField()

    def __str__(self):
        return '%s (%s, %s)' % (
            self.datetime, self.io_identifier.name, self.io_identifier.controller.name)


class AnalogValue(IoValue):
    value = models.FloatField('Value')
    unit = models.CharField('Unit', max_length=10)

    def __str__(self):
        return '%s - %f %s (%s, %s)' % (
            self.datetime, self.value, self.unit, self.io_identifier.name,
            self.io_identifier.controller.name)


class DigitalValue(IoValue):
    value = models.FloatField('Value')
    unit = models.CharField('Unit', max_length=10)
    speed = models.FloatField('Speed', null=True)

    def __str__(self):
        if(self.speed is not None):
            return '%s - %f%s %f (%s, %s)' % (self.datetime, self.value, self.unit, self.speed,
            self.io_identifier.name, self.io_identifier.controller.name)
        else:
            return '%s - %f %s (%s, %s)' % (self.datetime, self.value, self.unit,
            self.io_identifier.name, self.io_identifier.controller.name)


class HeatMeterValue(IoValue):
    power = models.FloatField('Power')
    energy = models.FloatField('Energy')

    def __str__(self):
        return '%s - %f kW %f kWh (%s, %s)' % (self.datetime, self.power, self.energy, self.io_identifier.name, self.io_identifier.controller.name)


def initial_create_io_identifiers(sender, **kwargs):
        if not kwargs.get('created'):
            return
        controller = kwargs.get('instance')
        # Create 32 Analog I/O Identifiers
        logger.info('Creating 32 Analog I/O Identifiers for controller %s' % controller.name)
        for i in range(32):
            name = 'Analog%d' % (i+1)
            io_identifier = IoIdentifier.objects.create(controller=controller,
                name=name, type=IoIdentifier.TYPE_ANALOG)
            logger.info('Created I/O Identifier %s with type %s' % (
                io_identifier.name, IoIdentifier.TYPE_ANALOG))
        # Create 26 Ditigal I/O Identifiers
        logger.info('Creating 26 Digital I/O Identifiers for controller %s' % controller.name)
        for i in range(26):
            name = 'Digital%d' % (i+1)
            io_identifier = IoIdentifier.objects.create(controller=controller,
                name=name, type=IoIdentifier.TYPE_DIGITAL)
            logger.info('Created I/O Identifier %s with type %s' % (
                io_identifier.name, IoIdentifier.TYPE_DIGITAL))
        # Create 4 HeatMeter I/O Identifiers
        logger.info('Creating 26 HeatMeter (energy) I/O Identifiers for controller %s' % controller.name)
        for i in range(4):
            name = 'HeatMeter%d' % (i+1)
            io_identifier = IoIdentifier.objects.create(controller=controller,
                name=name, type=IoIdentifier.TYPE_HEATMETER)
            logger.info('Created I/O Identifier %s with type %s' % (
                io_identifier.name, IoIdentifier.TYPE_HEATMETER))

post_save.connect(initial_create_io_identifiers, sender=Controller)
