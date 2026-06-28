import pygame
import sys
import math
import os

pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("L Chat")
CLOCK = pygame.time.Clock()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

try:
    _icon = pygame.image.load(resource_path("favicon.png"))
    pygame.display.set_icon(_icon)
    favicon_bar = pygame.transform.smoothscale(_icon.convert_alpha(), (36, 36))
except:
    favicon_bar = None
try:
    pygame.mixer.music.load(resource_path("lofi.wav"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except:
    pass

try:
    _icon = pygame.image.load(resource_path("favicon.png")).convert_alpha()
    pygame.display.set_icon(_icon)
except:
    pass

TITLE_FONT   = pygame.font.SysFont("georgia", 72, bold=True)
CREDITS_TITLE= pygame.font.SysFont("georgia", 32, bold=True)
SUBTITLE_FONT= pygame.font.SysFont("arial",   14, italic=True)
BTN_FONT     = pygame.font.SysFont("arial",   18)
CREDIT_FONT  = pygame.font.SysFont("georgia", 15, italic=True)

BG_TOP    = (255, 228, 236)
BG_BOT    = (255, 245, 250)
PANEL_BG  = (255, 248, 251)
PANEL_BDR = (244, 143, 177)
TITLE_CLR = (173, 20,  87)
SHADOW_CLR= (244, 143, 177)
SUB_CLR   = (240,  98, 146)
BTN_NORM  = (255, 240, 245)
BTN_HOV   = (252, 228, 236)
BTN_ACT   = (248, 187, 208)
BTN_BDR   = (233,  30, 140)
BTN_TXT   = (136,  14,  79)
PETAL_CLR = (252, 228, 236)
HEART_CLR = (233,  30, 140)
TEXT_MUTED= (176, 120, 150)


def gradient_bg(surface, c1, c2):
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(c1[0] + (c2[0]-c1[0])*t)
        g = int(c1[1] + (c2[1]-c1[1])*t)
        b = int(c1[2] + (c2[2]-c1[2])*t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def draw_rounded_rect(surface, color, rect, radius, border_color=None, border_w=0):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color and border_w:
        pygame.draw.rect(surface, border_color, rect, border_w, border_radius=radius)

def draw_petal(surface, cx, cy, w, h, angle, alpha=80):
    s = pygame.Surface((w*2, h*2), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (*PETAL_CLR, alpha), (0, 0, w*2, h*2))
    rotated = pygame.transform.rotate(s, angle)
    surface.blit(rotated, (cx - rotated.get_width()//2, cy - rotated.get_height()//2))

def draw_heart_small(surface, cx, cy, size, color, alpha=255):
    surf = pygame.Surface((size*3, size*3), pygame.SRCALPHA)
    r = size // 2
    sx, sy = size, size + r//2
    pygame.draw.circle(surf, (*color, alpha), (sx - r, sy - r//2), r)
    pygame.draw.circle(surf, (*color, alpha), (sx + r, sy - r//2), r)
    pts = [(sx - size, sy - r//2), (sx + size, sy - r//2), (sx, sy + size)]
    pygame.draw.polygon(surf, (*color, alpha), pts)
    surface.blit(surf, (cx - size, cy - size + r//2))

def text_centered(surface, font, text, cx, y, color):
    surf = font.render(text, True, color)
    surface.blit(surf, (cx - surf.get_width()//2, y))
    return surf.get_height()


class Button:
    def __init__(self, cx, cy, w, h, label, accent=False):
        self.rect = pygame.Rect(cx - w//2, cy - h//2, w, h)
        self.label = label
        self.accent = accent
        self.hovered = False
        self.pressed = False

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.pressed = True
            return True
        return False

    def draw(self, surface):
        if self.pressed:
            bg = BTN_ACT
        elif self.hovered:
            bg = BTN_HOV
        else:
            bg = (252, 228, 236) if self.accent else BTN_NORM
        draw_rounded_rect(surface, bg, self.rect, 40, BTN_BDR, 2)
        lbl = BTN_FONT.render(self.label, True, BTN_TXT)
        surface.blit(lbl, (self.rect.centerx - lbl.get_width()//2,
                            self.rect.centery - lbl.get_height()//2))


def credits_screen():
    lines = [
        ("title",  "L CHAT - Credits"),
        ("gap",    ""),
        ("header", "Game Design and Code <3"),
        ("body",   "Spouuu"),
        ("gap",    ""),
        ("header", "Inspiration <3"),
        ("body",   "L Lawliet - Death Note"),
        ("gap",    ""),
        ("header", "Music <3"),
        ("body", "Niobium Face"),
        ("body", "niobiumfafce.itch.io"),
        ("header", "Built with <3"),
        ("body",   "Pygame"),
        ("gap",    ""),
        ("hint",   "Press any key to return…"),
    ]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                return

        gradient_bg(screen, BG_TOP, BG_BOT)
        panel = pygame.Rect(220, 100, 460, 480)
        draw_rounded_rect(screen, PANEL_BG, panel, 22, PANEL_BDR, 2)

        for px, py in [(panel.left+28, panel.top+28),(panel.right-28, panel.top+28),
                       (panel.left+28, panel.bottom-28),(panel.right-28, panel.bottom-28)]:
            draw_heart_small(screen, px, py, 10, HEART_CLR, 140)

        y = 148
        for kind, text in lines:
            if kind == "gap":
                y += 14
            elif kind == "title":
                text_centered(screen, CREDITS_TITLE, text, WIDTH//2, y, TITLE_CLR)
                y += 48
                pygame.draw.line(screen, PANEL_BDR, (WIDTH//2-70, y-6), (WIDTH//2+70, y-6), 1)
                y += 6
            elif kind == "header":
                text_centered(screen, BTN_FONT, text, WIDTH//2, y, TITLE_CLR)
                y += 28
            elif kind == "body":
                text_centered(screen, CREDIT_FONT, text, WIDTH//2, y, (140, 60, 100))
                y += 26
            elif kind == "hint":
                text_centered(screen, SUBTITLE_FONT, text, WIDTH//2, y, TEXT_MUTED)
                y += 22

        pygame.display.flip()
        CLOCK.tick(60)


def main_menu():
    cx = WIDTH // 2

    btn_start   = Button(cx, 380, 220, 52, "Start",   accent=True)
    btn_credits = Button(cx, 450, 220, 52, "Credits")
    btn_quit    = Button(cx, 520, 220, 52, "Quit")

    float_hearts = [
        {"x": cx - 160 + i*80, "phase": i * 1.1, "size": 9 + i*2}
        for i in range(5)
    ]

    while True:
        t = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_start.handle(event):
                return "start"
            if btn_credits.handle(event):
                credits_screen()
                btn_credits.pressed = False
            if btn_quit.handle(event):
                pygame.quit(); sys.exit()

        gradient_bg(screen, BG_TOP, BG_BOT)

        draw_petal(screen, cx - 260, 180, 55, 35,  30, 60)
        draw_petal(screen, cx + 260, 180, 45, 28, -40, 60)
        draw_petal(screen, cx - 220, 570, 40, 25,  50, 45)
        draw_petal(screen, cx + 230, 560, 50, 30, -20, 45)
        draw_petal(screen, cx,       100, 70, 40,  10, 40)

        panel = pygame.Rect(cx - 240, 160, 480, 430)
        draw_rounded_rect(screen, PANEL_BG, panel, 24, PANEL_BDR, 2)

        for px, py in [(panel.left+28, panel.top+28),(panel.right-28, panel.top+28),
                       (panel.left+28, panel.bottom-28),(panel.right-28, panel.bottom-28)]:
            draw_heart_small(screen, px, py, 10, HEART_CLR, 120)

        shadow = TITLE_FONT.render("L CHAT", True, SHADOW_CLR)
        screen.blit(shadow, (cx - shadow.get_width()//2 + 3, 193))
        title  = TITLE_FONT.render("L CHAT", True, TITLE_CLR)
        screen.blit(title,  (cx - title.get_width()//2,      190))

        text_centered(screen, SUBTITLE_FONT, "— D E A T H  N O T E  E D I T I O N —",
                      cx, 272, SUB_CLR)

        for i, h in enumerate(float_hearts):
            fy = 315 + math.sin(t * 1.6 + h["phase"]) * 6
            alpha = int(180 + 60 * math.sin(t * 1.2 + h["phase"]))
            draw_heart_small(screen, h["x"], int(fy), h["size"], HEART_CLR, alpha)

        pygame.draw.line(screen, PANEL_BDR, (cx - 80, 345), (cx + 80, 345), 1)

        btn_start.draw(screen)
        btn_credits.draw(screen)
        btn_quit.draw(screen)

        pygame.display.flip()
        CLOCK.tick(60)


if __name__ == "__main__":
    while True:
        result = main_menu()
        if result == "start":
            import main
            main.screen = screen
            main.main()