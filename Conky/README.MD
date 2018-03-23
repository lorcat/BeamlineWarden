# Conky configuration for using at P02.2 beamline

## Purpose
Conky puts an overlay window showing current parameters for the display.
Requires setup for a specific user. It can be started remotely:
**cd $CONKYDIR**
**DISPLAY=:0 /usr/bin/conky -d -c $CONKYDIR/co_main &**

## Directory structure
- **co_main** - configuration file for conky
- ***.py** - python files containing additional conky layout elements


