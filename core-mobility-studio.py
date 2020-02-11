#!/usr/bin/env python2

# core-mobility-studio
# Written by Lars Baumgaertner (c) 2017
#
# requirements: tkinter, idle, appjar
# 
# Installation on Ubuntu:
# $ apt-get install python-tk idle python-pip
# $ pip install appjar

# import the library
import commands
import subprocess
import shlex
from appJar import gui
from coreposlib import *

play_process = None

def check_process():
    global play_process    
    if play_process != None:
        app.setStatusbar("Status: running", 2)
        play_process.poll()        
        if play_process.returncode != None:            
            change_state("normal","")
            play_process = None
    else:
        app.setStatusbar("Status: stopped", 2)

def get_filename():
    f = app.getEntry("Filename")
    if f == "":
        app.errorBox("Error", "Please enter filename.")
    return f

def get_delay():
    d_entry = app.getEntry("Delay")
    if d_entry == "":
        return ""
    try:
        d = float(d_entry)
        return " -d " + d_entry
    except ValueError:
        app.warningBox("Delay in seconds", "Please enter only valid float numbers. Ignoring value for now!")
        return ""

cur_step = 0
total_steps = 0
def get_total_number_of_steps():
    f = get_filename()
    if f != "":
        s_list = get_session()

        if len(s_list) != 1:
            print "Error: Need excatly one running session!\n"
            sys.exit()
        node_map = get_nodes(s_list[0])
        scenario = load_posfile(f, node_map, s_list[0])
        return len(scenario["step_list"])

def press_file(btn):
    global cur_step
    filepath = app.saveBox(fileTypes=[("Position Files", "*.pos"), ("All Files", "*.*")])
    print filepath
    app.setEntry("Filename", filepath)
    cur_step = 0
    update_steps()
    press_step_move("|<")

def update_steps():
    global total_steps
    total_steps = get_total_number_of_steps()
    app.setStatusbar("Steps: " + str(cur_step) + "/" + str(total_steps), 1)

def press_record(btn):
    print "pressed: ", btn
    filepath = get_filename()
    if filepath != "":
        cmd = "./core-record.py -f " + filepath
        print cmd
        commands.getstatusoutput(cmd)
        update_steps()

def change_state(newstate, except_btn):
    btns = ["Playback", "Loop", "Record Step", "|<", "<", ">", ">|"]
    for i in btns:
        if i != except_btn:
            app.setButtonState(i, newstate)

def press_playback(btn):
    global play_process
    print "pressed: ", btn
    filepath = get_filename()
    if play_process != None:
        play_process.kill()
        play_process = None
        change_state("normal",btn)
    else:
        if filepath != "":
            cmd = "./core-automator.py -f " + filepath + get_delay()
            print cmd
            args = shlex.split(cmd)
            play_process = subprocess.Popen(args)
            change_state("disabled",btn)

def press_loop(btn):
    global play_process
    print "pressed: ", btn
    if play_process != None:
        play_process.kill()
        play_process = None
        change_state("normal",btn)
    else:
        filepath = get_filename()
        if filepath != "":
            cmd = "./core-automator.py -l -f " + filepath + get_delay()        
            args = shlex.split(cmd)
            play_process = subprocess.Popen(args)
            change_state("disabled",btn)

def press_step_move(btn):
    global cur_step, total_steps
    #print "pressed: ", btn , total_steps
    if btn == "|<":
        cur_step = 0
    elif btn == ">|":
        cur_step = total_steps - 1
    elif btn == "<":        
        if cur_step > 0:
            cur_step -= 1
    elif btn == ">":
        if cur_step < (total_steps - 1):
            cur_step += 1  
    filepath = get_filename()
    if filepath != "":
        cmd = "./core-automator.py -f " + filepath + " -s " + str(cur_step)        
        commands.getstatusoutput(cmd)
        app.setStatusbar("Steps: " + str(cur_step+1) + "/" + str(total_steps), 1)


# top slice - CREATE the GUI
app = gui("CORE Mobility Studio")

### fillings go here ###

app.addLabelEntry("Filename", 1,0)

app.addButton("Select File", press_file, 1,1)

app.addHorizontalSeparator(2,0,2)

app.addLabelEntry("Delay",3 ,0)

app.addHorizontalSeparator(4,0,2)


app.addButtons(["Playback", "Loop"], [press_playback, press_loop], 5, 0, 2)
app.addButtons(["|<", "<", ">", ">|"], [press_step_move, press_step_move, press_step_move, press_step_move], 6, 0, 2)
app.addHorizontalSeparator(7,0,2)
app.addButton("Record Step", press_record, 8, 0, 2)

app.addStatusbar(fields=3)

# background jobs

app.setPollTime(500)
app.registerEvent(check_process)

# bottom slice - START the GUI
app.go()
