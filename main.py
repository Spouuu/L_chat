import pygame
import sys
import os
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("L chat")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

FONT = pygame.font.SysFont("Georgia", 22)
TITLE_FONT = pygame.font.SysFont("arial", 40, bold=True)
SUBTITLE_FONT = pygame.font.SysFont("arial", 20, italic=True)
TYPING_FONT = pygame.font.SysFont("arial", 18, italic=True)
CLOCK = pygame.time.Clock()

BG_COLOR = (255, 240, 245)
TEXT = (80, 70, 80)
BOX = (255, 255, 255)
BOX_BORDER = (255, 182, 193)
USER_BUBBLE = (255, 204, 213)
BOT_BUBBLE = (255, 255, 255)

HEADER_HEIGHT = 185
INPUT_HEIGHT = 80
CHAT_TOP = HEADER_HEIGHT + 10
CHAT_BOTTOM = HEIGHT - INPUT_HEIGHT
CHAT_AREA_HEIGHT = CHAT_BOTTOM - CHAT_TOP
BUBBLE_PADDING_X = 15
BUBBLE_PADDING_Y = 10
BUBBLE_GAP = 14
MAX_BUBBLE_WIDTH = 580

messages = []
input_text = ""
scroll_offset = 0
scroll_target = 0
auto_scroll = True

hearts = []

LOVE_TRIGGERS = [
    "love you", "i love you", "love u", "luv u",
    "i love you so much", "i really love you"
]

def spawn_hearts():
    for _ in range(22):
        hearts.append({
            "x": random.randint(60, WIDTH - 60),
            "y": HEIGHT + random.randint(0, 80),
            "vy": random.uniform(1.8, 3.5),
            "vx": random.uniform(-0.6, 0.6),
            "size": random.randint(16, 36),
            "alpha": 255,
            "wobble_offset": random.uniform(0, math.pi * 2),
            "wobble_speed": random.uniform(0.04, 0.09),
            "age": 0,
            "lifetime": random.randint(120, 200),
            "color": random.choice([
                (255, 105, 135),
                (255, 150, 170),
                (255, 80, 110),
                (255, 182, 193),
                (220, 80, 120),
            ]),
        })

try:
    _icon = pygame.image.load(resource_path("favicon.png")).convert_alpha()
    pygame.display.set_icon(_icon)
    favicon_bar = pygame.transform.smoothscale(_icon, (36, 36))
except:
    favicon_bar = None

try:
    avatar = pygame.image.load(resource_path("avatar.jpg")).convert_alpha()
    avatar = pygame.transform.smoothscale(avatar, (130, 130))
    def round_avatar(image, radius=65):
        size = image.get_size()
        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, size[0], size[1]), border_radius=radius)
        rounded = pygame.Surface(size, pygame.SRCALPHA)
        rounded.blit(image, (0, 0))
        rounded.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return rounded
    avatar = round_avatar(avatar, 65)
except:
    def round_avatar(image, radius=65):
        size = image.get_size()
        mask = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255), (0, 0, size[0], size[1]), border_radius=radius)
        rounded = pygame.Surface(size, pygame.SRCALPHA)
        rounded.blit(image, (0, 0))
        rounded.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return rounded
    avatar = pygame.Surface((130, 130), pygame.SRCALPHA)
    pygame.draw.circle(avatar, BOX_BORDER, (65, 65), 65)

try:
    background = pygame.image.load(resource_path("bg.png")).convert()
    background = pygame.transform.smoothscale(background, (WIDTH, HEIGHT))
    has_bg = True
except:
    has_bg = False

# Load sounds
try:
    pygame.mixer.init()
    send_sound = pygame.mixer.Sound(resource_path("send.wav"))
except:
    send_sound = None

try:
    pygame.mixer.init()
    receive_sound = pygame.mixer.Sound(resource_path("receive.wav"))
except:
    receive_sound = None

input_box = pygame.Rect(20, HEIGHT - INPUT_HEIGHT + 10, WIDTH - 40, 60)

typing = False
typing_start_time = 0
typing_delay = 1200

def normalize(text):
    return text.lower().strip()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_responses():
    data = []
    path = resource_path("bot_responses.txt")
    if not os.path.exists(path):
        return [(["hi", "hello", "hey"], "Hello there!")]
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "|" not in line:
                continue
            parts = line.split("|")
            triggers = [normalize(t) for t in parts[:-1]]
            response = parts[-1]
            data.append((triggers, response))
    return data

responses = load_responses()

def is_love_message(user_msg):
    msg = normalize(user_msg)
    return any(trigger in msg for trigger in LOVE_TRIGGERS)

def get_bot_reply(user_msg):
    user_msg = normalize(user_msg)
    best_match = None
    best_len = -1
    for triggers, response in responses:
        for trigger in triggers:
            trigger = normalize(trigger)
            if trigger == user_msg:
                return response
            if trigger in user_msg and len(trigger) > best_len:
                best_len = len(trigger)
                best_match = response
    if best_match:
        return best_match
    return "Hm... I see!"

def start_typing():
    global typing, typing_start_time
    typing = True
    typing_start_time = pygame.time.get_ticks()

def finish_reply(user_msg):
    global typing, auto_scroll
    raw = get_bot_reply(user_msg)
    if "..." in raw:
        after = raw.split("...", 1)[1].strip()
        msg = after if after else raw
    else:
        msg = raw
    messages.append(("bot", msg))
    typing = False
    auto_scroll = True
    if receive_sound:
        receive_sound.play()
    if is_love_message(user_msg):
        spawn_hearts()

def update_hearts():
    global hearts
    for h in hearts:
        h["age"] += 1
        h["y"] -= h["vy"]
        h["x"] += h["vx"] + math.sin(h["age"] * h["wobble_speed"] + h["wobble_offset"]) * 0.5
        fade_start = h["lifetime"] * 0.6
        if h["age"] > fade_start:
            h["alpha"] = max(0, int(255 * (1 - (h["age"] - fade_start) / (h["lifetime"] - fade_start))))
    hearts = [h for h in hearts if h["age"] < h["lifetime"]]

def draw_heart(surface, x, y, size, color, alpha):
    heart_surf = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
    cx, cy = size + 2, size + 2
    r = size // 2
    pygame.draw.circle(heart_surf, (*color, alpha), (cx - r, cy - r // 2), r)
    pygame.draw.circle(heart_surf, (*color, alpha), (cx + r, cy - r // 2), r)
    points = [
        (cx - size, cy - r // 2),
        (cx + size, cy - r // 2),
        (cx, cy + size),
    ]
    pygame.draw.polygon(heart_surf, (*color, alpha), points)
    surface.blit(heart_surf, (int(x) - size - 2, int(y) - size - 2))

def draw_hearts():
    for h in hearts:
        draw_heart(screen, h["x"], h["y"], h["size"], h["color"], h["alpha"])

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        test = (current + " " + word).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines if lines else [""]

def bubble_height_for(text):
    lines = wrap_text(text, FONT, MAX_BUBBLE_WIDTH - BUBBLE_PADDING_X * 2)
    return FONT.get_linesize() * len(lines) + BUBBLE_PADDING_Y * 2

def compute_total_content_height():
    total = sum(bubble_height_for(msg) + BUBBLE_GAP for _, msg in messages)
    if typing:
        total += FONT.get_linesize() + BUBBLE_GAP
    return total

def draw_bubble(surface, sender, msg, y):
    lines = wrap_text(msg, FONT, MAX_BUBBLE_WIDTH - BUBBLE_PADDING_X * 2)
    line_h = FONT.get_linesize()
    text_w = max(FONT.size(l)[0] for l in lines)
    bw = min(text_w + BUBBLE_PADDING_X * 2, MAX_BUBBLE_WIDTH)
    bh = line_h * len(lines) + BUBBLE_PADDING_Y * 2
    if sender == "user":
        bx = WIDTH - bw - 20
        rect = pygame.Rect(bx, y, bw, bh)
        pygame.draw.rect(surface, USER_BUBBLE, rect, border_radius=18)
        for i, line in enumerate(lines):
            surface.blit(FONT.render(line, True, TEXT), (bx + BUBBLE_PADDING_X, y + BUBBLE_PADDING_Y + i * line_h))
    else:
        bx = 20
        rect = pygame.Rect(bx, y, bw, bh)
        pygame.draw.rect(surface, BOT_BUBBLE, rect, border_radius=18)
        pygame.draw.rect(surface, BOX_BORDER, rect, 2, border_radius=18)
        for i, line in enumerate(lines):
            surface.blit(FONT.render(line, True, TEXT), (bx + BUBBLE_PADDING_X, y + BUBBLE_PADDING_Y + i * line_h))
    return bh

def draw():
    global scroll_offset, scroll_target, auto_scroll

    total_h = compute_total_content_height()
    max_scroll = max(0, total_h - CHAT_AREA_HEIGHT)

    if auto_scroll:
        scroll_target = max_scroll

    scroll_target = max(0, min(scroll_target, max_scroll))
    scroll_offset += (scroll_target - scroll_offset) * 0.18
    scroll_offset = max(0, min(scroll_offset, max_scroll))

    if has_bg:
        screen.blit(background, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 160))
        screen.blit(overlay, (0, 0))
    else:
        screen.fill(BG_COLOR)

    pygame.draw.circle(screen, (255, 255, 255), (100, 100), 68)
    pygame.draw.circle(screen, BOX_BORDER, (100, 100), 68, 3)
    screen.blit(avatar, (35, 35))
    screen.blit(TITLE_FONT.render("L Lawliet", True, TEXT), (190, 50))
    pygame.draw.circle(screen, (144, 238, 144), (200, 110), 6)
    screen.blit(SUBTITLE_FONT.render("Online", True, (120, 110, 120)), (215, 98))

    esc_font = pygame.font.SysFont("arial", 13, italic=True)
    esc_surf = esc_font.render("ESC — menu", True, (200, 160, 175))
    screen.blit(esc_surf, (WIDTH - esc_surf.get_width() - 16, 10))

    pygame.draw.line(screen, BOX_BORDER, (20, HEADER_HEIGHT - 2), (WIDTH - 20, HEADER_HEIGHT - 2), 2)

    screen.set_clip(pygame.Rect(0, CHAT_TOP, WIDTH, CHAT_AREA_HEIGHT))

    y = CHAT_TOP - scroll_offset
    if total_h < CHAT_AREA_HEIGHT:
        y = CHAT_BOTTOM - total_h

    for sender, msg in messages:
        h = bubble_height_for(msg)
        if y + h > CHAT_TOP and y < CHAT_BOTTOM:
            draw_bubble(screen, sender, msg, int(y))
        y += h + BUBBLE_GAP

    if typing and y < CHAT_BOTTOM:
        screen.blit(TYPING_FONT.render("L is typing...", True, (160, 150, 160)), (35, int(y)))

    screen.set_clip(None)
    draw_hearts()

    if max_scroll > 0:
        bar_h = max(30, int(CHAT_AREA_HEIGHT * CHAT_AREA_HEIGHT / total_h))
        scroll_frac = scroll_offset / max_scroll
        bar_y = CHAT_TOP + int((CHAT_AREA_HEIGHT - bar_h) * scroll_frac)
        pygame.draw.rect(screen, (255, 220, 228), pygame.Rect(WIDTH - 10, CHAT_TOP, 6, CHAT_AREA_HEIGHT), border_radius=3)
        pygame.draw.rect(screen, BOX_BORDER, pygame.Rect(WIDTH - 10, bar_y, 6, bar_h), border_radius=3)

    pygame.draw.rect(screen, BOX, input_box, border_radius=20)
    pygame.draw.rect(screen, BOX_BORDER, input_box, 3, border_radius=20)
    display_text = input_text + ("|" if pygame.time.get_ticks() % 1000 < 500 else "")
    screen.blit(FONT.render(display_text, True, TEXT), (input_box.x + 20, input_box.y + 16))

    pygame.display.flip()

def main():
    global input_text, scroll_offset, scroll_target, auto_scroll, messages, hearts, typing

    messages = []
    hearts = []
    input_text = ""
    scroll_offset = 0
    scroll_target = 0
    auto_scroll = True
    typing = False

    last_user_msg = ""

    while True:
        CLOCK.tick(60)
        now = pygame.time.get_ticks()

        update_hearts()

        if typing and now - typing_start_time > typing_delay:
            finish_reply(last_user_msg)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEWHEEL:
                max_scroll = max(0, compute_total_content_height() - CHAT_AREA_HEIGHT)
                scroll_target -= event.y * 35
                scroll_target = max(0, min(scroll_target, max_scroll))
                auto_scroll = (scroll_target >= max_scroll)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

                elif event.key == pygame.K_RETURN:
                    if input_text.strip() and not typing:
                        messages.append(("user", input_text.strip()))
                        last_user_msg = input_text
                        if send_sound:
                            send_sound.play()
                        start_typing()
                        input_text = ""
                        auto_scroll = True

                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]

                elif event.key == pygame.K_UP:
                    max_scroll = max(0, compute_total_content_height() - CHAT_AREA_HEIGHT)
                    scroll_target = max(scroll_target - 40, 0)
                    auto_scroll = False

                elif event.key == pygame.K_DOWN:
                    max_scroll = max(0, compute_total_content_height() - CHAT_AREA_HEIGHT)
                    scroll_target = min(scroll_target + 40, max_scroll)
                    auto_scroll = (scroll_target >= max_scroll)

                else:
                    if len(input_text) < 80:
                        input_text += event.unicode

        draw()

if __name__ == "__main__":
    main()