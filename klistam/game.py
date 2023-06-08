import traceback
from functools import cache
import numpy as np
from pathlib import Path
from typing import Final
from typing_extensions import Self

import pygame
from attr import define, field

from klistam.world.create_world import Scene, World
from klistam.world import WIDTH, HEIGHT
from klistam import _
from klistam.world.mob import Mob, Movement

KG: Final = 72
MOVEMENT_SPEED: Final = 0.05

MOVEMENTS: Final = (
    (np.array((1, 0)), pygame.K_RIGHT),
    (np.array((-1, 0)), pygame.K_LEFT),
    (np.array((0, -1)), pygame.K_UP),
    (np.array((0, 1)), pygame.K_DOWN)
)


@define
class Game:
    """The main class of the game that handles user input on the top level."""
    screen: pygame.Surface
    world: World
    scene_view: 'SceneView'

    def handle_key(self, event) -> None:
        key = event.unicode
        if not key:
            key = pygame.key.name(event.key)
        if key == "q":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_mouse(self, event) -> None:
        pass

    def handle_pressed(self) -> None:
        """Handle continuous key presses."""
        player = self.world.player
        if player:
            if not player.position or player.movement:
                pass
            else:
                for direction, key in MOVEMENTS:
                    if pygame.key.get_pressed()[key]:
                        target = player.position.coordinates + direction
                        if obj := self.world.get_object_at(target):
                            print(_("The player walked against {obj}").format(obj=obj))
                            player.movement = Movement(np.array((0, 0)))
                        else:
                            player.movement = Movement(direction)
                            self.world.summon(player, target)
                        break
            if player.movement:
                player.movement.progress -= MOVEMENT_SPEED
                if player.movement.progress <= 0.:
                    player.movement = None

    def save_game(self) -> None:
        pass

    @classmethod
    def create(cls) -> Self:
        pygame.init()
        screen = pygame.display.set_mode((KG * WIDTH, KG * HEIGHT))
        world = World.generate()
        return cls(screen, world=world, scene_view=SceneView())

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
                    self.world.tick()
                    # self.draw_kachel()
                    # self.draw_inventar()
                    # self.status_panel.tick(self.screen)
                    self.scene_view.draw(self.screen, self.world.get_player_scene())
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


@cache
def get_sprite_surface(name: str, scope: str) -> pygame.Surface | None:
    try:
        return pygame.image.load(assets_folder / "images" / scope / f"{name}.png").convert_alpha()
    except FileNotFoundError:
        return None


@define
class SceneView:
    """Shows the scene to the user."""
    hud: 'HUD' = field(factory=HUD)

    def draw(self, screen: pygame.Surface, scene: Scene) -> None:
        for y in range(HEIGHT):
            for x in range(WIDTH):
                self.draw_kachel(terrain=scene.get_terrain_file(x, y), screen=screen, x=x, y=y)
        for mob in scene.mobs:
            if mob.sprite and mob.position:
                self.draw_mob(mob, screen)
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

    def draw_mob(self, mob: Mob, screen: pygame.Surface) -> None:
        """Draw a mob."""
        assert mob.sprite
        assert mob.position
        surface = get_sprite_surface(mob.sprite.name, mob.sprite.scope) or get_sprite_surface("unknown", "object")
        assert surface
        x, y = mob.position.scene_coordinates
        x *= KG
        y *= KG
        if mob.movement:
            offset = np.rint(mob.movement.offset * KG)
            x += offset[0]
            y += offset[1]
        screen.blit(surface, (x + (KG - surface.get_width()) // 2, y - surface.get_height() + KG))


if __name__ == '__main__':
    Game.create().run()
