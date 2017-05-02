#!/usr/bin/python

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

def press_file(btn):
    filepath = app.saveBox(fileTypes=[("Position Files", "*.pos"), ("All Files", "*.*")])
    print filepath
    app.setEntry("Filename", filepath)

def press_record(btn):
    print "pressed: ", btn
    filepath = get_filename()
    if filepath != "":
        cmd = "./core-record.py -f " + filepath
        print cmd
        commands.getstatusoutput(cmd)

def change_state(newstate, except_btn):
    btns = ["Playback","Back to 1", "Loop", "Record Step"]
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
            cmd = "./core-automator.py -l -f " + filepath            
            args = shlex.split(cmd)
            play_process = subprocess.Popen(args)
            change_state("disabled",btn)

def press_back_1(btn):
    print "pressed: ", btn
    filepath = get_filename()
    if filepath != "":
        cmd = "./core-automator.py -i -f " + filepath
        print cmd
        commands.getstatusoutput(cmd)

# top slice - CREATE the GUI
app = gui("CORE Mobility Studio")

### fillings go here ###

app.addLabelEntry("Filename", 1,0)

app.addButton("Select File", press_file, 1,1)

app.addHorizontalSeparator(2,0,2)

app.addLabelEntry("Delay",3 ,0)

app.addHorizontalSeparator(4,0,2)


app.addButtons(["Playback", "Loop", "Back to 1"], [press_playback, press_loop, press_back_1], 5, 0, 2)
app.addHorizontalSeparator(6,0,2)
app.addButton("Record Step", press_record, 7, 0, 2)

app.addStatusbar(fields=3)

# background jobs

app.setPollTime(500)
app.registerEvent(check_process)

# bottom slice - START the GUI
app.go()
