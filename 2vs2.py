import sys
import threading
import pygame
import queue
import copy
import time
from pygame_widgets.button import Button
import subprocess
import pygame_widgets
#Dùng lại các hàm ở AI.py 
import AI
from AI import *
TIME_LIMITED = 1800
window_size = (1370,750)

wall = pygame.image.load('.\img\wall.png')
floor = pygame.image.load('.\img/space.png')
box = pygame.image.load('.\img/box.png')
box_docked = pygame.image.load('.\img/bingo.png')
worker = pygame.image.load('.\img\player.png')
worker_docked = pygame.image.load('.\img\worker_dock.png')
docker = pygame.image.load('.\img/target.png')
background = 41,41,41
stepcount = 0

def load_next_map(game, game2,gamesur,gamesur2):
    game.heuristic = 0
    game.heuristic = 0
    game.pathSol = ""
    game.step = 0
    game.state = "..."
    game.time = 0
    game.stack = []

    game2.heuristic = 0
    game2.heuristic = 0
    game2.pathSol = ""
    game2.step = 0
    game2.state = "..."
    game2.time = 0
    game2.stack = []

    gamesur.fill((41, 41, 41))
    gamesur2.fill((41, 41, 41))
    index = game.listMappath.index(game.curMappath)
    if index < len(game.listMappath) - 1:
        game.curMappath = game.listMappath[index + 1]
        game2.curMappath = game2.listMappath[index+1]
        game.matrix = map_open(game.curMappath)
        game2.matrix = map_open(game2.curMappath)
        print_game(game.get_matrix(), gamesur)
        print_game(game2.get_matrix(),gamesur2)

def load_previous_map(game,game2, gamesur,gamesur2):
    game.heuristic = 0
    game.heuristic = 0
    game.pathSol = ""
    game.step = 0
    game.state = "..."
    game.time = 0
    game.stack = []
    
    game2.heuristic = 0
    game2.heuristic = 0
    game2.pathSol = ""
    game2.step = 0
    game2.state = "..."
    game2.time = 0
    game2.stack = []

    gamesur.fill((41, 41, 41))
    gamesur2.fill((41, 41, 41))
    index = game.listMappath.index(game.curMappath)
    if index > 0:
        game.curMappath = game.listMappath[index - 1]
        game2.curMappath = game2.listMappath[index-1]
        game.matrix = map_open(game.curMappath)
        game2.matrix = map_open(game2.curMappath)
        print_game(game.get_matrix(), gamesur)
        print_game(game2.get_matrix(), gamesur2)

def a1():
    global al
    al = "A*"
def a2():
    global al2
    al2 = "A*"

def ucs1():
    global al
    al = "UCS"
def ucs2():
    global al2
    al2 = "UCS"

def dfs1():
    global al
    al = "DFS"
def dfs2():
    global al2
    al2 = "DFS"

def ids1():
    global al
    al = "IDS"
def ids2():
    global al2
    al2 = "IDS"

def bfs1():
    global al
    al = "BFS"
def bfs2():
    global al2
    al2 = "BFS"

def greedy1():
    global al
    al = "Greedy"
def greedy2():
    global al2
    al2 = "Greedy"

def run_solution1(screen, game, sur):
    i = 0
    global al
    if al == "A*":
        sol = AI.AstarSolution(game)
    if al == "UCS":
        sol = AI.UCSsolution(game)
    if al == "BFS":
        sol = AI.BFSsolution(game)
    if al == "DFS":
        sol = AI.DFSsolution(game)
    if al == "Greedy":
        sol = AI.GreedySolution(game)
    if al == "IDS":
        sol = AI.IDSsolution(game)
    for move in sol:
        playByBot(game, move)
        print_game(game.get_matrix(), sur)
        screen.blit(sur, (0, 0))
        pygame.display.flip()
        i += 1
        time.sleep(0.1)

def run_solution2(screen, game2, sur2):
    i = 0
    global al2
    if al2 == "A*":
        sol2 = AI.AstarSolution(game2)
    if al2 == "UCS":
        sol2 = AI.UCSsolution(game2)
    if al2 == "BFS":
        sol2 = AI.BFSsolution(game2)
    if al2 == "DFS":
        sol2 = AI.DFSsolution(game2)
    if al2 == "Greedy":
        sol2 = AI.GreedySolution(game2)
    if al2 == "IDS":
        sol2 = AI.IDSsolution(game2)

    for move2 in sol2:
        playByBot(game2, move2)
        print_game(game2.get_matrix(), sur2)
        screen.blit(sur2, (730, 0))
        pygame.display.flip()
        i += 1
        time.sleep(0.1)

def testrun(screen, game, game2, sur, sur2):
    thread1 = threading.Thread(target=run_solution1, args=(screen, game, sur))
    thread2 = threading.Thread(target=run_solution2, args=(screen, game2, sur2))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

al ="..."
al2 ="..."

def main():
    game = Game(map_open('map/game01.txt'))
    game2 = Game(map_open('map/game01.txt'))
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("Sokoban")

    screen = pygame.display.set_mode(window_size)
    screen.fill((41,41,41))

    #Game surface hiện trò chơi
    game_surface_size = (720, 400)
    game_surface = pygame.Surface(game_surface_size)
    game_surface.fill((41,41,41))

    game_surface_size2 = (720, 400)
    game_surface2 = pygame.Surface(game_surface_size2)
    game_surface2.fill((41,41,41))

    font = pygame.font.Font(None, 36)


    #Button trong game của player 1
    button_reset = Button(screen,  300,  450,  100,  40, text='Reset',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: game.reset() )
    
    button_bfs = Button(screen,  235,  500,  100,  40, text='BFS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: bfs1() )
    button_dfs = Button(screen,  365,  500,  100,  40, text='DFS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: dfs1() )
    button_ucs = Button(screen,  235,  550,  100,  40, text='UCS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: ucs1() )
    button_greedy = Button(screen,  365,  550,  100,  40, text='Greedy',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: greedy1() )
    button_astar = Button(screen,  235,  600,  100,  40, text='A*',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: a1() )
    button_bestfs = Button(screen,  365,  600,  100,  40, text='IDS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: ids1() )
    button_nextlevel = Button(screen,  700-20+50,  700,  100,  40, text='Next',  fontSize=34,  margin=20, 
                               inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: load_next_map(game,game2,game_surface,game_surface2) )
    button_previouslevel = Button(screen,  500+20+50,  700,  100,  40, text='Previous',  fontSize=34,  margin=20,  
                                  inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: load_previous_map(game,game2,game_surface,game_surface2) )
    button_Home = Button(screen,  600+50,  650,  100,  40, text='Home',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: home() )
    button_Run = Button(screen,  600+50,  600,  100,  40, text='Run',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: testrun(screen,game,game2,game_surface,game_surface2) )
    
    #Button trong game của player 2
    button_reset1 = Button(screen,  300+710,  450,  100,  40, text='Reset',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: game2.reset() )
    
    button_bfs1 = Button(screen,  235+710,  500,  100,  40, text='BFS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: bfs2() )
    button_dfs1 = Button(screen,  365+710,  500,  100,  40, text='DFS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: dfs2() )
    button_ucs1 = Button(screen,  235+710,  550,  100,  40, text='UCS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: ucs2() )
    button_greedy1 = Button(screen,  365+710,  550,  100,  40, text='Greedy',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: greedy2() )
    button_astar1 = Button(screen,  235+710,  600,  100,  40, text='A*',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: a2() )
    button_bestfs1 = Button(screen,  365+710,  600,  100,  40, text='IDS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: ids2() )
    

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
                elif event.key == pygame.K_f: 
                    game.unmove()
                elif event.key == pygame.K_KP4: 
                    game2.move(-1,0, True)
                    game2.step += 1
                elif event.key == pygame.K_KP6: 
                    game2.move(1,0, True)
                    game2.step += 1
                elif event.key == pygame.K_KP8: 
                    game2.move(0,-1, True)
                    game2.step += 1
                elif event.key == pygame.K_KP2: 
                    game2.move(0,1, True)
                    game2.step += 1
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if game.step > game2.step:
            game.state = 'Lose'
            game2.state = 'Win'
        elif game.step < game2.step:
            game.state = 'Win'
            game2.state = 'Lose'
        else:
            if game.time > game2.time:
                game.state = 'Lose'
                game2.state = 'Win'
            elif game.time < game2.time:
                game.state = 'Win'
                game2.state = 'Lose'
            else:
                game.state = 'Draw'
                game2.state = 'Draw'
        print_game(game.get_matrix(),game_surface)
        print_game(game2.get_matrix(),game_surface2)

        screen.fill((41, 41, 41), (0, game_surface.get_height(), window_size[0], 50))
        al1_label = font.render(f"Algorithm: {al}", True, (255, 255, 255))
        steps_label = font.render(f"Steps: {game.step}", True, (255, 255, 255))
        time_label = font.render(f"Time: {game.time}s", True, (255, 255, 255))
        state_label=font.render(f"State: {game.state}", True, (255, 255, 255))


        screen.fill((41, 41, 41), (0, game_surface2.get_height(), window_size[0], 50))
        al2_label = font.render(f"Algorithm: {al2}", True, (255, 255, 255))
        steps_label2 = font.render(f"Steps: {game2.step}", True, (255, 255, 255))
        time_label2 = font.render(f"Time: {game2.time}s", True, (255, 255, 255))
        state_label2=font.render(f"State: {game2.state}", True, (255, 255, 255))

        screen.blit(steps_label, (10, game_surface.get_height() + 10))
        screen.blit(time_label, (140, game_surface.get_height() + 10))
        screen.blit(state_label, (300, game_surface.get_height() + 10))
        screen.blit(al1_label, (440, game_surface.get_height() + 10))

        screen.blit(steps_label2, (10+700, game_surface2.get_height() + 10))
        screen.blit(time_label2, (140+700, game_surface2.get_height() + 10))
        screen.blit(state_label2, (300+700, game_surface2.get_height() + 10))
        screen.blit(al2_label, (440+700, game_surface.get_height() + 10))

        screen.blit(game_surface, (0, 0))
        screen.blit(game_surface2, (730, 0))


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