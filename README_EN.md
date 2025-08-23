
# MikroTik WiFi Clients Dashboard

## Description

This application is designed for centralized display of all devices connected via WiFi in the MikroTik infrastructure using CAPsMAN controller and DHCP server.  
An extended WiFi clients table is generated based on data from two MikroTik routers (one is the DHCP server, the other is the CAPsMAN controller) and is served via a web interface (Flask).

The application supports periodic information updates with a configurable interval. Connection parameters and update interval can be specified via environment variables or command line arguments.

***

## Features

- Obtain the current list of WiFi clients, their IP addresses, MAC addresses, binding to access points (AP) - SSID, interface, signal level
- Correct matching of data by MAC address between DHCP and CAPsMAN
- Display information as an HTML table on a web page
- Configurable data update interval (default 30 seconds)
- Simple integration and running in a Docker container

***

## Requirements

- Python 3.8+
- Two MikroTik devices with enabled API (DHCP server and CAPsMAN controller)
- Availability of MikroTik API ports (8728 by default)
- Docker (for containerization, optional)

***

## Installation and Running

### 1. Clone the repository and navigate to its directory
```
git clone https://github.com/Sharptop77/wifi-device-list.git
cd wifi-device-list
```
***

### 2. Prepare environment variables (or use arguments):

- `DHCP_MIKROTIK_HOST` — IP of DHCP MikroTik
- `DHCP_MIKROTIK_USER` — DHCP MikroTik login
- `DHCP_MIKROTIK_PASS` — DHCP MikroTik password
- `CAPSMAN_MIKROTIK_HOST` — IP of CAPsMAN MikroTik
- `CAPSMAN_MIKROTIK_USER` — CAPsMAN MikroTik login
- `CAPSMAN_MIKROTIK_PASS` — CAPsMAN MikroTik password
- `UPDATE_INTERVAL` — Update interval (seconds, default 30)

***

### 3. Run via Docker

Build and run the container:
```bash
docker build -t mikrotik_wifi_app .

docker run -d -p 8080:8080 
-e DHCP_MIKROTIK_HOST=192.168.88.1 
-e DHCP_MIKROTIK_USER=admin 
-e DHCP_MIKROTIK_PASS=adminpass 
-e CAPSMAN_MIKROTIK_HOST=192.168.88.2 
-e CAPSMAN_MIKROTIK_USER=admin 
-e CAPSMAN_MIKROTIK_PASS=adminpass 
-e UPDATE_INTERVAL=30 
–name mikrotik_wifi_container mikrotik_wifi_app
```

After starting, the interface will be available at:  

http://localhost:8080

***

### 4. Run locally (without Docker)

Create a virtual environment, install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the application (example with arguments):
```bash
python app.py \
–dhcp-host 192.168.88.1 –dhcp-user admin –dhcp-pass adminpass \
–capsman-host 192.168.88.2 –capsman-user admin –capsman-pass adminpass \
–update-interval 30 \
```
***

## Sample Table (What is displayed)

| Device Name       | IP Address | MAC Address | AP Interface | SSID    | Device Signal Level | Access Point (Name)        | Access Point Address/Port |
|-------------------|------------|-------------|--------------|---------|---------------------|----------------------------|---------------------------|
| laptop-A          | ...        | ...         | cap1         | Mikrotik| -75                 | ... (Remote CAP identity)  | ...                       |
| ...               | ...        | ...         | ...          | ...     | ...                 | ...                        | ...                       |

***

## FAQ

**Q: How to change the update interval?**  
A: Use the environment variable `UPDATE_INTERVAL` or the parameter `--update-interval`.

**Q: How to find the correct values for environment variables?**  
A: These are the IP/login/password of your MikroTik devices with enabled API access.

**Q: Why does the connection fail?**  
A: Check firewall, correctness of API ports, availability of username and password, and that the chosen users have permission to work with the API.

***

## License

MIT 

***

## Contacts

For questions and suggestions — create an issue or send an email.

