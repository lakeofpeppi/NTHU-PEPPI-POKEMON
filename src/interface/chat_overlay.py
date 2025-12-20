'''
import pygame as pg

class ChatOverlay:
    def __init__(self, width: int = 520, height: int = 240) -> None:
        self.opened = False
        self.text = ""
        self.width = width
        self.height = height
        self.font = pg.font.Font(None, 22)
        self.font_small = pg.font.Font(None, 20)

    def open(self) -> None:
        self.opened = True
        self.text = ""

    def close(self) -> None:
        self.opened = False
        self.text = ""

    def handle_event(self, event: pg.event.Event) -> str | None:
        """
        Returns submitted string if Enter is pressed.
        Returns None otherwise.
        """
        if not self.opened:
            return None
        
        # toggle open
        if event.type == pg.KEYDOWN and event.key == pg.K_t and self.online_manager is not None:
            self.chat_open = True
            self.chat_overlay.open()

        # if open, consume typing
        if self.chat_open:
            submitted = self.chat_overlay.handle_event(event)
            if submitted is not None and self.online_manager is not None:
                self.online_manager.send_chat(submitted)

            if not self.chat_overlay.opened:
                self.chat_open = False

            # IMPORTANT: return/continue so player movement doesn't happen while typing
            continue


        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.close()
                return None

            if event.key == pg.K_RETURN:
                out = self.text.strip()
                self.text = ""
                if out:
                    return out
                return None

            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
                return None

            # accept normal characters
            if event.unicode and event.unicode.isprintable():
                # cap length
                if len(self.text) < 120:
                    self.text += event.unicode

        return None

    def draw(self, screen: pg.Surface, messages: list[dict]) -> None:
        if not self.opened:
            return

        sw, sh = screen.get_size()
        x = (sw - self.width) // 2
        y = sh - self.height - 30

        # dark background
        panel = pg.Surface((self.width, self.height), pg.SRCALPHA)
        panel.fill((0, 0, 0, 170))
        screen.blit(panel, (x, y))

        # messages area
        lines_y = y + 12
        show = messages[-9:]  # last 9 lines

        for m in show:
            sender = m.get("from", "?")
            text = str(m.get("text", ""))
            line = f"{sender}: {text}"
            surf = self.font_small.render(line, True, (255, 255, 255))
            screen.blit(surf, (x + 12, lines_y))
            lines_y += 22

        if self.chat_open and self.online_manager is not None:
            msgs = self.online_manager.get_recent_chat(50)
            self.chat_overlay.draw(screen, msgs)


        # input line
        input_box = pg.Surface((self.width - 24, 30), pg.SRCALPHA)
        input_box.fill((30, 30, 30, 220))
        screen.blit(input_box, (x + 12, y + self.height - 42))

        prompt = self.font.render("> " + self.text, True, (255, 255, 255))
        screen.blit(prompt, (x + 18, y + self.height - 38))

'''

import pygame as pg

class ChatOverlay:
    def __init__(self, width: int = 520, height: int = 240) -> None:
        self.opened = False
        self.text = ""
        self.width = width
        self.height = height
        self.font = pg.font.Font(None, 22)
        self.font_small = pg.font.Font(None, 20)

    def open(self) -> None:
        self.opened = True
        self.text = ""

    def close(self) -> None:
        self.opened = False
        self.text = ""

    def handle_event(self, event: pg.event.Event) -> str | None:
        if not self.opened:
            return None

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.close()
                return None

            if event.key == pg.K_RETURN:
                out = self.text.strip()
                self.text = ""
                if out:
                    return out
                return None

            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
                return None

            if event.unicode and event.unicode.isprintable():
                if len(self.text) < 120:
                    self.text += event.unicode

        return None

    def draw(self, screen: pg.Surface, messages: list[dict]) -> None:
        if not self.opened:
            return

        sw, sh = screen.get_size()
        x = (sw - self.width) // 2
        y = sh - self.height - 30

        panel = pg.Surface((self.width, self.height), pg.SRCALPHA)
        panel.fill((0, 0, 0, 170))
        screen.blit(panel, (x, y))

        lines_y = y + 12
        show = messages[-9:]

        for m in show:
            sender = m.get("from", "?")
            text = str(m.get("text", ""))
            surf = self.font_small.render(f"{sender}: {text}", True, (255, 255, 255))
            screen.blit(surf, (x + 12, lines_y))
            lines_y += 22

        input_box = pg.Surface((self.width - 24, 30), pg.SRCALPHA)
        input_box.fill((30, 30, 30, 220))
        screen.blit(input_box, (x + 12, y + self.height - 42))

        prompt = self.font.render("> " + self.text, True, (255, 255, 255))
        screen.blit(prompt, (x + 18, y + self.height - 38))
