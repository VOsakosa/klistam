import traceback
from functools import cache
from pathlib import Path
from typing import Final
from typing_extensions import Self

import pygame
from attr import define, field

from klistam.world.create_world import World, Scene
from klistam import _

KG: Final = 72
WIDTH: Final = 10
HEIGHT: Final = 8


@define
class Game:
    """The main class of the game that handles user input on the top level."""
    screen: pygame.Surface
    scene: Scene
    scene_view: 'SceneView'

    def handle_key(self, event) -> None:
        key = event.unicode
        if not key:
            key = pygame.key.name(event.key)

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
        return cls(screen, scene=World.generate().get_terrain(width=WIDTH, height=HEIGHT), scene_view=SceneView())

    def run(self) -> None:
        print(_("Game started"))
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
def get_terrain(name: str) -> pygame.Surface | None:
    try:
        ans = pygame.image.load(assets_folder / "images" / "terrain" / f"{name}.png").convert_alpha()
        if name in ("grass", "dirt"):
            return pygame.transform.scale(ans, (KG, KG))
        else:
            base = get_terrain("dirt")

            return ans
    except FileNotFoundError:
        return None


@define
class SceneView:
    """Shows the scene to the user."""
    hud: 'HUD' = field(factory=HUD)

    def draw(self, screen: pygame.Surface, scene: Scene):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                self.draw_kachel(terrain=scene.get_terrain_file(x, y), screen=screen, x=x, y=y)
        self.hud.draw()

    def draw_kachel(self, terrain: str, screen: pygame.Surface, x: int, y: int) -> None:
        """Draw a single part of the map."""
        image = get_terrain(terrain)
        if image:
            if image not in ("grass", "dirt"):
                dirt = get_terrain("dirt")
                assert dirt
                screen.blit(dirt, (x * KG, y * KG, KG, KG))
            screen.blit(image, (x * KG, (1 + y) * KG - image.get_height(), KG, KG))
        else:
            # dirt = get_terrain("dirt")
            # assert dirt
            # screen.blit(dirt, (x * KG, y * KG, KG, KG))
            pygame.draw.rect(screen, (70, 70, 70), (x * KG, y * KG, KG, KG))


if __name__ == '__main__':
    Game.create().run()
