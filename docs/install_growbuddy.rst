*****************
Install GrowBuddy
*****************

At the end of installing GrowBuddy, you'll be able to attach sensors......

Step 1: Install the GrowBuddy Server.
=====================================
- Get a Raspberry Pi up and Running
  
The GrowBuddy Server runs on a Raspberry Pi.  I've used either a 3 or 4.  As for the OS, I've stuck with Buster even though the Raspbian Foundation have released newer OS.  

- Install and configure an mqtt broker.

- Install and configure influxdb.

Step 2: Create a folder on the Raspberry Pi that will hold the GrowBuddy Python classes.
========================================================================================
Make a directory, something like:

::
    $mkdir GrowBuddy

Step 3: Create a Python virtual environment.
============================================
`Bernard's video around 21 minutes ingives a great explanation of virtual environments if these are unfamiliar to you <https://youtu.be/ApDThpsr2Fw?t=1274>`_ .  Given Bernard's recommendation,
we'll use `virtualenv <https://virtualenv.pypa.io/en/latest/>`_ 

test

adfljaldfkjdklajf
adflajsdflkadjsfkj