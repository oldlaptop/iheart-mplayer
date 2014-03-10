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
		help='The type of stream to prefer, currently either auto or one of shout, rtmp, stw, or pls. The default is auto.',
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

def detect_stream (station):
	'''Takes a station dictionary and determines the best stream URL to use,
	returns its URL.
	'''

	# There are two keys within the station dictionary which contain dicts
	# of stream URLs. The first is 'stream_urls', which seems to always have
	# at least two members - 'rtmp' (which is an RTMP URL which VLC and some
	# mplayer versions don't seem to understand) and 'http' (which is an
	# HTTP URL which neither mplayer or vlc seem to understand in any case I
	# have tested). Quite often, at least one of these will be None (but
	# both are always present for a valid station). For our purposes we will
	# ignore this member. The second is 'streams', which *only* contains
	# members for those streams which actually exist (there will never be a
	# None in this dict). Keys which have been observed:
	#
	# shoutcast_stream: Seems to always be a standard shoutcast stream URL.
	#                   Widely understood and works in both VLC and mplayer,
	#                   as far as I've tested.
	#
	# secure_rtmp_stream: An RTMP URL, not always the same as the RTMP URL
	#                     in stream_urls. In cases I've seen it's more
	#                     likely to work than the RTMP URL in stream_urls,
	#                     but some mplayers still don't like it (VLC seems
	#                     fine).
	#
	# stw_stream: Some kind of special HTTP-based stream, which neither
	#             mplayer or VLC understand. Seems related to the (former?)
	#             StreamTheWorld Flash-based platform, always(?) seems to
	#             occur together with pls_stream.
	#
	# pls_stream: Contains a link to a PLS file (INI-based playlist). Occurs
	#             alongside stw_stream. Seems to contain a large number of
	#             HTTP links, none of which are the same as stw_stream.
	#             Seems to work in VLC, but not any mplayer I have tested.
	#
	# Stations tend to have either both of the first two, OR both of the
	# second two. There may be others I have not encountered - dictionary
	# dumps (use -vv) of stations with other stream types would be greatly
	# appreciated.


	# For our purposes, the preference order is:
	# shoutcast_stream
	# pls_stream
	# secure_rtmp_stream
	# stw_stream
	#
	# stw_stream will print a warning, since it is not known to work in any
	# player.
	preference_order = ['shoutcast_stream',
	                    'pls_stream',
	                    'secure_rtmp_stream',
	                    'stw_stream']
	stream_dict = station['streams']


	for candidate in preference_order:
		try:
			choice = stream_dict[candidate]
			print ("stream type auto: using " + candidate)
			break
		except KeyError:
			pass
	else:
		# we have an stw_stream - almost certain to not work
		print ("warning: using stw_stream, this stream type is not known to work anywhere")
	return choice

def get_station_url (station, stream_type):
	'''Takes a station dictionary and a stream type, and returns a URL
	Caller should be prepared for possible KeyErrors, since iheartradio
	completely omits non-existent streams instead of setting their values
	to null/None.
	'''

	station_url = None

	# If a stream does not exist, iheart seems to just omit its entry from
	# the 'streams' category in JSON. Therefore we will bail out with a
	# KeyError if the requested stream does not exist.
	if (stream_type == 'auto'):
		station_url = detect_stream (station)
	elif (stream_type == 'rtmp'):
		if (station['streams']['secure_rtmp_stream']):
			station_url = station['streams']['secure_rtmp_stream']
	elif (stream_type == 'shout'):
		if (station['streams']['shoutcast_stream']):
			station_url = station['streams']['shoutcast_stream']
	elif (stream_type == 'stw'):
		if (station['streams']['stw_stream']):
			print ("warning: using stw_stream, this stream type is not known to work anywhere")
			station_url = station['streams']['stw_stream']
	elif (stream_type == 'pls'):
		if (station['streams']['pls_stream']):
			station_url = station['streams']['pls_stream']

	# Apparently we don't usually get here, see above.
	if (not station_url):
		raise RuntimeError ("Requested stream does not exist")

	return station_url
