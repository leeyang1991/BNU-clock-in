
echo "[Unit]
Description=Network test
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /root/network_test.py

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/network_test.service

wget https://raw.githubusercontent.com/leeyang1991/BNU-clock-in/refs/heads/master/multiple_server_ping.py -O /root/network_test.py

systemctl restart network_test.service
systemctl enable network_test.service
systemctl status network_test.service
systemctl stop network_test.service
systemctl start network_test.service

journalctl -ru network_test.service