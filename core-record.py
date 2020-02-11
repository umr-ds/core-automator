#!/usr/bin/env python2

# core-record - record core node positions
# Written by Lars Baumgaertner (c) 2017

import sys
import commands
import time
import getopt
import glob
import re
from coreposlib import *

def usage():
    print sys.argv[0] + ' [param] -f <pos_file>'
    print " -f <pos_file> recorded movements"
    print " -e empty file, create a new one"
    print " -c <core_session_number> control specific session (default: first session)"        

if __name__ == "__main__":
    playbackfile = ''
    clear = False
    session = ""    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hf:c:e",["file=","core-session="])
    except getopt.GetoptError:
      usage()
      sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt in ("-f", "--file"):
            playbackfile = arg
        elif opt == "-e":
            clear = True   
        elif opt in ("-c", "--core-session"):
            session = arg     
        else:
            usage()
            sys.exit(1)
    if playbackfile == '':
        usage()
        sys.exit(1)


    s_list = get_session()

    if len(s_list) != 1 and session == "":
        print "Error: Need excatly one running session!\n"
        sys.exit()

    if session == "":
        session = s_list[0]
    else:
        if not session in s_list:
            print "Error: Invalid session ", session
            sys.exit()

    node_map = get_nodes_by_id(session)

    record(playbackfile, node_map, session, clear)
