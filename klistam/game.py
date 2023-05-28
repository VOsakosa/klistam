import traceback
from typing_extensions import Self

import pygame
from attr import define

KG = 50
WIDTH = 10
HEIGHT = 8


@define
class Game:
    """The main class of the game that handles user input on the top level."""
    screen: pygame.Surface

    def handle_key(self, event) -> None:
        pass

    def handle_mouse(self, event) -> None:
        pass

    def handle_pressed(self) -> None:
        """Handle continuous key presses."""

    def save_game(self) -> None:
        pass

    @classmethod
    def create(cls) -> Self:
        pygame.init()
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(
            (KG * WIDTH, KG * HEIGHT))
        return cls(screen)

    def run(self) -> None:
        try:
            cont = True
            while cont:
                # noinspection PyBroadException
                try:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            cont = False
                            break
                        elif event.type == pygame.KEYDOWN:
                            self.handle_key(event)
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            self.handle_mouse(event)
                    self.handle_pressed()
                    # self.tick()
                    # self.draw_kachel()
                    # self.draw_inventar()
                    # self.status_panel.tick(self.screen)
                    pygame.display.flip()
                    clock.tick(40)
                except Exception:
                    traceback.print_exc()
            self.save_game()
        finally:
            pygame.quit()


if __name__ == '__main__':
    Game().main()
