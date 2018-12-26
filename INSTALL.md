I dislike language-specific package managers such as pip, and for this reason
avoided making this a "real" python package for a long time. I still have no
intention of making this a good pip citizen of any kind, but the minimum
setup.py necessary to install the scripts system-wide or under $HOME (I only
test under $HOME) is present. Users on Unixish systems can install under $HOME
as follows:

 * Edit the iheart-mplayer wrapper script to change the line

```
IHEART_URL=${IHEART_URL:-"./iheart-url"}
``` so it points to the final location you'll be installing the executable
   scripts in. For $HOME/bin, you'll want:
```
IHEART_URL=${IHEART_URL:-"$HOME/bin/iheart-url"}
```
   It should work to omit the absolute path, but I wouldn't recommend it;
   surprising results could occur if you have `.` in your $PATH and run the
   script while in the source directory, for example. You could accomplish this
   in an automated fashion with something like:
```
printf '/IHEART_URL/s/.\/iheart-url/$HOME\/bin\/iheart-url/\nw\nq' | ed iheart-mplayer
```
   (Yes, I know sed -i would look cleaner, but sed -i is not standard and both
   printf and ed are. Think of the poor starving children using solaris, or
   something!)
 * Run `./setup.py install --home $HOME`; this copies the necessary files
   into appropriate locations, executable scripts to $HOME/bin and the
   parse_iheart_json module file to $HOME/lib/python (exact directory might vary
   according to your python version, or configuration, or something else.)
 * You now probably need to change $PYTHONPATH so it includes $HOME/lib/python
   (or whatever directory setup.py placed the module in, watch its output). On
   my systems, I put something like the following in ~/.profile:
```
PYTHONPATH="$HOME/lib/python:$PYTHONPATH"
export PYTHONPATH
```

Of course you can still run the scripts from the source directory if you prefer.
