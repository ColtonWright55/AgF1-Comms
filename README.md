# AgF1-Comms
LinuxCNC poller and socket in python


## IP Connection documentation

Make sure client (windows PC) has setting:

Settings > Network & Internet > Advanced network settings > Advanced sharing settings > Turn on network discovery everywhere

You have `ipconfig` on windows and `ifconfig` on linux. The physical "ETHERNET" port on linux is `ifconfig eth1`. You have to set that port with an IP address, with the same IP as the windows machine, but on a different subnet. For instance, I have set `sudo ifconfig eth1 172.30.94.50 netmask 255.255.255.0 up` on linux and then Ethernet Properties > Intel(R) Ethernet Connection (17) I219-LM > Internet Protocol Version 4 (TCP/IPv4) > Properties > IP Address: 172.30.95.100 > Subnet mask: 255.255.255.0

Then when I run on windows `ping 172.30.94.50` it works, and on linux `ping 172.30.94.100` that works. Then I started the rip-environment in pathpilot, ran `server.py`, ran `client.py` on windows, and it worked.
`

You should be able to ping windows from linux and linux from windows now.

Although, for some reason when you run `server.py` and `client.py` it resets `ifconfig eth1`. So you have to enter again `sudo ifconfig eth1 172.30.94.50 netmask 255.255.255.0 up`

This is all weird because IP settings without a router are strange. They have to be on same IP with different subnet if there isn't a router I think.