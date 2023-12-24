import sys
import pygame
import copy
from pygame_widgets.button import Button
import subprocess
import pygame_widgets

#Sử dụng lại các hàm và biến ở AI.py
import AI
from AI import *

window_size = (640,600)

def print_game(matrix,screen):
    screen.fill(background)

    screen_width, screen_height = screen.get_size()
    game_width = len(matrix[0]) * 40
    game_height = len(matrix) * 32

    x_offset = (screen_width - game_width) // 2
    y_offset = (screen_height - game_height) // 2

    x = x_offset
    y = y_offset
    
    for row in matrix:
        for char in row:
            if char == ' ': #floor
                screen.blit(floor,(x,y))
            elif char == '#': #wall
                screen.blit(wall,(x,y))
            elif char == '@': #worker on floor
                screen.blit(worker,(x,y))
            elif char == '.': #dock
                screen.blit(docker,(x,y))
            elif char == '*': #box on dock
                screen.blit(box_docked,(x,y))
            elif char == '$': #box
                screen.blit(box,(x,y))
            elif char == '+': #worker on dock
                screen.blit(worker_docked,(x,y))
            x = x + 32
        x = x_offset
        y = y + 32

def main():
    game = Game(map_open('map/game01.txt'))
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("Single play")

    screen = pygame.display.set_mode(window_size)
    screen.fill((41,41,41))

    #Game surface hiện trò chơi
    game_surface_size = (720, 400)
    game_surface = pygame.Surface(game_surface_size)
    game_surface.fill((41,41,41))

    print_game(game.get_matrix(),game_surface)

    font = pygame.font.Font(None, 36)

    #Button trong game
    button_reset = Button(screen,  280,  450,  100,  40, text='Reset',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: game.reset() )
    button_nextlevel = Button(screen,  345,  500,  100,  40, text='Next',  fontSize=34,  margin=20, 
                               inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: load_next_map(game,game_surface) )
    button_previouslevel = Button(screen,  215,  500,  100,  40, text='Previous',  fontSize=34,  margin=20,  
                                  inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: load_previous_map(game,game_surface) )
    button_Home = Button(screen,  280,  550,  100,  40, text='Home',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: home() )

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move(-1,0, True)
                    game.step += 1
                elif event.key == pygame.K_RIGHT:
                    game.move(1,0, True)
                    game.step += 1
                elif event.key == pygame.K_UP:
                    game.move(0,-1, True)
                    game.step += 1
                elif event.key == pygame.K_DOWN:
                    game.move(0,1, True)
                    game.step += 1
                elif event.key == pygame.K_d: 
                    game.unmove()
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if game.is_completed(): 
            game.state = 'Win'

        print_game(game.get_matrix(),game_surface)
        screen.fill((41, 41, 41), (0, game_surface.get_height(), window_size[0], 50))
        steps_label = font.render(f"Steps: {game.step}", True, (255, 255, 255))
        lavel_label = font.render(f"Level: {game.current_level}", True, (255, 255,255))
        
        state_label=font.render(f"State: {game.state}", True, (255, 255, 255))
        screen.blit(steps_label, (80, game_surface.get_height() + 10))
        screen.blit(state_label, (500, game_surface.get_height() + 10))
        screen.blit(lavel_label,(300, game_surface.get_height() + 10))
        screen.blit(game_surface, (0, 0))

        pygame.display.flip()
        pygame_widgets.update(events)
        pygame.display.update()

def home():
    try:
        subprocess.Popen(["python", "menuSokoban.py"])
        sys.exit()
    except Exception as e:
        print(f"Error opening Menu.py: {e}")
if __name__ == "__main__":
    main()