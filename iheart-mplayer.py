#! /usr/bin/env python3

import parse_iheart_json
import subprocess
import argparse

def launch_mplayer (url):
	# Make sure we actually have mplayer
	try:
		subprocess.check_call (['which', 'mplayer'], shell=False)
	except subprocess.CalledProcessError:
		raise RuntimeError ('MPlayer could not be found.')

	# Now we run mplayer. Pass it '-novideo', since we're playing radio
	# streams which are obviously audio-only - otherwise some versions of
	# mplayer will spend minutes looking for a nonexistent video stream.
	subprocess.call (['mplayer', url, '-novideo'], shell=False)

if __name__ == '__main__':
	parser = argparse.ArgumentParser (description='Play an iheartradio station in MPlayer')
	parser.add_argument (
		'stream_id',
		nargs=1,
		type=int,
		help='The (five-digit?) ID number of the station',
		)
	parser.add_argument (
		'-v', '--verbose',
		action='count',
		help='Display extra information',
		)

	args = parser.parse_args ()

	station = parse_iheart_json.station_info (args.stream_id[0])

	if (args.verbose):
		try:
			print ("station name:", station['name'])
			print ("description:", station['description'])
			print ("broadcast format:", station['format'])
		except KeyError:
			if  (args.verbose >= 2):
				print ("warning: a field is missing")
				print ("full dictionary dump:")
				print ("station")

	if (station['stream_urls']['rtmp']):
		station_url = station['stream_urls']['rtmp']
	elif (station['stream_urls']['http']):
		print ("warning: http stream being used")
		station_url = station['stream_urls']['http']
	else:
		print ("error: no stream for this station")
		if (args.verbose >= 2):
			print ("full dictionary dump:")
			print (station)

	launch_mplayer (station_url)
