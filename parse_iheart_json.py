#! /usr/bin/env python3

import urllib.request
import urllib.parse
import json

class autodetectError (ValueError):
	pass

def station_search (search_keywords):
	''' Returns a dict containing iHeartRadio search results for search_keyword
	
	search_keyword is a string (radio call letters, for instance -
	URL-illegal characters will be escaped) which will be submitted to
	iHeartRadio, matching against stations in their database. This function
	will return a (potentially very large) dict containing detailed search
	results, including station ID numbers, names, short descriptions,
	locations, radio band/frequency, call letters, URLs to logo images, the
	search algorithm's "score", and potentially other data. In addition
	there seems to be some summary information, such as the number of search
	results and other metadata. For now detailed documentation of this dict
	is not available, manual inspection of results will be highly
	illuminating.
	'''

	# This information is derived from deep packet inspection of the
	# official iHeartRadio Android app's HTTP traffic. Exhaustive analysis
	# has not been done as of this writing.
	#
	# iheartradio has a simple API for running searches against its station
	# database. The response to a GET request to a URL of the form:
	#
	# http://api.iheart.com/api/v1/catalog/searchAll?&keywords=<keywords>
	#
	# where <keywords> is a search term, will be UTF-8 encoded JSON giving
	# detailed search results; containing both search metadata and detailed
	# information on all search results. Importantly, ID numbers for search
	# results are included.
	#
	# There are a great many additional parameters that the official app
	# includes. A full API request URL from the official app follows:
	#
	# http://api2.iheart.com/api/v1/catalog/searchAll?&keywords=wjr&bestMatch=True&queryStation=True&queryArtist=True&queryTrack=True&queryTalkShow=True&startIndex=0&maxRows=12&queryFeaturedStation=False&queryBundle=False&queryTalkTheme=False&amp_version=4.11.0
	#
	# Analysis of these parameters will be conducted some other time (TM),
	# however it appears only &keywords is necessary; it is the only one
	# this program uses.

	# Base URL for our API request
	iheart_base_url = 'http://api.iheart.com/api/v1/catalog/searchAll?'

	paramaters = urllib.parse.urlencode ({ 'keywords':search_keywords })

	response = urllib.request.urlopen (iheart_base_url + paramaters)

	# We assume we're dealing with UTF-8 encoded JSON, if we aren't the API
	# has probably changed in ways we can't deal with.
	assert (response.getheader ('Content-Type') == 'application/json;charset=UTF-8')

	results = json.loads (response.read ().decode ("utf-8"))

	if (results['errors']):
		raise RuntimeError (results['errors'])
	else:
		return results

def station_info (station_id):
	''' Returns a dict containing all available information about station_id

	station_id is a five-digit number assigned to an iHeartRadio station.
	No publicly documented method of obtaining a list of valid station_ids
	is currently available, however see the function station_search in this
	file.
	'''

	# The iheartradio API is not publicly documented, to my knowledge. At 
	# the time of writing, one can submit a POST request with a content of
	# '1' to a URL of the following form (where STATION_ID_NUMBER is a five-
	# digit number):
	#
	# http://iheart.com/a/live/station/STATION_ID_NUMBER/stream/
	#
	# The response will be UTF-8 encoded JSON describing some vital
	# information about the station (if it exists), such as name, market,
	# genre, and links to various live streams of its content (often RTMP or
	# HTTP, but usually (never?) both). Valid station ID numbers can
	# currently be obtained by searching for stations on the
	# http://www.iheart.com website - for example, in the following URL, the
	# station ID number is 1165:
	#
	# http://www.iheart.com/live/WOOD-Radio-1069-FM-1300AM-1165/
	#
	# See also the docstring and block comment for station_search().

	# The base URL for our API request (%s is for string substitution)
	iheart_base_url = 'http://www.iheart.com/a/live/station/%i/stream/'

	response = urllib.request.urlopen (iheart_base_url % station_id, '1'.encode('utf-8'))

	# We assume we're dealing with UTF-8 encoded JSON, if we aren't the API
	# has probably changed in ways we can't deal with.
	assert (response.getheader('Content-Type') == 'application/json; charset=utf-8')

	station = json.loads (response.read().decode('utf-8'))

	if (not station['ok']):
		raise RuntimeError(station['error'])
	else:
		return station

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
	# rtmp_stream: Yet another rtmp URL; in the one instance I've seen so
	#              far, it's identical to the one in stream_urls.
	#
	# hls_stream: A URL for Apple's HTTP Live Streaming protocol, understood
	#             by recent mplayer and VLC.
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
	# Stations tend to have either both shoutcast_stream and one of the
	# RTMP streams, OR both stw_stream and pls_stream. There may be others I
	# have not encountered - dictionary dumps (use -vvv) of stations with
	# other stream types would be greatly appreciated.
	
	# For our purposes, the preference order is:
	# shoutcast_stream
	# hls_stream
	# pls_stream
	# secure_rtmp_stream
	# rtmp_stream
	# stw_stream
	#
	# stw_stream will print a warning, since it is not known to work in any
	# player.
	preference_order = ['shoutcast_stream',
	                    'hls_stream',
	                    'pls_stream',
	                    'secure_rtmp_stream',
	                    'rtmp_stream',
	                    'stw_stream']

	stream_dict = station['streams']
	choice = None

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

	if (choice is not None):
		return choice
	else:
		# nothing in preference_order exists in the dict, we cannot cope
		raise autodetectError ("No known stream exists")

def get_station_url (station, stream_type):
	'''Takes a station dictionary and a stream type, and returns a URL.
	Caller should be prepared for possible KeyErrors, since iheartradio
	completely omits non-existent streams instead of setting their values
	to null/None. If the stream type is 'auto', a stream will be detected
	automatically using detect_stream().
	'''

	station_url = None

	# If a stream does not exist, iheart seems to just omit its entry from
	# the 'streams' category in JSON. Therefore we will bail out with a
	# KeyError if the requested stream does not exist.
	if (stream_type == 'auto'):
		station_url = detect_stream (station)
	elif (stream_type == 'secure_rtmp'):
		if (station['streams']['secure_rtmp_stream']):
			station_url = station['streams']['secure_rtmp_stream']

	elif (stream_type == 'rtmp'):
		if (station['streams']['rtmp_stream']):
			station_url = station['streams']['rtmp_stream']

	elif (stream_type == 'shout'):
		if (station['streams']['shoutcast_stream']):
			station_url = station['streams']['shoutcast_stream']

	elif (stream_type == 'hls'):
		if (station['streams']['hls_stream']):
			station_url = station['streams']['hls_stream']

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
