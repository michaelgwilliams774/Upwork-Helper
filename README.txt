// To run the notebook on google-colab-research, 
// You need to install chrome driver manager first.

// Copy the following commands on the cell and run

%%shell
# Ubuntu no longer distributes chromium-browser outside of snap
#
# Proposed solution: https://askubuntu.com/questions/1204571/how-to-install-chromium-without-snap

# Add debian buster
cat > /etc/apt/sources.list.d/debian.list <<'EOF'
deb [arch=amd64 signed-by=/usr/share/keyrings/debian-buster.gpg] http://deb.debian.org/debian buster main
deb [arch=amd64 signed-by=/usr/share/keyrings/debian-buster-updates.gpg] http://deb.debian.org/debian buster-updates main
deb [arch=amd64 signed-by=/usr/share/keyrings/debian-security-buster.gpg] http://deb.debian.org/debian-security buster/updates main
EOF

# Add keys
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys DCC9EFBF77E11517
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 648ACFD622F3D138
apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 112695A0E562B32A

apt-key export 77E11517 | gpg --dearmour -o /usr/share/keyrings/debian-buster.gpg
apt-key export 22F3D138 | gpg --dearmour -o /usr/share/keyrings/debian-buster-updates.gpg
apt-key export E562B32A | gpg --dearmour -o /usr/share/keyrings/debian-security-buster.gpg

# Prefer debian repo for chromium* packages only
# Note the double-blank lines between entries
cat > /etc/apt/preferences.d/chromium.pref << 'EOF'
Package: *
Pin: release a=eoan
Pin-Priority: 500


Package: *
Pin: origin "deb.debian.org"
Pin-Priority: 300


Package: chromium*
Pin: origin "deb.debian.org"
Pin-Priority: 700
EOF

# Install chromium and chromium-driver
apt-get update
apt-get install chromium chromium-driver


// After that, Run the below commands on bash
!pip install --upgrade pip
!pip install -U selenium
!pip install -U webdriver-manager


// We changed to use firefox, instead of chrome on google-colab-research,
// because chrome arises TimoutException continuously. 
// No solution at the moment.


** Daemonize JupyterLab
https://www.vultr.com/docs/how-to-set-up-a-jupyterlab-environment-on-ubuntu-22-04/

1. sudo systemctl start jupyterlab

2. find google-chrome path
	whereis google-chrome-stable
2. Enable chrome to open a port for remote debugging.
https://cosmocode.io/how-to-connect-selenium-to-an-existing-browser-that-was-opened-manually/
	google-chrome-stable --remote-debugging-port=9222 --user-data-dir="~/ChromeProfile"