import pygame as pg

class ChatOverlay:
    def __init__(self, width: int = 420, height: int = 220, margin: int = 16) -> None:
        self.opened = False
        self.text = ""
        self.width = width
        self.height = height
        self.margin = margin
        self.font = pg.font.Font(None, 22)
        self.font_small = pg.font.Font(None, 20)
        font_path = "assets/fonts/Minecraft.ttf" 
        self.font = pg.font.Font(font_path, 18)
        self.font_small = pg.font.Font(font_path, 14)

    def open(self) -> None:
        self.opened = True
        self.text = ""

    def close(self) -> None:
        self.opened = False
        self.text = ""

    def handle_event(self, event: pg.event.Event) -> str | None:
        """Return submitted message when Enter is pressed; None otherwise."""
        if not self.opened:
            return None

        if event.type != pg.KEYDOWN:
            return None

        if event.key == pg.K_ESCAPE:
            self.close()
            return None

        if event.key == pg.K_RETURN:
            out = self.text.strip()
            self.text = ""
            return out if out else None

        if event.key == pg.K_BACKSPACE:
            self.text = self.text[:-1]
            return None

        # normal characters
        if event.unicode and event.unicode.isprintable():
            if len(self.text) < 120:
                self.text += event.unicode

        return None

    def draw(self, screen: pg.Surface, messages: list[dict], show_when_closed: bool = True) -> None:
        # show panel even when closed (so you can always see chat history)
        if (not self.opened) and (not show_when_closed):
            return

        sw, sh = screen.get_size()

        x = self.margin
        y = sh - self.height - self.margin

        # background
        panel = pg.Surface((self.width, self.height), pg.SRCALPHA)
        panel.fill((0, 0, 0, 170))
        screen.blit(panel, (x, y))

        # messages
        lines_y = y + 10
        show = messages[-8:]
        for m in show:
            sender = m.get("name") or m.get("from") or m.get("id") or "?"
            text = str(m.get("text", ""))
            surf = self.font_small.render(f"{sender}: {text}", True, (255, 255, 255))
            screen.blit(surf, (x + 10, lines_y))
            lines_y += 22

        # input line ONLY when opened
        if self.opened:
            input_box = pg.Surface((self.width - 20, 30), pg.SRCALPHA)
            input_box.fill((30, 30, 30, 220))
            screen.blit(input_box, (x + 10, y + self.height - 40))

            prompt = self.font.render("> " + self.text, True, (255, 255, 255))
            screen.blit(prompt, (x + 14, y + self.height - 36))
        else:
            hint = self.font_small.render("Press shift + R to chat", True, (200, 200, 200))
            screen.blit(hint, (x + 10, y + self.height - 32))
