import pygame
import sys
import os
from engine.game import Game
from engine.config import Config
from web_display import WebDisplay

class SimulationEngine:
    def __init__(self):
        try:
            # Initialize pygame without audio to avoid ALSA warnings
            pygame.display.init()
            pygame.font.init()
            self.config = Config()
            
            # Set environment variable for SDL to use web display
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            
            # Use a web-compatible display mode
            print("Creating display surface...")
            self.screen = pygame.Surface((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
            print("Display surface created successfully")
            
            # Initialize game components
            pygame.display.set_caption("Life Survival Simulation")
            self.clock = pygame.time.Clock()
            self.game = Game(self.screen, self.config)
            self.running = True
            print("Game initialization complete")
            
        except Exception as e:
            print(f"Initialization error: {str(e)}")
            raise

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                self.screen = pygame.display.set_mode(
                    (width, height),
                    pygame.SCALED | pygame.RESIZABLE | pygame.SHOWN
                )
            self.game.handle_event(event)

    def update(self):
        self.game.update()

    def render(self):
        try:
            # Clear screen and render game
            self.screen.fill((0, 0, 0))
            self.game.render()
            
            # Convert the display to web format and update the webpage
            print("Converting surface to image data...")
            image_data = WebDisplay.surface_to_image_data(self.screen)
            print("Updating webpage...")
            WebDisplay.update_webpage(image_data)
            print("Render complete")
            
        except Exception as e:
            print(f"Render error: {str(e)}")
            raise

    def run(self):
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.render()
                self.clock.tick(self.config.FPS)
        except Exception as e:
            print(f"Critical error: {e}")
        finally:
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    engine = SimulationEngine()
    engine.run()
