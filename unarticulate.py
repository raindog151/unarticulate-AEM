#!/usr/bin/env python3

# imports

import argparse
import base64
import fileinput
import html
import json
import os
import pprint
import random
import re
import shutil
import sys
import traceback
import zipfile

# constants

FILE_CHAR_EXCLUDE = '|'.join(["\*", "/", ";", "\[", "\\\\", "\]", "\|", "%", "\{", "\}", "\?", "#", " "])
DIR_CHAR_EXCLUDE  = '|'.join(["\*", ";", "\[", "\]", "\|", "%", "\{", "\}", "\?", "#", " ", "_"])
TEXT_FILE_TYPES   = ["html", "htm", "js", "xml", "css", "json"]

TMPDIR1      = "./temp-" + str(random.randint(100000000,900000000)) + "/"
TMPDIR2      = "./temp-" + str(random.randint(900000001,999999999)) + "/"
NEW_ZIP_FILE = "content-" + str(random.randint(10000,99999))

# parse commandline args

parser = argparse.ArgumentParser(prog='unarticulate',
                                 usage='%(prog)s [options] -f FILENAME.ZIP',
                                 description="This utility was built to replace filenames made in Articulate whatever the wife said to work nicely with Adobe Experience Manager.")

parser.add_argument("-f", "--filename", type=str, required=True, help="Articulate zip file to convert (ex: website.zip) - This assumes the file is in the same directory you are running this from")
parser.add_argument("-n", "--nozip", action='store_true', help="Don't automatically zip the unarticulated file when complete", default=False)
parser.add_argument("-d", "--debug", action='store_true', help="Enable debugging (very verbose, YHBW)", default=False)

args = parser.parse_args()

# validate the file exists and is a valid zip file

print("[*] Validating the contents of archive %s..." % (args.filename))

try: 

    with zipfile.ZipFile(args.filename, 'r') as zip: 

        bad_file = zip.testzip()

        if bad_file != None:
            print("[!] The specified archive %s contained a file with errors: %s\n" % (args.filename, bad_file))
            print("[!] Aborting!\n")
            sys.exit(1)
        else:
            print("[*] No errors found in archive...")

            # unpack the zipfile to the local directory

            print("[*] Extracting archive to folder %s..." % (TMPDIR1)) 

            try:
                zip.extractall(path=TMPDIR1) 
            except Exception as ex:
                print("[!] The specified archive %s contained a file with errors: %s\n" % (args.filename, bad_file))
                print("[!] Aborting!\n")
                if args.debug: print(ex)
                if args.debug: traceback.print_exc()
                sys.exit(1)

except Exception as ex:
    print("[!] The specified archive %s could not be opened.  Please verify the file exists and try again.\n" % (args.filename))
    print("[!] Aborting!\n")
    if args.debug: print(ex)
    if args.debug: traceback.print_exc()
    sys.exit(1)


# get a k:v set of all of the files in the zip
# generate a new filename for each file or rename them if arg selected (MUST BE LOWERCASE!!)
# data format:
# orig_file_list[old_filename] = [new_file_name, new_file_pre, new_file_ext, old_file_name, old_file_pre, old_file_ext, is_changed]
# orig_dir_list[new_filename]  = relative_path

orig_file_list = {}
orig_dir_list  = {}

for filename in zip.namelist():

    # get the relative path from the zip data, parse out the file name
    split_path    = filename.split("/")
    relative_path = str.join("/", split_path[0:len(split_path) - 1]) + "/"
    old_file_name = split_path[-1]

    # clean up the filename to remove bad characters, set lowercase, remove extra periods
    clean_file_name = split_path[-1].lower()
    clean_file_name = re.sub(FILE_CHAR_EXCLUDE, '-', clean_file_name)
    clean_file_name = clean_file_name.replace(".", "-", clean_file_name.count(".") - 1)
    clean_file_pre  = clean_file_name.split(".")[0]
    clean_file_ext  = clean_file_name.split(".")[-1]
    is_changed      = 0

    if clean_file_name.strip(): 
        if clean_file_name != old_file_name:
            is_changed = 1

        old_file_split = re.match('(.*)\.([A-Za-z0-9]{2,4})$', old_file_name)
        old_file_pre   = old_file_split.group(1)
        old_file_ext   = old_file_split.group(2)

        orig_file_list[filename] = [clean_file_name, clean_file_pre, clean_file_ext, old_file_name, old_file_pre, old_file_ext, is_changed]
        orig_dir_list[filename]  = relative_path

# create new directory and create subfolders

try:
    print("[*] Creating new folder %s..." % (TMPDIR2))
    os.mkdir(TMPDIR2)
except Exception as ex:
    print("[!] ERROR: Could not create local directory! %s! Please ensure you have permissions to write to this directory!" % (TMPDIR2))
    print("[!] Aborting!")
    if args.debug: print(ex)
    if args.debug: traceback.print_exc()
    sys.exit(1)

try:
    for directory in orig_dir_list.values():
        new_dir = TMPDIR2 + directory
        os.makedirs(new_dir, exist_ok=True)
except Exception as ex:
    print("[!] ERROR: Could not create local directory! %s! Please ensure you have permissions to write to this directory!" % (new_dir))
    print("[!] Aborting!")
    if args.debug: print(ex)
    if args.debug: traceback.print_exc()
    sys.exit(1)

# copy files to new directory with new names

print("[*] Copying files to new folder %s..." % (TMPDIR2))

try:
    for filename, value in orig_file_list.items():
        (new_file_name, new_file_pre, new_file_ext, old_file_name, old_file_pre, old_file_ext, is_changed) = value
        if args.debug: print("[D] " + TMPDIR1 + filename + " ----> " + TMPDIR2 + orig_dir_list[filename] + new_file_name)
        shutil.copyfile(TMPDIR1 + filename, TMPDIR2 + orig_dir_list[filename] + new_file_name)

        # search for references to files within text based files and replace

        if new_file_ext in TEXT_FILE_TYPES:
            fileio = TMPDIR2 + orig_dir_list[filename] + new_file_name
            fileop = new_file_name

            if args.debug: print("[D] Found text file! --> " + fileio + " (" + fileop + ")")

            with open(fileio, 'r') as f:
                file_source = f.read()
                
                for filename, value in orig_file_list.items():
                    (new_file_name, new_file_pre, new_file_ext, old_file_name, old_file_pre, old_file_ext, is_changed) = value

                    if is_changed != 1 and fileop != "index.html":
                        pass

                    if args.debug: 
                        print("[D] Trying to change %s to %s..." % (old_file_pre, new_file_pre))
                    
                        guess = file_source.find(old_file_pre)
                        if guess != -1:
                            print("[D] old filename " + old_file_pre + " found at position " + str(guess) + " in file " + fileio)
                    
                    file_source = file_source.replace("/" + old_file_pre, new_file_pre)

                # if we're poking at the index.html file, we need to replace the base64 data

                if fileop == "index.html":
                    regex = r"\s+window\.courseData\s+=\s+\"(.*)\";\s+\n"
                    b64_split = re.search(regex, file_source)

                    if b64_split:
                        if args.debug: print("[D] We found a base64 blob starting with %s.." % (b64_split.group(1)[0:20]))
                        b64_blob_encoded = b64_split.group(1)
                        b64_blob_decoded = base64.b64decode(b64_blob_encoded).decode()
                        
                        b64_blob_decoded = b64_blob_decoded.replace("%2520", " ")
                        b64_blob_decoded = b64_blob_decoded.replace("%20", " ")

                        for filename, value in orig_file_list.items():
                            (new_file_name, new_file_pre, new_file_ext, old_file_name, old_file_pre, old_file_ext, is_changed) = value
                            
                            guess = b64_blob_decoded.find(old_file_pre)

                            if args.debug: 
                                if guess != -1:
                                    print("[D] base64 blob " + old_file_pre + " found at position " + str(guess) + " in file " + fileio + " containing " + new_file_pre)

                            if is_changed != 1:
                                pass
                                
                            b64_blob_decoded = b64_blob_decoded.replace(old_file_pre, new_file_pre)
                            
                        #print("That blob turned into %s.." % (b64_blob_decoded))

                        print("[*] Unpacking base64 strings in index.html...")
                        b64_new_blob_encoded = base64.b64encode(b64_blob_decoded.encode())

                        if b64_blob_encoded != b64_new_blob_encoded:
                            if args.debug: print("[D] It appears we changed the base64 encoded garbage, that's encouraging..")
                            
                            guess = file_source.find(b64_blob_encoded)
                            if args.debug: 
                                if guess > 0:
                                    print("[D] We looked for the old encoded base64 blob and found it on line: %s" % str(guess))
                                else:
                                    print("[D] We didn't find the encoded base64 blob when we tried to update it, things might not work right :((((((")
                            
                            file_source = file_source.replace(b64_blob_encoded, b64_new_blob_encoded.decode())

                    else:
                        print("[!] We didn't find a base64 blob in index.html, things might not work right :((((((")
                
            with open(fileio, 'w') as f:
                f.write(file_source)
            
except Exception as ex:
    print("[!] ERROR: Could not copy file %s to local directory %s! Please ensure you have permissions to write to this directory!" % (new_file_name, orig_dir_list[new_file_name]))
    print("[!] Aborting!")
    if args.debug: print(ex)
    if args.debug: traceback.print_exc()
    sys.exit(1)

# zip up and write file to disk

if args.nozip is False:
    print("[*] Creating new archive %s.zip..." % (NEW_ZIP_FILE))

    try:
        shutil.make_archive(NEW_ZIP_FILE, 'zip', root_dir=TMPDIR2, base_dir="content")
    except Exception as ex:
        print("[!] ERROR: Could not create new archive %s! Please ensure you have permissions to write to this directory!" % (NEW_ZIP_FILE))
        print("[!] Aborting!")
        #if args.debug: 
        print(ex)
        #if args.debug: 
        traceback.print_exc()
        sys.exit(1)

else:
    print("[*] --nozip option passed to script, not creating archive...")
    print("[*] Leaving directory %s in place..." % (TMPDIR2))

# remove old directory as well as new directory unless -n/--nozip is selected

try:
    shutil.rmtree(TMPDIR1)
except Exception as ex:
    print("[!] ERROR: Could not remove local directory! %s! Please ensure you have permissions to write to this directory!" % (TMPDIR1))
    print("[!] Aborting!")
    if args.debug: print(ex)
    if args.debug: traceback.print_exc()
    sys.exit(1)

if args.nozip is False:
    try:
        shutil.rmtree(TMPDIR2)
    except Exception as ex:
        print("[!] ERROR: Could not remove local directory! %s! Please ensure you have permissions to write to this directory!" % (TMPDIR1))
        print("[!] Aborting!")
        if args.debug: print(ex)
        if args.debug: traceback.print_exc()
        sys.exit(1)

print("[*] Looks like everything was successful...")
print("[*] Exiting...")

sys.exit(0)
