#!/usr/bin/python

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
    print sys.argv[0] + ' [param] -f <inputfile>'
    print " -f <inputfile> recorded movements"
    print " -c clear"        

if __name__ == "__main__":
    playbackfile = ''
    clear = False    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hf:c",["file="])
    except getopt.GetoptError:
      usage()
      sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt in ("-f", "--file"):
            playbackfile = arg
        elif opt == "-c":
            clear = True        
        else:
            usage()
            sys.exit(1)
    if playbackfile == '':
        usage()
        sys.exit(1)


    s_list = get_session()

    if len(s_list) != 1:
        print "Error: Need excatly one running session!\n"
        sys.exit()

    node_map = get_nodes_by_id(s_list[0])

    record(playbackfile, node_map, s_list[0], clear)
