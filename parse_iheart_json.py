#! /usr/bin/env python3

import urllib.request
import urllib.parse
import json

# The iheartradio API is not publicly documented, to my knowledge. At the time
# of writing, one can submit a POST request with a content of '1' to a URL of
# the following form (where STATION_ID_NUMBER is a five-digit number):
#
# http://iheart.com/a/live/station/STATION_ID_NUMBER/stream/
#
# The response will be UTF-8 encoded JSON describing some vital information
# about the station (if it exists), such as name, market, genre, and links to
# various live streams of its content (often RTMP or HTTP, but usually (never?)
# both). Valid station ID numbers can currently be obtained by searching for
# stations on the http://iheart.com website - for example, in the following
# URL, the station ID number is 1165:
#
# http://www.iheart.com/live/WOOD-Radio-1069-FM-1300AM-1165/

# The base URL for our API request
iheart_base_url = 'http://www.iheart.com/a/live/station/'

# The postfix for our API request URL (comes after the ID number)
iheart_url_postfix = 'stream/'


def station_info (station_id):
	''' Returns a dict containing all available information about station_id

	station_id is a five-digit number assigned to an iHeartRadio station.
	No publicly documented method of obtaining a list of valid station_ids
	is currently available.
	'''

	# We can't do this in one function call, since urljoin can't deal with
	# more than two URL components.
	iheart_url = urllib.parse.urljoin (iheart_base_url, (str(station_id) + '/'))
	iheart_url = urllib.parse.urljoin (iheart_url, iheart_url_postfix)

	response = urllib.request.urlopen (iheart_url, '1'.encode('utf-8'))

	# We assume we're dealing with UTF-8 encoded JSON, if we aren't the API
	# has probably changed in ways we can't deal with.
	assert (response.getheader('Content-Type') == 'application/json; charset=utf-8')

	station = json.loads (response.read().decode('utf-8'))

	if (not station['ok']):
		raise RuntimeError(station['error'])
	else:
		return station
