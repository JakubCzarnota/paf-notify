# paf-notify

**paf-notify** is a lightweight desktop notification daemon for Arch Linux that alerts you when there are pending updates for:

- Pacman (official repositories)  
- AUR (via `yay` or `paru`)  
- Flatpak  

It shows a notification with buttons to **update now**, **list available updates**, or **remind later**.

---

## ✨ Features

- Periodic background checks (default: every 15 minutes)
- Interactive terminal-based update prompts
- Smart detection of AUR helpers and terminal emulators
- Flatpak support
- User-friendly configuration stored in JSON

---

## 📦 Installation

### From the AUR (recommended)

```bash
yay -S paf-notify
# or
paru -S paf-notify
```

### From source 

```bash
git clone https://github.com/JakubCzarnota/paf-notify.git
cd paf-notify
makepkg -si
```
