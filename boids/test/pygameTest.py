import pygame as pg
import sys

class Example:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((400, 400))
        self.clock = pg.time.Clock()
        self.done = False

        self.image = pg.Surface((100, 100), pg.SRCALPHA)
        self.image.fill(pg.Color('white'))
        
        self.font = pg.font.Font(None, 36)  # Change the font and size as needed

    def run(self):
        while not self.done:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.done = True

            self.screen.fill((255, 255, 255))

            center = (200, 200)
            velocity = (250, 250)
            acceleration = (200, 300)
            steering = (300, 200)

            overlay = pg.Surface((100, 100), pg.SRCALPHA)
            overlay.blit(self.image, center - (10, 10))

            pg.draw.line(overlay, pg.Color('green'), center, velocity, 3)
            pg.draw.line(overlay, pg.Color('red'), center + (5, 0),
                         acceleration + (5, 0), 3)
            pg.draw.line(overlay, pg.Color('blue'), center - (5, 0),
                         steering - (5, 0), 3)

            # Add text to the overlay
            text_surface = self.font.render(self.name, True, pg.Color('black'))
            text_rect = text_surface.get_rect(center=(50, 50))
            overlay.blit(text_surface, text_rect)

            self.screen.blit(overlay, (50, 50))  # Adjust the position as needed

            pg.display.flip()
            self.clock.tick(30)

        pg.quit()
        sys.exit()

if __name__ == "__main__":
    example = Example()
    example.run()
