echo "[Unit]
Description=Network test
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /root/network_test.py

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/network_test.service
systemctl start network_test.service
systemctl enable network_test.service