# core-automator

Various helper scripts to automate node movement in [CORE](https://www.nrl.navy.mil/itd/ncs/products/core)

## Prerequisites

* Python 2.7
* Installed and running CORE
* Only **ONE** active core session is supported at the moment
* Nodes must be placed on grid using `core-gui`
* Session must already be started

## Scripts

`core-record.py` - record current node layout to a file (default: appending)

`core-automator.py` - replay a recorded position file, sleep between steps (default: 1s)

## Record File Format

Empty lines are ignored.

`#` Mark a comment - only allowed at the beginning of a line

`-- STEP` Marks the end of a movement block, sleep is triggered

`<node_name> <int_x> <int_y>` describes the position of a node

Example movement log:
```
# initial node placement

robot1 50 50
drone1 100 50
drone2 200 150
drone3 350 150
drone4 400 250
center1 763 276

-- STEP
robot1 55 50
drone1 110 50
drone2 200 170
drone3 350 130
drone4 370 250

-- STEP
robot1 60 50
drone1 120 50
drone2 210 190
drone3 360 120
drone4 420 250
```

**Note:** Node *center1* is only mentioned in the initial setup, no movement is applied later on as this node is meant to be static.