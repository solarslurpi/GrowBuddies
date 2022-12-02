(systemd_doc)=
# Systemd

[systemd](https://wiki.archlinux.org/title/Systemd) is used to configure how and when to run the Python scripts.  The GrowBuddies use Systemd to run in the background - when you want it to.  I run mine pretty much all the time. Another nice feature is the availability of the logging info.

## Useful Learning Resources on Systemd

I found the following info useful to figure out how to get systemd to do what I want:

- [Intro to systemd video](https://youtu.be/AtEqbYTLHfs?t=147).
- [Place in the video where using commands starts](https://youtu.be/AtEqbYTLHfs?t=230).
- [systemd on Raspberry Pi documentation](https://www.raspberrypi.org/documentation/linux/usage/systemd.md).
- [Article on how to autorun service using systemd](https://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/).
- [archlinux systemd documentation](https://wiki.archlinux.org/title/Systemd)
## Setting Up A Python Script to run as a Systemd service
### Write the Script
1. The first thing to do is write the .service file.  Here are the `snifferbuddy_storereadings`.service` file I used for the `snifferbuddy_storereadings.py` code.


```{literalinclude} ../growbuddiesproject/growbuddies/examples/snifferbuddy_storereadings.service
:language: python
:linenos: true
```
2. From the directory where the service file is located, set permissions so systemd can execute the script: `sudo chmod +x {python script}`.  For example,  `sudo chmod +x snifferbuddy_storereadings.py`.
3. Copy the systemd service file to `/lib/systemd/system`.  `sudo` privileges are needed.  For example, `sudo cp snifferbuddy_storereadings.service /lib/systemd/system/.`
4. Enable the service with `sudo systemctl enable snifferbuddy_storereadings.service`.
5. Check to make sure the service has been enabled with `systemctl is-enabled snifferbuddy_storereadings.service`.
6. Start the service with `sudo systemctl start snifferbuddy_storereadings.service`.
7. Check to make sure the service has been started with `systemctl is-active snifferbuddy_storereadings.service`.  In this example, starting the service failed.  To find out why, try `journalctl -u snifferbuddy_storereadings.service`.  Here are log lines from one of the services I ran:

```{literalinclude} logreadings.txt
:language: bash
:emphasize-lines: 3
```
The highlighted line shows the service failed to start up /home/py/**growbuddy**/py_env... .

Oh, right! our directory is growbuddies.  I changed this back in the service file.


The reason for the above example is to give a little detail on the approach I take when I can't get the service to start.  I hope it is helpful.
