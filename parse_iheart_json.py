#! /usr/bin/env python3

import urllib.request
import urllib.parse
import json

class autodetectError (ValueError):
	pass

def station_search (search_keywords, tls = True):
	'''Returns a dict containing iHeartRadio search results for search_keyword
	
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
	iheart_base_url = '%s://api.iheart.com/api/v1/catalog/searchAll?'

	paramaters = urllib.parse.urlencode ({ 'keywords':search_keywords })

	response = urllib.request.urlopen ((iheart_base_url % ("https" if tls else "http")) + paramaters)

	# We assume we're dealing with UTF-8 encoded JSON, if we aren't the API
	# has probably changed in ways we can't deal with.
	assert (response.getheader ('Content-Type') == 'application/json;charset=UTF-8')

	results = json.loads (response.read ().decode ("utf-8"))

	if (results['errors']):
		raise RuntimeError (results['errors'])
	else:
		return results

def station_info (station_id, tls = True):
	''' Returns a dict containing all available information about station_id

	station_id is a five-digit number assigned to an iHeartRadio station.
	No publicly documented method of obtaining a list of valid station_ids
	is currently available, however see the function station_search in this
	file.
	'''

	# The iheartradio API is not publicly documented, to my knowledge.
	# There have been several historical versions of this function using
	# obsolete APIs, their descriptions may be found in the 'iheart-api'
	# document in the source distribution.
	#
	# AGAIN, in early 2017 the iheart API broke; the new URL comes from
	# Nathan Rajlich's node.js library
	# (https://github.com/TooTallNate/iheart). Deep-packet analysis of
	# official iHeartRadio apps remains to be done.

	# The base URL for our API request (%s is for string substitution)
	iheart_base_url = "%s://api.iheart.com/api/v2/content/liveStations/%s"

	response = urllib.request.urlopen (iheart_base_url % (("https" if tls else "http"), station_id))

	# We assume we're dealing with UTF-8 encoded JSON, if we aren't the API
	# has probably changed in ways we can't deal with.
	(response.getheader ('Content-Type') == 'application/json;charset=UTF-8')

	# TODO: investigate this new "hits" structure, perhaps searching and
	#       stream-fetching can be unified
	station = json.loads (response.read ().decode('utf-8'))['hits'][0]

	if (not station['streams']):
		raise RuntimeError("station streams list empty")
	else:
		return station

def depls (pls_url):
	'''PLS to HTTP audio stream
	
	Assuming pls_url is the location of a PLS stream, rip out File1 and
	return the contents. This is meant to be used to cut through the PLS
	junk returned by some iheartradio stations as a "stream" URL. As a
	warning, if this function gets confused it may well just pass the
	original URL back.
	'''

	response = urllib.request.urlopen (pls_url)

	# Failure of this assert is marginally more likely than it is for the
	# iheart API functions, and may simply indicate that there is variation
	# between different servers serving PLS playlists for iheartradio;
	# I'd like to know the station id for any station which causes this to
	# be tripped.
	assert (response.getheader ('Content-Type') == 'audio/x-scpls; charset=UTF-8')

	playlist_file = response.read ().decode('utf-8').splitlines ()
	# We simply pull out the first entry (File1) with brute force.
	for candidate in playlist_file:
		if ("File1" in candidate):
			# The format of these lines will be FileN=<url> or so
			return candidate[len ("File1="):]
	else:
		# We fell through, something went wrong in the oh-so-robust
		# "parsing" logic above. It won't hurt things too bad to just
		# toss the original URL back to the caller.
		return pls_url


def get_station_url (station, tls = True):
	'''Takes a station dictionary and returns a URL.
	'''

	def streamcmp (x, y):
		'''By analogy with C strcmp(), this returns >0 if x is more
		preferred than y, >0 if it is less preferred, or 0 if x and y
		are equal.
		'''
		# We prefer shoutcast over pls over rtmp (and we prefer no
		# stream at all over stw_stream), and unless otherwise specified
		# we prefer tls ("secure_") variants. Note that we will also
		# never pick an https stream if told not to, even if that means
		# picking no valid stream.
		order = { 'secure_shoutcast_stream': (3.1 if tls else -1),
		          'shoutcast_stream': 3,
		          'secure_pls_stream': (2.1 if tls else -1),
	                  'pls_stream': 2,
	                  'secure_hls_stream': (2.1 if tls else -1),
	                  'hls_stream': 2,
	                  'secure_rtmp_stream': (1.1 if tls else -1),
	                  'rtmp_stream': 1,
	                  None: 0,
	                  # appears to be a normal HLS stream fed through an
	                  # (HTTPS) redirector hosted by iHeart; since it seems
	                  # to occur alongside non-redirected HLS streams,
	                  # prefer those.
	                  'pivot_hls_stream': (0.2 if tls else -1),
	                  # one station observed with this stream type (github
	                  # issue #6), but no URL for it
	                  'flv_stream': 0.1,
	                  'stw_stream': -1 }
		
		if order[x] > order[y]:
			return 1
		elif order[x] == order[y]: # should never happen
			return 0
		elif order[x] < order[y]:
			return -1
	
	preferred_stream = None
	for stream in station['streams'].keys ():
		                                            # stations with blank URLs have been observed
		if (streamcmp (stream, preferred_stream) > 0) and len(station['streams'][stream]) > 0:
			preferred_stream = stream

	return (station['streams'][preferred_stream])
