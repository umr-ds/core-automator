#!/usr/bin/python

# core-record - record core node positions
# Written by Lars Baumgaertner (c) 2017

import sys
import commands
import time
import getopt
import glob
import re

def get_session():
    sessions = []
    (ret, val) = commands.getstatusoutput("coresendmsg -T -l sess flags=str,txt")
    for line in val.split("\n"):
        if "CORE_TLV_SESS_NUMBER" in line:
            sessions.append(line.split(":")[1].strip())
    return sessions

def get_nodes_by_id(session_number):
    nodes = {}
    lines = [line.rstrip('\n') for line in open("/tmp/pycore." + session_number + "/nodes")]
    for l in lines:
        entries = l.split(" ")
        nodes[entries[0]] = entries[1]
    return nodes

def record(filename, nodemap, session, clear=False):
    mode = "a"
    if clear:
        mode = "w"
    
    with open(filename, mode) as out:
        for f in glob.glob("/tmp/pycore." + session + "/*.xy"):
            m = re.search("/n(\d+).xy$", f)
            node_name = nodemap[m.group(1)]
            with open(f, "r") as xy:
                coord = xy.read().strip().split()
                print f, node_name, coord                
                out.write(node_name + " " + coord[0].split(".")[0] + " " + coord[1].split(".")[0] +"\n")
        out.write("-- STEP\n")

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
