import subprocess
import time
import gi

from config import Config

gi.require_version("Notify", "0.7")
from gi.repository import Notify, GObject, GLib

check_again_time = 60 * 15 # check every 15 minutes
remind_later_time = 60 * 60 # 1 hour

loop = GLib.MainLoop()

config = Config()

config.show()

def on_closed(notification, data=None):
    print("Closed")
    loop.quit()

    time.sleep(remind_later_time)


def create_update_command():
    command = []

    command.append('read -p "Update with pacman? [Y/n] " p; p=${p:-y}')

    if config.update_aur:
        command.append('read -p "Update with yay (AUR)? [Y/n] " y; y=${y:-y}')

    if config.update_flatpak:
        command.append('read -p "Update with flatpak? [Y/n] " f; f=${f:-y}')

    command.append('[[ $p =~ ^[Yy]$ ]] && echo "updating with pacman" && sudo pacman -Syu --noconfirm')

    if config.update_aur:
        command.append('[[ $y =~ ^[Yy]$ ]] && echo "updating with yay" && yay -Sua --noconfirm')

    if config.update_flatpak:
        command.append('[[ $f =~ ^[Yy]$ ]] && echo "updating with flatpak" && flatpak update --assumeyes')

    command.append('read -p "Press Enter to continue..."')

    return " ; ".join(command)


def on_update(notification, action, data=None):
    update_command = create_update_command()

    print(config.terminal)
    print(update_command)

    subprocess.Popen([config.terminal, "-e", "bash", "-c", update_command]).wait()


    print("Updated")

    loop.quit()

    time.sleep(check_again_time)

def on_updates_list(notification, action, data=None):
    subprocess.Popen([config.terminal, "-e", "bash", "-c", 'echo "Pacman updates:" ; checkupdates ; echo "AUR updates:" ; yay -Qua ; echo "Flatpak updates:" ; flatpak remote-ls --updates ; read -p "Press Enter to continue..."']).wait()

    print("Updates listed")

    loop.quit()

    #time.sleep(60 * 5)

def on_remind_later(notification, action, data=None):
    loop.quit()

    print("Remind later")

    time.sleep(remind_later_time)

def create_notification(pacman_updates, aur_updates, flatpak_updates):
    all_updates_amount =  pacman_updates + aur_updates + flatpak_updates

    n = Notify.Notification.new(f"Updates available: {all_updates_amount}", f"pacman ({pacman_updates}), AUR ({aur_updates}), flatpak ({flatpak_updates})", "system-software-update" )

    n.connect("closed", on_closed)

    n.set_timeout(2147483647)

    n.add_action("update",  # action name
                 "Update now",  # button label
                 on_update,  # callback
                 None)  # user data

    n.add_action("updates list",  # action name
                 "Updates list",  # button label
                 on_updates_list,  # callback
                 None)  # user data

    n.add_action("remind later",  # action name
                 "Remind later",  # button label
                 on_remind_later,  # callback
                 None)  # user data

    return n

def get_pacman_updates():
    try:
        output = subprocess.check_output(["checkupdates"], text=True)
        return output.count('\n')
    except subprocess.CalledProcessError:
        return 0

def get_aur_updates():
    try:
        output = subprocess.check_output(["yay", "-Qua"], text=True)
        return output.count('\n')
    except subprocess.CalledProcessError:
        return 0

def get_flatpak_updates():
        try:
            output = subprocess.check_output(["flatpak", "remote-ls", "--updates"], text=True)
            return output.count('\n')
        except subprocess.CalledProcessError:
            return 0

def main():
    Notify.init("Update checker")
    while True:

        print("Checking updates")
        pacman_updates = get_pacman_updates()
        aur_updates = get_aur_updates()
        flatpak_updates = get_flatpak_updates()

        if (pacman_updates + aur_updates + flatpak_updates) > 0:
            n = create_notification(pacman_updates, aur_updates, flatpak_updates)
            n.show()
            loop.run()
        else:
            print("no updates")
            time.sleep(check_again_time)

if __name__ == "__main__":
    main()
