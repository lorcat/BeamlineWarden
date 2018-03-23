# Monitoring project of P02.2 beamline Petra-III, DESY

# Description/purpose
Operation and debugging of the beamline operating within heterogeneous information environment requires:
- Agents collecting, merging information
- Agents preparing data for various clients

This project is a simple data proxy realization with a backend of a Memcached data base.
Main Tango server operates on a time interval level - ticks (default 0.1s).
On the startup procedure Tango Server tests presence of plugins - individual programs working as Agents.

Each plugin is written as a simple one task program and has parameters defining interval of operation and its startup offset.
This way it makes it easier to debug and create new plugins from scratch, also by copy and paste.
Plugins are started as a part of separate threads. They can share certain common code.

# Configuration
Main TangoServer configuration is written into TangoServer/app/config.py file.
Plugins can have their own configuration. The recommended approach is to use TangoServer/app/plugins/plugins_common/ directory for such tasks

# Tango configuration
The server has Start/Stop commands and attributes covering TickTackPeriod and NumThreads
Plugins are found only upon the initialization process of the TangoServer (can be reimplemented into a command).

# Directory structure
Plugins are placed inside the TangoServer/app/plugins/ folder

TangoServer/BeamlineWarden - shell script used to start the TangoServer
TangoServer/BeamlineWarden.py - implementation of the TangoServer (PyTango)
TangoServer/BeamlineWarden_daemon.py - simple `daemon` implementation - run until killed, no system signals processed

# Python Dependencies
Tango Server: (PyTango)[https://pypi.python.org/pypi/PyTango], (pluginbase)[http://pluginbase.pocoo.org/]
Plugins: json, plugin_memcached, etc.

