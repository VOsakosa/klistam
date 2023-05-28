import traceback
from functools import cache
from pathlib import Path
from typing import Final

from typing_extensions import Self

import pygame
from attr import define

from world.create_world import World, Scene

KG: Final = 72
WIDTH: Final = 10
HEIGHT: Final = 8


@define
class Game:
    """The main class of the game that handles user input on the top level."""
    screen: pygame.Surface
    hud: 'HUD'
    scene: Scene
    scene_view: 'SceneView'

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
        screen = pygame.display.set_mode((KG * WIDTH, KG * HEIGHT))
        return cls(screen, HUD(), scene=World.generate().get_terrain(width=WIDTH, height=HEIGHT), scene_view=SceneView())

    def run(self) -> None:
        clock = pygame.time.Clock()
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
                    self.scene_view.draw(self.screen, self.scene)
                    self.hud.draw()
                    pygame.display.flip()
                    clock.tick(40)
                except Exception:
                    traceback.print_exc()
            self.save_game()
        finally:
            pygame.quit()


@define
class HUD:
    """The Heads-Up-Display HUD is an overlay that is shown above the game elements and serves as a UI to the player."""

    def draw(self):
        pass


assets_folder = Path(__file__).parents[1] / "assets"


@cache
def get_terrain(name: str) -> pygame.Surface:
    if name not in ["dirt", "grass", "tree"]:
        name = "tree"
    return pygame.image.load(assets_folder / "images" / "terrain" / f"{name}.png").convert_alpha()


@define
class SceneView:
    """Shows the scene to the user."""

    def draw(self, screen: pygame.Surface, scene: Scene):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                self.draw_kachel(terrain=scene.get_terrain_file(x, y), screen=screen, x=x, y=y)

    def draw_kachel(self, terrain: str, screen: pygame.Surface, x: int, y: int) -> None:
        """Draw a single part of the map."""
        dreck = get_terrain(terrain)
        screen.blit(dreck, (x * KG, y * KG, KG, KG), (0, 0, dreck.get_width(), dreck.get_height()))


if __name__ == '__main__':
    Game.create().run()
