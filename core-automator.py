#!/usr/bin/python

# core-automator - replay of core node positions
# Written by Lars Baumgaertner (c) 2017

import sys
import commands
import time
import getopt
import string

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

def replay_parsed(step_list, session):
    while True:
        print "REVERSE LOOP"
        step_list = list(reversed(step_list))
        count = 0
        for steps in step_list:
            count += 1
            for node in steps:
                cmd = "coresendmsg node number=" + node[0] + " xpos=" + node[1] + " ypos=" + node[2]
                (ret, val) = commands.getstatusoutput(cmd)
                if node[4] != "":                    
                    cmd = "vcmd -c /tmp/pycore." + session + "/" + node[3] + " -- bash -c '" + node[4] + "'"
                    (ret, val) = commands.getstatusoutput(cmd)

            print "step ", count
            time.sleep(1)

def playback(filename, nodemap, session, loop=False, init_pos=False):
    step_number=0
    step_list = []
    step_moves = []
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
                step_list.append(step_moves)
                step_moves=[]                
            if len(fields) >= 3:
                node = nodemap[fields[0]]
                xpos = fields[1]
                ypos = fields[2]

                cmd = "coresendmsg node number=" + node + " xpos=" + xpos + " ypos=" + ypos
                #print cmd
                (ret, val) = commands.getstatusoutput(cmd)
                exec_cmd = ""
                if len(fields) > 3:
                    exec_cmd = string.join(fields[3:], " ")
                    cmd = "vcmd -c /tmp/pycore." + session + "/" + fields[0] + " -- bash -c '" + exec_cmd + "'"
                    #print "EXEC: ", exec_cmd
                    #print cmd
                    (ret, val) = commands.getstatusoutput(cmd)
                    print ret, val 
                step_moves.append((node,xpos,ypos, fields[0], exec_cmd))
    if loop:
        replay_parsed(step_list, session)

def usage():
    print sys.argv[0] + ' [param] -f <inputfile>'
    print " -f <inputfile> recorded movements"
    print " -l loop"
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

    playback(playbackfile, node_map, s_list[0], loop, init_pos)
