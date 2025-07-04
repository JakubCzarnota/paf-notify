import subprocess
import time
import gi

from config import Config
from updates import Updates

gi.require_version("Notify", "0.7")
from gi.repository import Notify, GObject, GLib

check_again_time = 60 * 15 # check every 15 minutes
remind_later_time = 60 * 60 # 1 hour

loop = GLib.MainLoop()

config = Config()
config.show()

updates = Updates(config)

def on_closed(notification, data=None):
    print("Closed")
    loop.quit()

    time.sleep(remind_later_time)


def create_update_command():
    command = []

    if updates.get_pacman_updates_amount() > 0:
        command.append('read -p "Update with pacman? [Y/n] " p; p=${p:-y}')

    if config.update_aur and updates.get_aur_updates_amount() > 0:
        command.append(f'read -p "Update with {config.aur_helper} (AUR)? [Y/n] "; ' + 'y=${y:-y}')

    if config.update_flatpak and updates.get_flatpak_updates_amount() > 0:
        command.append('read -p "Update with flatpak? [Y/n] " f; f=${f:-y}')

    if updates.get_pacman_updates_amount() > 0:
        command.append('[[ $p =~ ^[Yy]$ ]] && echo "updating with pacman" && sudo pacman -Syu --noconfirm')

    if config.update_aur and updates.get_aur_updates_amount() > 0:
        command.append(f'[[ $y =~ ^[Yy]$ ]] && echo "updating with {config.aur_helper}" && {config.aur_helper} -Sua --noconfirm')

    if config.update_flatpak and updates.get_flatpak_updates_amount() > 0:
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

def create_updates_list_command():
    command = []

    if updates.get_pacman_updates_amount():
        command.append(f'echo "pacman updates: \n{updates.pacman_updates}"')

    if config.update_aur and updates.get_aur_updates_amount() > 0:
        command.append(f'echo "{config.aur_helper} (AUR) updates: \n{updates.aur_updates}"')

    if config.update_flatpak and updates.get_flatpak_updates_amount() > 0:
        command.append(f'echo "flatpak updates: \n{updates.flatpak_updates}"')

    command.append('read -p "Press Enter to continue..."')

    return " ; ".join(command)

def on_updates_list(notification, action, data=None):
    updates_list_command = create_updates_list_command()

    subprocess.Popen([config.terminal, "-e", "bash", "-c", updates_list_command]).wait()

    print("Updates listed")

    loop.quit()

def on_remind_later(notification, action, data=None):
        loop.quit()

        print("Remind later")

        time.sleep(remind_later_time)

def create_notification():
        update_message = []

        if updates.get_pacman_updates_amount() > 0:
            update_message.append(f'pacman ({updates.get_pacman_updates_amount()})')

        if updates.get_aur_updates_amount() > 0:
            update_message.append(f'AUR ({updates.get_aur_updates_amount()})')

        if updates.get_flatpak_updates_amount() > 0:
            update_message.append(f'flatpak ({updates.get_flatpak_updates_amount()})')

        update_message = ', '.join(update_message)

        n = Notify.Notification.new(f"Updates available: {updates.get_updates_amount()}", update_message,
                                    "system-software-update")

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

def main():
    Notify.init("Update checker")

    while True:

        print("Checking for updates")

        updates.check_for_updates()

        if updates.get_updates_amount() > 0:
            n = create_notification()
            n.show()
            loop.run()
        else:
            print("no updates")
            time.sleep(check_again_time)

if __name__ == "__main__":
    main()
