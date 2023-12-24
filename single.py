import sys
import pygame
import copy
from pygame_widgets.button import Button
import subprocess
import pygame_widgets
TIME_LIMITED = 1800
window_size = (640,600)
wall = pygame.image.load('.\img\wall.png')
floor = pygame.image.load('.\img/space.png')
box = pygame.image.load('.\img/box.png')
box_docked = pygame.image.load('.\img/bingo.png')
worker = pygame.image.load('.\img\player.png')
worker_docked = pygame.image.load('.\img\worker_dock.png')
docker = pygame.image.load('.\img/target.png')
background = 41,41,41
stepcount = 0
class Game:

    def is_valid_value(self,char):
        if ( char == ' ' or #floor
            char == '#' or #wall
            char == '@' or #worker on floor
            char == '.' or #dock
            char == '*' or #box on dock
            char == '$' or #box
            char == '+' ): #worker on dock
            return True
        else:
            return False

    def __init__(self,matrix):
        self.heuristic = 0
        self.pathSol = ""
        self.stack = []
        self.matrix = matrix
        self.initial_matrix = copy.deepcopy(matrix)
        self.listMappath = ['map/game01.txt', 'map/game02.txt', 'map/game03.txt','map/game04.txt','map/game05.txt','map/game06.txt',
                            'map/game07.txt','map/game08.txt','map/game09.txt','map/game10.txt','map/game11.txt','map/game12.txt',
                            'map/game13.txt','map/game14.txt','map/game15.txt']   
        self.curMappath = "map/game01.txt"
        self.state="..."
        self.step = 0    
        self.current_level = 1 
    def printStep(self):
        print (f"AI Step:{self.aiStep}")
        print (f"Player step: {self.playerStep}")
    def __lt__(self, other):
        return self.heuristic < other.heuristic

    def load_size(self):
        x = 0
        y = len(self.matrix)
        for row in self.matrix:
            if len(row) > x:
                x = len(row)
        return (x * 32, y * 32)

    def get_matrix(self):
        return self.matrix

    def print_matrix(self):
        for row in self.matrix:
            for char in row:
                sys.stdout.write(char)
                sys.stdout.flush()
            sys.stdout.write('\n')

    def get_content(self,x,y):
        return self.matrix[y][x]

    def set_content(self,x,y,content):
        if self.is_valid_value(content):
            self.matrix[y][x] = content
        else:
            print("ERROR: Value '"+content+"' to be added is not valid")

    def worker(self):
        x = 0
        y = 0
        for row in self.matrix:
            for pos in row:
                if pos == '@' or pos == '+':
                    return (x, y, pos)
                else:
                    x = x + 1
            y = y + 1
            x = 0

    def box_list(self):
        x = 0
        y = 0
        boxList = []
        for row in self.matrix:
            for pos in row:
                if pos == '$':
                    boxList.append((x,y))
                x = x + 1
            y = y + 1
            x = 0
        return boxList

    def dock_list(self):
        x = 0
        y = 0
        dockList = []
        for row in self.matrix:
            for pos in row:
                if pos == '.':
                    dockList.append((x,y))
                x = x + 1
            y = y + 1
            x = 0
        return dockList

    def can_move(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y) not in ['#','*','$']

    def next(self,x,y):
        return self.get_content(self.worker()[0]+x,self.worker()[1]+y)

    def can_push(self,x,y):
        return (self.next(x,y) in ['*','$'] and self.next(x+x,y+y) in [' ','.'])

    def is_completed(self):
        for row in self.matrix:
            for cell in row:
                if cell == '$':
                    return False
        return True

    def move_box(self,x,y,a,b):
#        (x,y) -> move to do
#        (a,b) -> box to move
        current_box = self.get_content(x,y)
        future_box = self.get_content(x+a,y+b)
        if current_box == '$' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,' ')
        elif current_box == '$' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,' ')
        elif current_box == '*' and future_box == ' ':
            self.set_content(x+a,y+b,'$')
            self.set_content(x,y,'.')
        elif current_box == '*' and future_box == '.':
            self.set_content(x+a,y+b,'*')
            self.set_content(x,y,'.')

    def unmove(self):
        if len(self.stack) > 0:
            movement = self.stack.pop()
            if movement[2]:
                current = self.worker()
                self.move(movement[0] * -1,movement[1] * -1, False)
                self.move_box(current[0]+movement[0],current[1]+movement[1],movement[0] * -1,movement[1] * -1)
            else:
                self.move(movement[0] * -1,movement[1] * -1, False)

    def move(self,x,y,save):
        if self.can_move(x,y):
            current = self.worker()
            future = self.next(x,y)
            if current[2] == '@' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],' ')
                if save: self.stack.append((x,y,False))
            elif current[2] == '@' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],' ')
                if save: self.stack.append((x,y,False))
            elif current[2] == '+' and future == ' ':
                self.set_content(current[0]+x,current[1]+y,'@')
                self.set_content(current[0],current[1],'.')
                if save: self.stack.append((x,y,False))
            elif current[2] == '+' and future == '.':
                self.set_content(current[0]+x,current[1]+y,'+')
                self.set_content(current[0],current[1],'.')
                if save: self.stack.append((x,y,False))
        elif self.can_push(x,y):
            current = self.worker()
            future = self.next(x,y)
            future_box = self.next(x+x,y+y)
            if current[2] == '@' and future == '$' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '@' and future == '$' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '@' and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
            elif current[2] == '@' and future == '*' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],' ')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '$' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '$' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'@')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '*' and future_box == ' ':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
            elif current[2] == '+' and future == '*' and future_box == '.':
                self.move_box(current[0]+x,current[1]+y,x,y)
                self.set_content(current[0],current[1],'.')
                self.set_content(current[0]+x,current[1]+y,'+')
                if save: self.stack.append((x,y,True))
    def reset(self):
        current_map = self.curMappath
        self.matrix = map_open(self.curMappath) 
        self.heuristic = 0
        self.pathSol = ""
        self.step = 0
        self.state = "..."
        self.time = 0  
        self.stack = []
        print_game(self.get_matrix(), pygame.display.get_surface())

def load_next_map(game, gamesur):
    if (game.current_level == (len(game.listMappath))):
        game.current_level = len(game.listMappath)
    else:
        game.current_level += 1
    game.heuristic = 0
    game.heuristic = 0
    game.pathSol = ""
    game.step = 0
    game.state = "..."
    game.time = 0
    game.stack = []
    gamesur.fill((41, 41, 41))
    index = game.listMappath.index(game.curMappath)
    if index < len(game.listMappath) - 1:
        game.curMappath = game.listMappath[index + 1]
        game.matrix = map_open(game.curMappath)
        print_game(game.get_matrix(), gamesur)

def load_previous_map(game, gamesur):
    if game.current_level == 1:
        game.current_level =1
    else:
        game.current_level -= 1
    game.heuristic = 0
    game.heuristic = 0
    game.pathSol = ""
    game.step = 0
    game.state = "..."
    game.time = 0
    game.stack = []
    gamesur.fill((41, 41, 41))
    index = game.listMappath.index(game.curMappath)
    if index > 0:
        game.curMappath = game.listMappath[index - 1]
        game.matrix = map_open(game.curMappath)
        print_game(game.get_matrix(), gamesur)

def map_open(filename):
    matrix = []
    try:
        file = open(filename, 'r')
        for line in file:
            row = []
            for char in line.strip():
                if char in [' ', '#', '@','$', '*', '.']:
                    row.append(char)
                else:
                    print(f"ERROR: Invalid value {char} in the map file.")
                    sys.exit(1)
            matrix.append(row)
        return matrix
    except FileNotFoundError:
        print(f"ERROR: File {filename} not found.")
        sys.exit(1)

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