# L Chat

A small chatbot app built with Python and Pygame, styled after a messaging interface. It's a personal project I made for fun while learning how to work with UI animations in Pygame.

Still a work in progress — things might break, change, or get added without much notice.

---

## Features

- Chat-style interface with message bubbles
- Typing indicator animation
- Custom bot responses loaded from a text file
- Heart animations triggered by certain messages
- Scrollable message history
- Lofi background music
- Pink menu screen with credits

---

## Requirements

```bash
pip install pygame
```

---

## How to Run

```bash
python menu.py
```

---

## How It Works

Bot responses are stored in `bot_responses.txt`. Each line follows this format:

```
trigger1|trigger2 ... Bot reply here
```

The bot matches your message against the triggers and returns the corresponding reply. If nothing matches, it falls back to a default response.

---

## Project Structure

```
L_chatbot/
├── menu.py            # Main entry point — launches the menu
├── main.py            # Chat screen
├── bot_responses.txt  # Bot response definitions
├── avatar.jpg         # L Lawliet avatar
├── bg.png             # Chat background image
├── favicon.png        # Window icon
└── lofi.wav           # Background music
```

---

## Planned

- More bot responses
- Smarter message matching
- New visual effects
- General polish

---

## Credits

- Music by [Niobium Face](https://niobiumfafce.itch.io/free-lofi-music-pack-15-full-songs-royalty-free-lofi-music) — free lofi music pack, royalty free
- Built with [Python](https://www.python.org/) and [Pygame](https://www.pygame.org/)

---

Made by Spouuu
