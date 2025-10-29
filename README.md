# BotHostFetch — Discord host monitoring & control

BotHostFetch is a lightweight, secure, and extensible Discord bot that lets you **monitor** and **control** your hosts (Raspberry Pi and Windows) from a Discord server. It provides system stats (CPU, RAM, disk, temperature, network info) and safe admin actions (update, reboot) with owner-only protection.

## Features
- Cross-platform support: Raspberry Pi (Linux) and Windows detection
- Real-time system info: CPU usage, CPU frequency, RAM, disk, uptime
- Raspberry-specific metrics: CPU temperature, throttling, model, local & public IP
- Interactive Discord UI: buttons for refresh, update, and reboot
- Owner-only controls and optional ownership protection toggle
- Easy to run as a systemd service on Raspberry Pi
- Small, dependency-light Python codebase

## Quickstart

1. Clone the repo:
```bash
git clone https://github.com/your-username/BotHostFetch.git
cd BotHostFetch
```
2. Make sure config.json exists in the repo root. Example structure:
```json
{
  "token": "YOUR!BOT!TOKEN",
  "owner_id": "YOUR!ID"
}
```
3. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
4. Run locally:
```bash
python BotHostFetch.py
```
5. (Optional) Run as a systemd service on Raspberry Pi:
```bash
sudo cp bothostfetch.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable bothostfetch
sudo systemctl start bothostfetch
```

# Security & sudo rights

To allow safe commands (update, reboot) without a password, add a limited sudoers entry (replace <user> with your system username):
```bash
sudo visudo
# add the following line:
<user> ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/apt-get, /sbin/reboot
```
Do not use NOPASSWD: ALL — it grants full root access.
Limit sudo only to the commands your bot needs.
pls
