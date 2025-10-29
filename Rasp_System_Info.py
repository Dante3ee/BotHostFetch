import platform
import psutil
import socket
import subprocess
import datetime
import re


def get_CPU_temperature():
    try:
        out = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        return re.search(r"temp=([\d.]+)", out).group(1) + "°C"
    except Exception:
        return "N/A"


def get_throttled():
    """Throttling state (overheat / low power)"""
    try:
        out = subprocess.check_output(["vcgencmd", "get_throttled"]).decode().strip()
        code = int(out.split("=")[1], 16)
        flags = {
            0x1: "Under-voltage",
            0x2: "CPU frequency reduced",
            0x4: "Throttling active",
            0x8: "GPU frequency reduced",
            0x10000: "Under-voltage (occurred)",
            0x20000: "Throttling (occurred)",
            0x40000: "CPU frequency reduced (occurred)",
            0x80000: "GPU frequency reduced (occurred)",
        }
        return ", ".join(v for k, v in flags.items() if code & k) or "OK"
    except Exception:
        return "N/A"


def get_network():
    ip_local = socket.gethostbyname(socket.gethostname())
    try:
        ip_public = subprocess.check_output(
            ["curl", "-s", "ifconfig.me"]
        ).decode().strip()
    except Exception:
        ip_public = "N/A"
    interfaces = psutil.net_if_addrs()
    return {"ip_local": ip_local, "ip_public": ip_public, "interfaces": list(interfaces.keys())}


def get_system_info():
    uname = platform.uname()
    cpu_temp = get_CPU_temperature()
    throttled = get_throttled()

    cpu_freq = psutil.cpu_freq()
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    uptime_seconds = (datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds()
    uptime = str(datetime.timedelta(seconds=int(uptime_seconds)))

    net = get_network()

    try:
        model = subprocess.check_output(["cat", "/proc/device-tree/model"]).decode().strip()
    except Exception:
        model = "Unknown Model"

    info = {
        "Model": model,
        "OS": f"{uname.system} {uname.release}",
        "Kernel": uname.version.split()[0],
        "Architecture": uname.machine,
        "CPU Usage": f"{cpu_usage}%",
        "CPU Freq": f"{cpu_freq.current:.1f} MHz" if cpu_freq else "N/A",
        "Temperature": cpu_temp,
        "Power/Throttling": throttled,
        "RAM": f"{ram.percent}% ({ram.used // (1024**2)} Mo / {ram.total // (1024**2)} Mo)",
        "Disk": f"{disk.percent}% ({disk.used // (1024**3)} Go / {disk.total // (1024**3)} Go)",
        "Uptime": uptime,
        "Hostname": socket.gethostname(),
        "Local IP": net["ip_local"],
        "Public IP": net["ip_public"],
        "Interfaces": ", ".join(net["interfaces"]),
    }
    return info


def print_sysinfo():
    info = get_system_info()
    longest = max(len(k) for k in info.keys())
    for k, v in info.items():
        print(f"{k:<{longest}} : {v}")


if __name__ == "__main__":
    print_sysinfo()
