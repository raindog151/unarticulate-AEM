# unarticulate-AEM
Hastily written script to unpack content created by Articulate Rise and fix it to work with Adobe Experience Manager filename requirements

This script fixes a moment in time issue with Adobe Experience Manager (AEM) where courses generated in Articulate Rise auto-generate file names that are not compatable due to character constraints. This script expects a zip file containing all html and assets (images, etc) and outputs a new zip file unless the -n flag is passed. It worked on one course I was supplied, but I make no promises it will work for you. Happy to try to fix bugs if reported. 

This script has been tested on OSX and Linux, I don't have access to a Windows box to try.

If this helps you, feel free to donate to me via venmo/paypal: raindog151[at]gmail[dot]com

Usage:

```
$ ./unarticulate.py -h
usage: unarticulate [options] -f FILENAME.ZIP

This utility was built to replace filenames made in Articulate whatever the wife said to work nicely with Adobe Experience Manager.

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        Articulate zip file to convert (ex: website.zip) - This assumes the file is in the same directory you are running this from
  -n, --nozip           Don't automatically zip the unarticulated file when complete
  -d, --debug           Enable debugging (very verbose, YHBW)
```
