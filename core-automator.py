#!/usr/bin/python

import sys
import commands
import time
import getopt

def get_session():
    sessions = []
    (ret, val) = commands.getstatusoutput("coresendmsg -T -l sess flags=str,txt")
    for line in val.split("\n"):
        if "CORE_TLV_SESS_NUMBER" in line:
            sessions.append(line.split(":")[1].strip())
    return sessions

def get_nodes(session_number):
    nodes = {}
    lines = [line.rstrip('\n') for line in open("/tmp/pycore." + session_number + "/nodes")]
    for l in lines:
        entries = l.split(" ")
        nodes[entries[1]] = entries[0]
    return nodes

def playback(filename, nodemap, loop=False, init_pos=False):
    step_number=0
    with open(filename, "r") as f:
        for line in f:
            line=line.strip()
            if line == "" or line.startswith("#"):
                continue
            fields = line.split()
            if line == "-- STEP":
                if init_pos == True:
                    sys.exit()
                time.sleep(1)
                step_number += 1
                print "step: " + str(step_number)                
            if len(fields) == 3:                
                cmd = "coresendmsg -T node number=" + nodemap[fields[0]] + " xpos=" + fields[1] + " ypos=" + fields[2]
                print cmd
                (ret, val) = commands.getstatusoutput(cmd)
                time.sleep(0.05)


def usage():
    print sys.argv[0] + ' [param] -f <inputfile>'
    print " -f <inputfile> recorded movements"
    print " -l loop (not implemented yet)"
    print " -i set initial positions"    

if __name__ == "__main__":
    playbackfile = ''
    loop = False
    init_pos = False
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hf:li",["file="])
    except getopt.GetoptError:
      usage()
      sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt in ("-f", "--file"):
            playbackfile = arg
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

    if len(s_list) != 1:
        print "Error: Need excatly one running session!\n"
        sys.exit()

    node_map = get_nodes(s_list[0])

    playback(playbackfile, node_map, loop, init_pos)
