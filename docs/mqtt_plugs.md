# MQTT Power Plugs

## Introduction
GrowBuddies is a set of IoT devices for controlling VPD and CO2 in indoor grow tents. They use MQTT for communication. Most power plugs can't send or receive MQTT messages. However, plugs with Tasmota firmware can.  This means we can do things like plug in a CO2 solenoid into a Tasmotized plug and turn it on/off with MQTT messages.  GrowBuddies uses three Tasmotized plugs.  Two are used for MistBuddy.  One to turn the mister on/off and another to turn the fan on/off.  One is used for StomaBuddy to turn the CO2 solenoid on/off.

## Hardware Requirements
