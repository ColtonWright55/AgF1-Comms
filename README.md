# AgF1-Comms
LinuxCNC poller and socket in python


## IP Connection documentation

### Client setup (Windows)
Make sure client (windows PC) has setting:

Settings > Network & Internet > Advanced network settings > Advanced sharing settings > Turn on network discovery

You have `ipconfig` on windows and `ifconfig` on linux. The physical "ETHERNET" port on linux is `ifconfig eth1`. You have to set that port with an IP address, with the same IP as the windows machine, but on a different subnet. For instance, I have set `sudo ifconfig eth1 172.30.95.50 netmask 255.255.255.0 up` on linux and then Ethernet Properties > Intel(R) Ethernet Connection (17) I219-LM > Internet Protocol Version 4 (TCP/IPv4) > Properties > IP Address: 172.30.95.100 > Subnet mask: 255.255.255.0

Then when I run on windows `ping 172.30.94.50` it works, and on linux `ping 172.30.94.100` that works. Then I started the rip-environment in pathpilot, ran `server.py`, ran `client.py` on windows, and it worked.

You should be able to ping windows from linux and linux from windows now.

This is all weird because IP settings without a router are strange. They have to be on same IP with different subnet if there isn't a router I think.

### Server setup (Linux/Pathpilot)

You can use `sudo ifconfig eth1 172.30.95.50 netmask 255.255.255.0 up` to set `eth1` internet address, but NetworkManager can dynamically change your ip address. You need to setup `eth1` in the `interfaces` configuration file so that the IP does not change during runtime or restart. You will edit `/etc/network/interfaces` and add the following to the bottom of the file:

```
auto eth1
iface eth1 inet static
    address 172.30.95.50
    netmask 255.255.255.0
```

This is helpful if you get stuck: https://wiki.debian.org/NetworkConfiguration

Once this was done, `eth1`'s ip address was persistent through reboots, and server stability issues were fixed.

## Agility Forge Device IP's

Promess Controller
172.30.95.51
255.255.255.0

Promess PLC
To change the Promess PLC's IP you will need to log in as the admin.
Username: Admin
Password: 123
172.30.95.52
255.255.255.0

Windows PC
172.30.95.55
255.255.255.0

Linux Network Port
172.30.95.50
255.255.255.0

Linux Machine Port
10.10.10.9
255.255.255.0

Micro-Epsilon Linescanner
172.30.95.53
255.255.255.0

Micro-Epsilon Thermal Camera USB Server
Software needed for setup : https://www.wut.de/e-53www-15-inus-000.php
For setup, you follow Optris quick start guide: https://optris.com/wp-content/uploads/2024/10/ACPIUSBSGB-QSG-E2023-05-C.pdf
USB Server IP: 172.30.95.54
Subnet:        255.255.255.0


## Agility Forge start server on boot

To have the Linux box start server.py on boot,

Add to `/etc/rc.local`:

```
#!/bin/sh -e
#
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

if [ -e /home/operator/monitorWatch ]; then
  if [ -d /home/operator/tmc/venv ]; then
    # we make sure the monitorWatch.txt log file can be changed by the later logrotator script
    if [ ! -e /home/operator/gcode/logfiles/monitorWatch.txt ]; then
      touch /home/operator/gcode/logfiles/monitorWatch.txt
    fi
    chown operator /home/operator/gcode/logfiles/monitorWatch.txt
    chgrp operator /home/operator/gcode/logfiles/monitorWatch.txt
    chmod 644 /home/operator/gcode/logfiles/monitorWatch.txt
    bash -c "source /home/operator/tmc/venv/bin/activate; /home/operator/monitorWatch" >> /home/operator/gcode/logfiles/monitorWatch.txt
  fi
fi

su - operator -c "
  cd /home/operator/v2.12.1/cjw/AgF1-Comms
  source /home/operator/v2.12.1/scripts/rip-environment.sh
  python -u my_server.py >> /home/operator/server.log 2>&1 &
"


exit 0

```

Note that server logs will be added to /home/operator/server.log
rc.local script is ran on boot by the initialization system. The pathpilot PC is an older distribution and does not have systemd, Its sysvinit i think. 

Note: I had to update server.py to work on boot
ToolpathGenerator may require a restart to connect to server sometimes
server.py renamed my_server.py