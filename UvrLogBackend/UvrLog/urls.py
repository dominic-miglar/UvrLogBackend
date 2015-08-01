#!/usr/bin/env python2
#-*- coding:utf-8 -*-

from django.conf.urls import patterns, include, url
from rest_framework.routers import DefaultRouter
import views

__author__ = "Dominic Miglar"
__copyright__ = "Copyright 2015"
__license__ = "GPL"
__maintainer__ = "Dominic Miglar"
__email__ = "dominic.miglar@w1r3.net"

# Rest framework's routes
router = DefaultRouter(trailing_slash=True)
router.register(r'controllers', views.ControllerViewSet)
router.register(r'ioidentifiers', views.IoIdentifierViewSet)
router.register(r'iovalues', views.IoValueViewSet)
router.register(r'analogvalues', views.AnalogValueViewSet)
router.register(r'digitalvalues', views.DigitalValueViewSet)
router.register(r'heatmetervalues', views.HeatMeterValueViewSet)
router.register(r'uploadedschemas', views.UploadedSchemaViewSet)

urlpatterns = patterns('',
    url(r'', include(router.urls)),
)
