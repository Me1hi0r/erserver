# dependencies:
	* Django (pip)
	* mplayer.py (pip)
	* omxplayer-wrapper(pip)
	* mplayer (apt-get)
	* uwsgi

# for devs (Linux):
	* run "sudo apt-get install mplayer";
	* create a new Pycharm project named "ERServer";
	* clone that repo;
	* put this repo's content into ERServer folder in your new Pycharm project
	* **DO NOT ADD & COMMIT db.sqlite3**

# deployment:
#### download server:

	cd ~/
	git clone https://your_login@bitbucket.org/ind_developers/erserver.git

#####	static IP configuration:

**sudo nano /etc/dhcpcd.conf**

	interface eth0
	static ip_address=192.168.10.100/24
	static routers=192.168.10.1
	static domain_name_servers=192.168.10.1

##### HDMI sound output enable:

	sudo raspi-config-> Advanced options-> Audio-> Force HDMI

##### enable autostart at boot:

**sudo nano /etc/xdg/autostart/erserver.desktop**

	[Desktop Entry]
	Type=Application
	Name=erserver
	Comment=erp + music ctrl
	NoDisplay=false
	Exec=/usr/bin/lxterminal -e /home/pi/erserver_start.sh &
	NotShowIn=GNOME;KDE;XFCE;

**nano /home/pi/erserver_start.sh**

	#!/bin/bash
	cd /home/pi/erserver
	uwsgi --ini erserver_uwsgi.ini

**chmod +x /home/pi/erserver_start.sh**

**sudo ln -s /home/pi/erserver/erserver_nginx.conf /etc/nginx/sites-enabled/**

_in prj dir:_

	`python3 manage.py collectstatic`

#### change hostname

`sudo raspi-config` -> `Networks Options` -> `Hostname` -> input `erserver` -> `ok` -> `finish` -> `reboot`

#### suppress socket warning:

**cd ~/**  
**mkdir .mplayer**  
**echo nolirc=yes > .mplayer/config**  

#### clean setup
clean all migration
delete db
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser



master onetwo
operator 1passpass

#### create quest
login admin
go to admin panel
Quests +add
Panel-States CURRENT QUEST new_quest_name


