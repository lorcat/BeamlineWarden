# Crontab twitter bot configuration for using at P02.2 beamline

## Purpose
Beamline scientists usually have olny limited access to the experiemntal machines and execution rights for different processes.
Crontab represents a userland capability to run processes at a given interval.
Simple python program testing remote data vs specific events and reporting them in twitter.

Requires setup for a specific user (i.e. beamline user). It can be started remotely.

## Directory structure
- **crontab_daemon.py** - python executable file collecting data and performing twitter notifications on certain events.
- **app/config.py** - configuration file for twitter bot. API keys should be placed there.
