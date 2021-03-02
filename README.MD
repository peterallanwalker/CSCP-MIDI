# CSCP-MIDI

A Python 3.x application...

Provides connectivity and two-way comms between devices supporting the CSCP protocol and devices/software supporting the MIDI protocol
* Provides remote control over Calrec Audio mixers from a multitude of low-cost physical MIDI controllers

* Allows Calrec Audio mixers to control DAW software applications

This application has been developed and tested using:
* [Korg NanoKontrol2](https://www.korg.com/uk/products/computergear/nanokontrol2/) - A physical MIDI controller. 

* [Reaper](https://www.reaper.fm/) - DAW software 

* [Calrec Audio Brio](https://calrec.com/) - Live/Pro/Broadcast Audio mixer (supporting the CSCP protocol). 


## Getting Started

CSCP-MIDI.py is the entry point for the main application.
The supporting .py files will run with unit tests.


### Prerequisites
Third party Python library dependencies:
* **[json](https://docs.python.org/3/library/json.html)** - for reading/writing connection configuration and control mapping files 

* **[socket](https://realpython.com/python-sockets/)** - for sending/receiving data over an IP connection. 

* **[struct](https://www.delftstack.com/howto/python/how-to-convert-int-to-bytes-in-python-2-and-python-3/)** - for packing decimal payload data into hex bytes ready to send CSCP data using socket

* **[threading](https://realpython.com/intro-to-python-threading/)** - for running processes in a thread so they can run continuously without blocking the main application (threads are used to receive data on the open CSCP & MIDI connections)

* **[mido](https://mido.readthedocs.io/en/latest/)** - for midi comms (install with 'pip install mido'.

* **[rtmidi](https://pypi.org/project/python-rtmidi/)** - used by mido (install with 'pip install python-rtmidi'.

* **[time](https://www.tutorialspoint.com/python/time_sleep.htm)** - used to pause CSCP_connection between connection attempts


### Project files

* **CSCP-MIDI.py** - the Main Application.

* **CSCP_MIDI_settings.py** - provides `get_settings()` & `save_settings()` to load/save config data to/from a json file
    and gets validated user input to confirm or edit the config settings. Validates user input (validates IP address, 
    available midi ports etc), returns dictionary of configuration settings.

* **CSCP_UTILS.py** - provides constants for the CSCP protocol as well as functions for calculating and verifying 
    CSCP message checksums.

* **CSCP_connection.py** - provides `Connection` class/object to handle CSCP comms, runs a separate thread receiving and 
    buffering incoming messages without blocking the main app, and provides `send_message() `& `get_message()` methods 
    to send and receive CSCP messages.

* **MIDI_connection.py** - provides `Connection` class/object to handle MIDI comms, runs a separate thread receiving and
    buffering incoming messages without blocking the main app, and provides `send_message() `& `get_message()` methods 
    to send and receive MIDI messages.

* **CSCP_to_MIDI.py** - provides `convert_message()` function to translate CSCP messages to mido MIDI, Takes a dict of 
    control mapping parameters sourced from external json file (by CSCPS_MIDI_settings.py) converts fader scaling and 
    other MIDI params.

* **MIDI_to_CSCP.py** - provides `convert_message()` function to translate mido midi messages to CSCP. Takes a dict of 
    control mapping sourced from external json file (by CSCPS_MIDI_settings.py) converts fader scaling and other MIDI 
    params.

* **CSCP_unpack.py** -  provides `unpack_data()` function, called by CSCP_connection. Takes byte strings, validates and
    extracts CSCP messages.

* **CSCP_decode.py** - provides a `Message` class/object that initialises from a validated CSCP byte string, called by 
    CSCP_connection. The resulting object has message parameters as attributes (and has a `__str__()`) method to print it).

* **CSCP_encode.py** - provides a `Message` class/object that initialises from a set of message parameters to create a 
    CSCP Message object, including `Message.encoded` - a byte string ready to be sent to a mixer using 
    `CSCP_Connections.send()` Can also be printed using its __str__ method.

* **settings.json** - The last used connection settings. Loaded/saved by CSCP_settings.py

* **korg_sonar_reaper.json** & others - control mapping files to translate between CSCP message parameters and given 
    MIDI modes. Allows users to tweak control mapping by editing the json. e.g. if they want to change which 
    control/strip on the mixer relates to which control/channel on the DAW/MIDI controller

### Usage
The following instructions relate to Calrec Brio & Summa mixers. For other Calrec mixer types, 
please refer to their installation manual for configuring CSCP.

* Connect one of the LAN ports on your Calrec Audio mixer to your PC (or to the same network your PC is on).

* Go to System-Settings>LAN config and set the mixer's IP address to one that is reachable from your PC 
(and set a static IP address on your PC if necessary).

* Go to System-Settings>Control-Protocols, check/set the TCP Port the mixer is using for CSCP and ensure CSCP is set to
enabled. 

* If using a physical controller, its midi port will automatically be available to select from the CSCP-MIDI application
if the controller is connected when CSCP-MIDI starts up.
    * CSCP-MIDI has been tested with the KorgNanoKontrol2
        * To use in its' default "CC" mode, selectable on the 
            controller by holding its SET MARKER & CYCLE buttons when connecting it to your PC.
        * To use in "Sonar" mode, hold the SET MARKER & RECORD buttons when connecting.
        * To request support for other MIDI modes, contact peter.allan.walker@gmail.com


* If using DAW software running on the same PC as this application on Windows, then 3rd party software is required to provide virtual midi ports (to allow midi comms between applications running in Windows)
    * Download [loopmidi](https://www.tobias-erichsen.de/software/loopmidi.html) by Tobias Erichsen. Open loopmidi and
    click the '+' button to add a MIDI port that will be accessible to your DAW and to CSCP-MIDI.

    * Configure your DAW for use with a MIDI controller, selecting the MIDI port/s created by loopmidi.
        * CSCP-MIDI has been tested with the Reaper DAW:
            * Reaper>Options>Preferences>Control-Surfaces, select "Add", choose "Makie Control Universal" and select the 
            midi ports created by loopmidi. Note, It is best to configure two MIDI ports in loop midi, one for input
            and one for output to avoid feedback loops. Ensure you select the correct ports here and in CSCP-MIDI when it
            starts.
            * Also in preferences, select Audio>MIDI-Devices and enable the MIDI I/O created from loopmidi.
            
* Start CSCP-MIDI using `python cscp-midi.py` or running the .exe. IF it has been run before, you will be presented
with the last used settings. If you need to change the settings press 'n' and enter the mixer's IP address, CSCP port,
the MIDI ports you are using and the MIDI mode...
    * **You now have two-way comms between your Calrec mixer and your MIDI device/DAW!**      


## Author

**Peter Walker**
Feedback/requests, email:peter.allan.walker@gmail.com
