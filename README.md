IHEART-URL(1) - General Commands Manual

# NAME

**iheart-url** - print the audio stream URL for an iheartradio station

# SYNOPSIS

**iheart-url**
\[**-chiv**]
\[**-l**&nbsp;*terms*]
\[**-s**&nbsp;*terms*]
\[station\_id]  
**iheart-mplayer**
\[**-l**&nbsp;*terms*]
\[station\_id]  
**iheart-mpv**
\[**-l**&nbsp;*terms*]
\[station\_id]  
**iheart-vlc**
\[**-l**&nbsp;*terms*]
\[station\_id]

# DESCRIPTION

**iheart-url**
fetches the URL for an iHeartRadio station's audio stream from iHeartRadio's
API servers and prints it to stdout. It is meant to be used with audio players
and the command substitution syntax in most shells, like so:

	$ mplayer -novideo "$(iheart-url [station_id])"

**iheart-mplayer**
is a trivial POSIX sh wrapper scripts that does precisely that for the
**mplayer**
media player, or for
**mpv**
or
**vlc**
if it is called by the corresponding names.

The options are as follows:

**-c**

> Disable TLS; all API requests will be done in cleartext, and only cleartext
> stream URLS will be returned. May prevent any valid stream URL from being
> returned, in the event that the station has only TLS streams.

**-h**

> Display a help message. Meaningless for wrapper scripts.

**-i**

> Instead of printing the URL for a station, output some human-readable info about
> it. Meaningless for wrapper scripts.

**-l** *terms*

> "I'm feeling lucky"
> search for terms; print the URL of the
> "best"
> result according to iHeartRadio's servers.

**-s** *terms*

> Run a search for terms, outputting vital information like station ID for each
> result. Meaningless for wrapper scripts.

**-v**

> Increase verbosity level, may be specified multiple times for more verbosity.
> Useful in conjunction with
> **-s.**
> Meaningless for wrapper scripts.

station\_id

> Print the URL for this numerical station ID. Station IDs can be obtained with
> **-i**
> or
> **-s.**

# ENVIRONMENT

`MPLAYER_OPTS`

`MPV_OPTS`

`VLC_OPTS`

> Command line arguments for wrapper scripts to pass their players.

# EXAMPLES

Print the URL for station ID 5361:

	$ iheart-url 5361

Print expanded search results for the term
"Sports:"

	$ iheart-url -vs Sports

Play the best match for the search term
"Classic rock"
in mpv
(note the use of double quotes to prevent the shell from field-splitting the search term:)

	$ iheart-mpv -l "Classic rock"

# CAVEATS

While most media players capable of handling network streams will be able to use
these URLs, the lack of public documentation concerning iHeartRadio's API
precludes any guarantees about the content provided. Also because of the lack of
documentation, much of this tool's functionality relies on information gained
from deep-packet inspection of official iHeartRadio apps' traffic and on trial
and error. The iHeartRadio API has been known to change on occasion and break
iheart-url's functionality. Technical documentation derived from this tool's
development may be found in its source code and in the 'iheart-url' file in the
source distribution.

# BUGS

**iheart-mplayer,**
**iheart-mpv,**
and
**iheart-vlc**
naively pass all their arguments to iheart-url, and all of iheart-url's stdio
output as an argument to the player. Players do not particularly like the output
of
**-h,**
**-i,**
or
**-s.**

Multiple people have reported intermittent outages of the iHeartRadio API,
during which it may return HTTP errors for iheart-url's requests for certain
stations.

Up-to-date information on any issues can be found on the Github issue tracker:
https://github.com/oldlaptop/iheart-mplayer/issues

OpenBSD 6.4 - November 28, 2018
