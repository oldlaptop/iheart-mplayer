#! /usr/bin/env python3

import parse_iheart_json
import driver_common
import subprocess

def launch_vlc (url, vlc_args):
	# Make sure we actually have vlc
	try:
		subprocess.check_call (['which', 'vlc'], shell=False)
	except subprocess.CalledProcessError:
		raise RuntimeError ('VLC could not be found.')

	# Now we run vlc.
	subprocess.call (['vlc', url] + vlc_args, shell=False)

if __name__ == '__main__':
	parser = driver_common.build_parser ('Play an iheartradio station in VLC')
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

		launch_vlc (station_url, [])
