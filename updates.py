import subprocess

from config import Config


class Updates:
    pacman_updates : str = ""
    aur_updates : str = ""
    flatpak_updates : str = ""

    config : Config

    def __init__(self, config : Config):
        self.config = config

    def check_for_updates(self):
        self.pacman_updates = self._get_pacman_updates()

        if self.config.update_aur:
            self.aur_updates = self._get_aur_updates()

        if self.config.update_flatpak:
            self.flatpak_updates = self._get_flatpak_updates()

    def _get_pacman_updates(self):
        try:
            output = subprocess.check_output(["checkupdates"], text=True)
            return output
        except subprocess.CalledProcessError:
            return ""

    def _get_aur_updates(self):
        try:
            output = subprocess.check_output([self.config.aur_helper, "-Qua"], text=True)
            return output
        except subprocess.CalledProcessError:
            return ""

    def _get_flatpak_updates(self):
        try:
            output = subprocess.check_output(["flatpak", "remote-ls", "--updates"], text=True)
            return output
        except subprocess.CalledProcessError:
            return ""

    def get_updates_amount(self):
        return self.get_pacman_updates_amount() + self.get_aur_updates_amount() + self.get_flatpak_updates_amount()

    def get_pacman_updates_amount(self):
        return self.pacman_updates.count('\n')

    def get_aur_updates_amount(self):
        return self.aur_updates.count('\n')

    def get_flatpak_updates_amount(self):
        return self.flatpak_updates.count('\n')
