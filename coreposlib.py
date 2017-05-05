#!/usr/bin/python

# coreposlib - library for replay of core node positions
# Written by Lars Baumgaertner (c) 2017

import sys
import commands
import time
import getopt
import string
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
