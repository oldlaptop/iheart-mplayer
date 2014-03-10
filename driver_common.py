#! /usr/bin/env python3

import subprocess
import argparse

def build_parser (driver_desc):
	parser = argparse.ArgumentParser (description=driver_desc)
	parser.add_argument (
		'stream_id',
		nargs=1,
		type=int,
		help='The (five-digit?) ID number of the station',
		)
	parser.add_argument (
		'-t', '--stream_type',
		default='shout',
		help='The type of stream to prefer, currently either shout, rtmp, stw, or pls. The default is shout.',
		)
	parser.add_argument (
		'-v', '--verbose',
		action='count',
		help='Display extra information',
		)

	return parser

def print_station_info (station):
	print ("station name:", station['name'])
	print ("description:", station['description'])
	print ("broadcast format:", station['format'])

def get_station_url (station, stream_type):
	station_url = None

	# If a stream does not exist, iheart seems to just omit its entry from
	# the 'streams' category in JSON. Therefore we will bail out with a
	# KeyError if the requested stream does not exist.
	if (stream_type == 'rtmp'):
		if (station['streams']['secure_rtmp_stream']):
			station_url = station['streams']['secure_rtmp_stream']
	elif (stream_type == 'shout'):
		if (station['streams']['shoutcast_stream']):
			station_url = station['streams']['shoutcast_stream']
	elif (stream_type == 'stw'):
		if (station['streams']['stw_stream']):
			station_url = station['streams']['stw_stream']
	elif (stream_type == 'pls'):
		if (station['streams']['pls_stream']):
			station_url = station['streams']['pls_stream']

	# Apparently we don't usually get here, see above.
	if (not station_url):
		raise RuntimeError ("Requested stream does not exist")

	return station_url
