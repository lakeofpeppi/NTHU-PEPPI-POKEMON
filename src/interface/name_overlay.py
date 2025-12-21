import pygame as pg

class NameOverlay:
    def __init__(self, width: int = 760, height: int = 170) -> None:
        self.opened = False
        self.text = ""
        self.width = width
        self.height = height

        font_path = "assets/fonts/minecraft.ttf"
        self.font = pg.font.Font(font_path, 18)
        self.font_small = pg.font.Font(font_path, 14)

    def open(self) -> None:
        self.opened = True
        self.text = ""

    def close(self) -> None:
        self.opened = False

    def handle_event(self, event: pg.event.Event) -> str | None:
        if not self.opened:
            return None
        if event.type != pg.KEYDOWN:
            return None

        if event.key == pg.K_ESCAPE:
            self.close()
            return None

        if event.key == pg.K_RETURN:
            out = self.text.strip()
            return out if out else None

        if event.key == pg.K_BACKSPACE:
            self.text = self.text[:-1]
            return None

        if event.unicode and event.unicode.isprintable():
            if len(self.text) < 18:
                self.text += event.unicode

        return None

    def draw(self, screen: pg.Surface, x: int, y: int) -> None:
        if not self.opened:
            return

        # panel
        panel = pg.Surface((self.width, self.height), pg.SRCALPHA)
        panel.fill((0, 0, 0, 170))
        screen.blit(panel, (x, y))

        # text
        title = self.font.render("Hi, please type your name here!", True, (255, 255, 255))
        hint  = self.font_small.render("Press Enter to confirm", True, (200, 200, 200))
        screen.blit(title, (x + 18, y + 16))
        screen.blit(hint,  (x + 18, y + 52))

        # input box
        input_box = pg.Surface((self.width - 36, 44), pg.SRCALPHA)
        input_box.fill((30, 30, 30, 220))
        screen.blit(input_box, (x + 18, y + self.height - 62))

        prompt = self.font.render("> " + self.text, True, (255, 255, 255))
        screen.blit(prompt, (x + 26, y + self.height - 56))
