Run the below commands on bash
!pip install --upgrade pip
!pip install -U selenium
!pip install -U webdriver-manager


** Daemonize JupyterLab
https://www.vultr.com/docs/how-to-set-up-a-jupyterlab-environment-on-ubuntu-22-04/

1. sudo systemctl start jupyterlab

2. find google-chrome path
	whereis google-chrome-stable
2. Enable chrome to open a port for remote debugging.
https://cosmocode.io/how-to-connect-selenium-to-an-existing-browser-that-was-opened-manually/
	google-chrome-stable --remote-debugging-port=9222 --user-data-dir="~/ChromeProfile"