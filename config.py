#!/usr/bin/env python3

import os
import json
import shutil
from dataclasses import dataclass, asdict, field


def find_terminal():
    terminals = [
        'xdg-terminal', 'x-terminal-emulator', 'kitty',
        'gnome-terminal', 'konsole', 'xfce4-terminal',
        'alacritty', 'xterm'
    ]
    for term in terminals:
        if shutil.which(term):
            print(f"{term} found")
            return term
    raise RuntimeError("No terminal emulator found.")


def is_yay_installed() -> bool:
    return shutil.which("yay") is not None


def is_paru_installed() -> bool:
    return shutil.which("paru") is not None


def is_flatpak_installed() -> bool:
    return shutil.which("flatpak") is not None


def get_aur_update_command():
    if is_yay_installed():
        return "yay"
    elif is_paru_installed():
        return "paru"

    return None


@dataclass
class Config:
    terminal: str = find_terminal()

    update_aur : bool = is_yay_installed() or is_paru_installed()
    update_flatpak : bool = is_flatpak_installed()

    aur_helper : str = get_aur_update_command()

    _path: str = field(default=os.path.expanduser("~/.config/updates-notifications/config.json"), init=False)

    def __post_init__(self):
        """Automatically load config data from file on init."""
        data = self._load_from_file()
        if data:
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        else:
            self._save()

    def _load_from_file(self):
        """Try to load config from user or system file."""
        if os.path.isfile(self._path):
            try:
                with open(self._path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config from {self._path}: {e}")
        return {}

    def _save(self):
        """Save current config to the user config path."""
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, 'w') as f:
            json.dump(asdict(self), f, indent=4)
        print(f"Config saved to {self._path}")

    def show(self):
        print(f"Config loaded from: {self._path}")
        print(json.dumps(asdict(self), indent=4))

