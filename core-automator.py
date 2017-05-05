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

def play_step(scenario, step_number):
    step_list = scenario["step_list"]
    session = scenario["session"]    
    delay = scenario["delay"]
    for node in step_list[step_number]:
        if node[1] != '-' and node[2] != '-':
            cmd = "coresendmsg node number=" + node[0] + " xpos=" + node[1] + " ypos=" + node[2]
            (ret, val) = commands.getstatusoutput(cmd)        
        if node[4] != "":                    
            cmd = "vcmd -c /tmp/pycore." + session + "/" + node[3] + " -- bash -c '" + node[4] + "'"
            (ret, val) = commands.getstatusoutput(cmd)

def replay_parsed(scenario, loop = False):
    step_list = scenario["step_list"]
    session = scenario["session"]    
    delay = scenario["delay"]
    while True:        
        count = 0
        for i in range(len(step_list)):
            play_step(scenario, i)
            print "step ", i
            time.sleep(delay)
        
        if loop == True:
            print "REVERSE LOOP"
            scenario["step_list"] = list(reversed(step_list))
        else:
            break


def load_posfile(filename, nodemap, session, cmd_delay=1.0, cmd_delay_set=False):
    step_number=0
    step_list = []
    step_moves = []
    delay=1.0
    with open(filename, "r") as f:
        for line in f:
            line=line.strip()
            if line == "" or line.startswith("#"):
                continue                
            fields = line.split()
            if line.startswith("%delay") and len(fields) == 2:
                delay=float(fields[1])
            if line == "-- STEP":
                step_number += 1                
                step_list.append(step_moves)
                step_moves=[]                
            if len(fields) >= 3:
                try: node = nodemap[fields[0]]
                # skip the step, if the node is not available
                except KeyError: continue
                xpos = fields[1]
                ypos = fields[2]

                exec_cmd = ""
                if len(fields) > 3:
                    exec_cmd = string.join(fields[3:], " ")
                step_moves.append((node,xpos,ypos, fields[0], exec_cmd))
    
    if cmd_delay_set == True:
        delay = cmd_delay
    scenario = {"session": session,                 
        "delay": delay, 
        "step_list": step_list}
    return scenario     

def usage():
    print sys.argv[0] + ' [param] -f <inputfile>'
    print " -f <inputfile> recorded movements"
    print " -d <delay> delay between steps (seconds as float)"
    print " -l loop"
    print " -i set initial positions"
    print " -s <int_step> load specific step (range: 0..MAXSTEP-1)"    

if __name__ == "__main__":
    playbackfile = ''
    loop = False
    init_pos = False
    set_step = -1
    delay = 1.0
    delay_set = False
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hf:lid:s:",["file=","delay=","step="])
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

    scenario = load_posfile(playbackfile, node_map, s_list[0], delay, delay_set)
    if init_pos:
        play_step(scenario, 0)
    elif set_step >= 0:
        play_step(scenario, set_step)
    else:
        replay_parsed(scenario, loop)
