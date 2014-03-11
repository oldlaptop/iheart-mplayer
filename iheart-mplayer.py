#! /usr/bin/env python3

import parse_iheart_json
import argparse
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

def launch_vlc (url, vlc_args):
	# Make sure we actually have vlc
	try:
		subprocess.check_call (['which', 'vlc'], shell=False)
	except subprocess.CalledProcessError:
		raise RuntimeError ('VLC could not be found.')

	# Now we run vlc.
	subprocess.call (['vlc', url] + vlc_args, shell=False)

if __name__ == '__main__':
	parser = argparse.ArgumentParser (description="Play an iHeartRadio station in mplayer or VLC")
	parser.add_argument (
		'stream_id',
		nargs=1,
		type=int,
		help="The (five-digit?) ID number of the station",
		)
	parser.add_argument (
		'-p', '--player',
		default='mplayer',
		choices=['mplayer', 'vlc'],
		help="The player to use (currently either mplayer or vlc), the default is mplayer",
		)
	parser.add_argument (
		'-o', '--player_options',
		nargs='*',
		help="Command-line arguments to pass the media player (UNIMPLEMETED)",
		)
	parser.add_argument (
		'-t', '--stream_type',
		default='auto',
		help="The type of stream to use, currently either auto or one of shout, rtmp, stw, or pls. The default is auto.",
		)
	parser.add_argument (
		'-v', '--verbose',
		action='count',
		help="Display extra information",
		)

	args = parser.parse_args ()

	station = parse_iheart_json.station_info (args.stream_id[0])

	if (args.verbose):
		try:
			print ("station name:", station['name'])
			print ("description:", station['description'])
			print ("broadcast format:", station['format'])
		except KeyError:
			print ("warning: a field is missing")
			if (verbose >= 2):
				print ("full dictionary dump:")
				print (station)

	try:
		station_url = parse_iheart_json.get_station_url (station, args.stream_type)
	except KeyError:
		print ("error: requested stream does not exist for this station")
		if (args.verbose is not None and args.verbose >= 2):
			print ("full dictionary dump:")
			print (station)
		exit ()

	if (args.player == 'mplayer'):
		launch_mplayer (station_url, [])
	elif (args.player == 'vlc'):
		launch_vlc (station_url, [])
