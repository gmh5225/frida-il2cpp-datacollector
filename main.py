import frida
import threading
import time
import sys
import json
from define import OS, MODE
import mono_pipeserver as monopipe

with open("config.json") as f:
    config = json.loads(f.read())


def get_device():
    mgr = frida.get_device_manager()
    changed = threading.Event()

    def on_changed():
        changed.set()

    mgr.on("changed", on_changed)

    device = None
    while device is None:
        devices = [dev for dev in mgr.enumerate_devices() if dev.type == "usb"]
        if len(devices) == 0:
            print("Waiting for usb device...")
            changed.wait()
        else:
            device = devices[0]

    mgr.off("changed", on_changed)
    return device


def main(package, pid=None):
    targetOS = config["targetOS"]
    mode = config["mode"]
    frida_server_ip = config["frida_server_ip"]

    if targetOS in [OS.ANDROID.value, OS.IOS.value]:
        if frida_server_ip != "":
            device = frida.get_device_manager().add_remote_device(frida_server_ip)
        else:
            device = get_device()
        if pid == None:
            apps = device.enumerate_applications()
            target = package
            for app in apps:
                if target == app.identifier or target == app.name:
                    app_identifier = app.identifier
                    app_name = app.name
                    break
            if mode == MODE.SPAWN.value:
                process_id = device.spawn([app_identifier])
                session = device.attach(process_id)
                device.resume(process_id)
                time.sleep(1)
            else:
                session = device.attach(app_name)
        else:
            session = device.attach(pid)
    else:
        if frida_server_ip != "":
            device = frida.get_device_manager().add_remote_device(frida_server_ip)
        else:
            device = frida.get_remote_device()
        if pid == None:
            processes = device.enumerate_processes()
            target = package
            for process in processes:
                if target == str(process.pid) or target == process.name:
                    process_name = process.name
                    process_id = process.pid
                    break
            session = device.attach(process_id)
        else:
            session = device.attach(pid)

    def on_message(message, data):
        print(message)

    if targetOS in [OS.ANDROID.value, OS.IOS.value]:
        print("monoDissect Enabled!")
        time.sleep(5)

        monopipe.pipeserver(session)
    else:
        print("TargetOS Not Supported!")


if __name__ == "__main__":
    args = sys.argv
    target = config["target"]
    if target == "":
        if args[1] == "-p" or args[1] == "--pid":
            pid = int(args[2])
            main(None, pid)
        else:
            main(args[1])
    else:
        main(target)
