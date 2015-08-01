#!/usr/bin/env python2
#-*- coding:utf-8 -*-

"""
This module contains all ViewSets which control the request / response cycle.
"""

import logging
import os
import magic
from datetime import datetime
from django.db import IntegrityError, transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import FileUploadParser
import models, serializers, filtersets

__author__ = "Dominic Miglar"
__copyright__ = "Copyright 2015"
__license__ = "GPL"
__maintainer__ = "Dominic Miglar"
__email__ = "dominic.miglar@w1r3.net"

logger = logging.getLogger(__name__)

def datestring_to_datetime(datestring):
    return datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S')

def get_mime_type(file):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(file.read())
    return mime_type


class ControllerViewSet(viewsets.ModelViewSet):
    queryset = models.Controller.objects.all()
    serializer_class = serializers.ControllerSerializer
    filter_class = filtersets.ControllerFilter

    ''' Reads an JSON-Formatted string which contains many datasets and saves that into
        the database.
    '''
    @detail_route(methods=['post',], renderer_classes = [JSONRenderer,])
    def import_data(self, request, pk=None):
        #logger.info('DEBUG:')
        #logger.info(request.data)

        # get actual time, later used for calculating the whole import process time
        date_start = datetime.now()

        controller = models.Controller.objects.get(pk=pk)
        io_identifiers = controller.get_io_identifiers()

        # Make dictionary with I/O Identifiers to provide fast access for later
        io_identifier_dict = {}
        for io_identifier in io_identifiers:
            io_identifier_dict[io_identifier.name] = io_identifier

        # sort datasetlist, from past to present
        datasetlist_sorted = sorted(request.data, key=lambda dataset: datestring_to_datetime(dataset['date']))

        # Write values in dataset into the database. Do all database operation in an transaction.
        # When one value cannot be saved, all others will be reverted too to avoid an inconsistent
        # dataset.
        try:
            with transaction.atomic():
                for dataset in datasetlist_sorted:
                    date = datestring_to_datetime(dataset['date'])
                    for analogvalueset in dataset['analog']:
                        analogvalue, created = models.AnalogValue.objects.get_or_create(
                            io_identifier=io_identifier_dict[analogvalueset['name']],
                            datetime=date,
                            unit=analogvalueset['unit'],
                            value=analogvalueset['value']
                        )
                        # Update latest_value field in I/O Identifier to the latest received I/O Value object
                        # if that value was created newly and did not exist in the past.
                        if dataset is datasetlist_sorted[-1] and created == True:
                            io_identifier = io_identifier_dict[analogvalueset['name']]
                            io_identifier.latest_value = analogvalue
                            io_identifier.save(update_fields=['latest_value',])
                            #logger.info('Updated latest_value field on I/O Identifier %s to %s' % (
                            #    io_identifier_dict[analogvalueset['name']].__str__(), analogvalue.__str__()))
                        #logger.info('Created new AnalogValue object: %s' % analogvalue.__str__())
                    for digitalvalueset in dataset['digital']:
                        digitalvalue, created = models.DigitalValue.objects.get_or_create(
                            io_identifier=io_identifier_dict[digitalvalueset['name']],
                            datetime=date,
                            unit=digitalvalueset['unit'],
                            value=digitalvalueset['value'],
                            speed=digitalvalueset.get('speed', None)
                        )
                        # Update latest_value field in I/O Identifier to the latest received I/O Value object
                        # if that value was created newly and did not exist in the past.
                        if dataset is datasetlist_sorted[-1] and created == True:
                            io_identifier = io_identifier_dict[digitalvalueset['name']]
                            io_identifier.latest_value = digitalvalue
                            io_identifier.save(update_fields=['latest_value',])
                            #logger.info('Updated latest_value field on I/O Identifier %s to %s' % (
                            #    io_identifier_dict[digitalvalueset['name']].__str__(), digitalvalue.__str__()))
                        # logger.info('Created new DigitalValue object: %s' % digitalvalue.__str__())
                    for heatmetervalueset in dataset['energy']:
                        heatmetervalue, created = models.HeatMeterValue.objects.get_or_create(
                            io_identifier=io_identifier_dict[heatmetervalueset['name']],
                            datetime=date,
                            power=heatmetervalueset['power'],
                            energy=heatmetervalueset['energy']
                        )
                        # Update latest_value field in I/O Identifier to the latest received I/O Value object
                        # if that value was created newly and did not exist in the past.
                        if dataset is datasetlist_sorted[-1] and created == True:
                            io_identifier = io_identifier_dict[heatmetervalueset['name']]
                            io_identifier.latest_value = heatmetervalue
                            io_identifier.save(update_fields=['latest_value',])
                            #logger.info('Updated latest_value field on I/O Identifier %s to %s' % (
                            #    io_identifier_dict[heatmetervalueset['name']].__str__(), heatmetervalue.__str__()))
                        # logger.info('Created new HeatMeterValue object: %s' % heatmetervalue.__str__())
        except IntegrityError:
            error_msg = u'Error while processing dataset! Rolled back changes in database!'
            logger.error(error_msg)

        # get actual time, used for calculating the time the whole import process took
        date_stop = datetime.now()
        # import process duration, in seconds
        import_process_duration = (date_stop-date_start).total_seconds()

        ok_msg = u'The datasets were successfully processed in %d seconds.' % import_process_duration
        logger.info(ok_msg)
        return Response(ok_msg, status=status.HTTP_200_OK)


class IoIdentifierViewSet(viewsets.ModelViewSet):
    queryset = models.IoIdentifier.objects.all()
    serializer_class = serializers.IoIdentifierSerializer
    filter_class = filtersets.IoIdentifierFilter


class IoValueViewSet(viewsets.ModelViewSet):
    queryset = models.IoValue.objects.all()
    serializer_class = serializers.IoValueSerializer
    filter_class = filtersets.IoValueFilter


class AnalogValueViewSet(viewsets.ModelViewSet):
    queryset = models.AnalogValue.objects.all()
    serializer_class = serializers.AnalogValueSerializer
    filter_class = filtersets.AnalogValueFilter


class DigitalValueViewSet(viewsets.ModelViewSet):
    queryset = models.DigitalValue.objects.all()
    serializer_class = serializers.DigitalValueSerializer
    filter_class = filtersets.DigitalValueFilter


class HeatMeterValueViewSet(viewsets.ModelViewSet):
    queryset = models.HeatMeterValue.objects.all()
    serializer_class = serializers.HeatMeterValueSerializer
    filter_class = filtersets.HeatMeterValueFilter


class UploadedSchemaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.UploadedSchema.objects.all()
    serializer_class = serializers.UploadedSchemaSerializer
    filter_class = filtersets.UploadedSchemaFilter

    @detail_route(methods=['post',], parser_classes=[FileUploadParser,],)
    def upload(self, request, pk=None):
        controller_id = request.data['controller'] or None

        if 'file' in request.data:
            uploaded_file = request.data['file']
        else:
            uploaded_file = None

        if uploaded_file is None:
            response = {
                'message': 'You have to provide a attribute named file which contains the schema file to upload.'
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)

        if controller_id is None:
            response = {
                'message': 'You have to provide a attribute named controller which specifies the controller id.'
            }
            return Response(response, status.HTTP_400_BAD_REQUEST)

        try:
            controller = models.Controller.objects.get(pk=controller_id)
        except ObjectDoesNotExist as e:
            response = {
                'message': 'The controller with the ID %s was not found!' % controller_id
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file_name, uploaded_file_extension = os.path.splitext(uploaded_file.name)
        if uploaded_file_extension.lower() != '.svg':
            response = {
                'message': 'The file you are trying to upload must have the .svg extension!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        mime_type = get_mime_type(uploaded_file)
        if(mime_type != 'image/svg+xml'):
            response = {
                'message': 'The file you are trying to upload is not a SVG file!'
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        uploaded_schema = models.UploadedSchema(uploaded_file=uploaded_file, related_controller=controller)
        uploaded_schema.save()
        uploaded_schema_serializer = serializers.UploadedSchemaSerializer(uploaded_schema, context={'request': request})

        return Response(
            uploaded_schema_serializer.data,
            status=status.HTTP_201_CREATED
        )

