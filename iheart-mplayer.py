#! /usr/bin/env python3

import parse_iheart_json
import driver_common
import subprocess

def launch_mplayer (url, mplayer_args):
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
	parser = driver_common.build_parser ('Play an iheartradio station in MPlayer')
	args = parser.parse_args ()

	station = parse_iheart_json.station_info (args.stream_id[0])

	if (args.verbose):
		try:
			driver_common.print_station_info (station)
		except KeyError:
			print ("warning: a field is missing")
			if (verbose >= 2):
				print ("full dictionary dump:")
				print ("station")

	try:
		station_url = driver_common.get_station_url (station, args.stream_type)
	except KeyError:
		print ("error: requested stream does not exist for this station")
		if (args.verbose is not None and args.verbose >= 2):
			print ("full dictionary dump:")
			print (station)
		exit ()

	launch_mplayer (station_url, [])
