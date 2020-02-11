#!/usr/bin/env python2

# core-automator - replay of core node positions
# Written by Lars Baumgaertner (c) 2017

import sys
import commands
import time
import getopt
import string

from coreposlib import *

def usage():
    print sys.argv[0] + ' [param] -f <inputfile>'
    print " -f <inputfile> recorded movements"
    print " -d <delay> delay between steps (seconds as float)"
    print " -l loop"
    print " -i set initial positions"
    print " -s <int_step> load specific step (range: 0..MAXSTEP-1)"  
    print " -c <core_session_number> control specific session (default: first session)"  

if __name__ == "__main__":
    playbackfile = ''
    loop = False
    init_pos = False
    set_step = -1
    delay = 1.0
    delay_set = False
    session = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hf:lid:s:c:",["file=","delay=","step=","core-session="])
    except getopt.GetoptError:
      usage()
      sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt in ("-f", "--file"):
            playbackfile = arg
        elif opt in ("-d", "--delay"):
            delay = float(arg)
            delay_set = True
        elif opt in ("-s", "--step"):
            set_step = int(arg)            
        elif opt in ("-c", "--core-session"):
            session = arg
        elif opt == "-l":
            loop = True
        elif opt == "-i":
            init_pos = True
        else:
            usage()
            sys.exit(1)
    if playbackfile == '':
        usage()
        sys.exit(1)


    s_list = get_session()

    if len(s_list) != 1 and session == "":
        print "Error: Need excatly one running session or -c <session_number>!\n"
        sys.exit()
    
    if session == "":
        session = s_list[0]
    else:
        if not session in s_list:
            print "Error: Invalid session ", session
            sys.exit()

    node_map = get_nodes(session)

    scenario = load_posfile(playbackfile, node_map, session, delay, delay_set)
    if init_pos:
        play_step(scenario, 0)
    elif set_step >= 0:
        play_step(scenario, set_step)
    else:
        replay_parsed(scenario, loop)
