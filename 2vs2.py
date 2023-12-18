import sys
import threading
import pygame
import queue
import copy
import time
from pygame_widgets.button import Button
from pygame_widgets.combobox import ComboBox
from tkinter import messagebox
import subprocess
import pygame_widgets
from queue import PriorityQueue
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
                            'map/game13.txt','map/game14.txt','map/game15.txt','map/game16.txt','map/game17.txt']  
        self.curMappath = "map/game01.txt"
        self.state="..."
        self.step = 0    
        self.time = 0
    
    def load_next_map(self,gamesur):
        gamesur.fill((41,41,41))
        index = self.listMappath.index(self.curMappath)
        if index < len(self.listMappath) - 1:
            self.curMappath = self.listMappath[index + 1]
            map_open(self.curMappath)

    def load_previous_map(self,gamesur):
        gamesur.fill((41,41,41))
        index = self.listMappath.index(self.curMappath)
        if index > 0:
            self.curMappath = self.listMappath[index - 1]
            map_open(self.curMappath)
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
        self.matrix = map_open(self.curMappath) 
        self.heuristic = 0
        self.pathSol = ""
        self.step = 0
        self.state = "..."
        self.time = 0  
        self.stack = []

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

        

def validMove(state):
    x = 0
    y = 0
    move = []
    for step in ["U","D","L","R"]:
        if step == "U":
            x = 0
            y = -1
        elif step == "D":
            x = 0
            y = 1
        elif step == "L":
            x = -1
            y = 0
        elif step == "R":
            x = 1
            y = 0

        if state.can_move(x,y) or state.can_push(x,y):
            move.append(step)

    return move

def is_deadlock(state):
    box_list = state.box_list()
    for box in box_list:
        x = box[0]
        y = box[1]
        #corner up-left
        if state.get_content(x,y-1) in ['#','$','*'] and state.get_content(x-1,y) in ['#','$','*']:
            if state.get_content(x-1,y-1) in ['#','$','*']:
                return True
            if state.get_content(x,y-1) == '#' and state.get_content(x-1,y) =='#':
                return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x+1,y-1) == '#' and state.get_content(x-1,y+1) == '#':
                    return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x-1,y) == '#':
                if state.get_content(x+1,y-1) == '#':
                    return True
            if state.get_content(x,y-1) == '#' and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x-1,y+1) == '#':
                    return True
                
        #corner up-right
        if state.get_content(x,y-1) in ['#','$','*'] and state.get_content(x+1,y) in ['#','$','*']:
            if state.get_content(x+1,y-1) in ['#','$','*']:
                return True
            if state.get_content(x,y-1) == '#' and state.get_content(x+1,y) =='#':
                return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x-1,y-1) == '#' and state.get_content(x+1,y+1) == '#':
                    return True
            if state.get_content(x,y-1) in ['$','*'] and state.get_content(x+1,y) == '#':
                if state.get_content(x-1,y-1) == '#':
                    return True
            if state.get_content(x,y-1) == '#' and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x+1,y+1) == '#':
                    return True


        #corner down-left
        elif state.get_content(x,y+1) in ['#','$','*'] and state.get_content(x-1,y) in ['#','$','*']:
            if state.get_content(x-1,y+1) in ['#','$','*']:
                return True
            if state.get_content(x,y+1) == '#' and state.get_content(x-1,y) =='#':
                return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x-1,y-1) == '#' and state.get_content(x+1,y+1) == '#':
                    return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x-1,y) == '#':
                if state.get_content(x+1,y+1) == '#':
                    return True
            if state.get_content(x,y+1) == '#' and state.get_content(x-1,y) in ['$','*']:
                if state.get_content(x-1,y-1) == '#':
                    return True
                

        #corner down-right
        elif state.get_content(x,y+1) in ['#','$','*'] and state.get_content(x+1,y) in ['#','$','*']:
            if state.get_content(x+1,y+1) in ['#','$','*']:
                return True
            if state.get_content(x,y+1) == '#' and state.get_content(x+1,y) =='#':
                return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x-1,y+1) == '#' and state.get_content(x+1,y-1) == '#':
                    return True
            if state.get_content(x,y+1) in ['$','*'] and state.get_content(x+1,y) == '#':
                if state.get_content(x-1,y+1) == '#':
                    return True
            if state.get_content(x,y+1) == '#' and state.get_content(x+1,y) in ['$','*']:
                if state.get_content(x+1,y-1) == '#':
                    return True
                
    return False

def get_distance(state):
    sum = 0
    box_list = state.box_list()
    dock_list = state.dock_list()
    for box in box_list:
        for dock in dock_list:
            sum += (abs(dock[0] - box[0]) + abs(dock[1] - box[1]))
    return sum

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
    game_width = len(matrix[0]) * 32  
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
def h(state):
    total_distance = 0
    boxes = state.box_list()
    docks = state.dock_list()

    for box in boxes:
        if docks:  
            distance = min(abs(box[0] - dock[0]) + abs(box[1] - dock[1]) for dock in docks)
            total_distance += distance
        else:
            total_distance += 0
    return total_distance

def AstarSolution(game):
    start = time.time()
    node_generated = 0
    state = copy.deepcopy(game) 
    node_generated += 1
    if is_deadlock(state):
        end = time.time()
        print("Time to find solution:",round(end -start,2))
        print("Number of visited node:",node_generated)
        print("No Solution!")
        return "NoSol"                 
    stateSet = PriorityQueue()    
    stateSet.put((0, state))  
    stateExplored = []                 
    print("Processing...")
    while not stateSet.empty():
        if (time.time() - start) >= TIME_LIMITED:
            print("Time Out!")
            return "TimeOut"                        
        _, currState = stateSet.get()                    
        move = validMove(currState)                     
        stateExplored.append(currState.get_matrix())    
        
        for step in move:                              
            newState = copy.deepcopy(currState)
            node_generated += 1
            if step == "U":
                newState.move(0,-1,False)
            elif step == "D":
                newState.move(0,1,False)
            elif step == "L":
                newState.move(-1,0,False)
            elif step == "R":
                newState.move(1,0,False)
            newState.pathSol += step
        
            if newState.is_completed():
                end = time.time()
                print("Time to find solution with A*:",round(end -start,2),"seconds")
                print("Number of visited node with A*:",node_generated)
                print("Solution:",newState.pathSol)
                game.step = len(newState.pathSol)
                game.time = round(end -start,2)
                return newState.pathSol

            if (newState.get_matrix() not in stateExplored) and (not is_deadlock(newState)):
                cost = len(newState.pathSol) + h(newState)
                stateSet.put((cost, newState))  
                
    end = time.time()
    print("Time to find solution:",round(end -start,2))
    print("Number of visited node:",node_generated)
    print("No Solution!")
    return "NoSol"

def UCSsolution(game):
    start = time.time()
    node_generated = 0
    state = copy.deepcopy(game) 
    node_generated += 1
    if is_deadlock(state):
        end = time.time()
        print("Time to find solution:",round(end -start,2))
        print("Number of visited node:",node_generated)
        print("No Solution!")
        return "NoSol"                 
    stateSet = PriorityQueue()    
    stateSet.put((0, state))  
    stateExplored = []                 
    print("Processing...")
    while not stateSet.empty():
        if (time.time() - start) >= TIME_LIMITED:
            print("Time Out!")
            return "TimeOut"                        
        _, currState = stateSet.get()                    
        move = validMove(currState)                     
        stateExplored.append(currState.get_matrix())    
        
        for step in move:                              
            newState = copy.deepcopy(currState)
            node_generated += 1
            if step == "U":
                newState.move(0,-1,False)
            elif step == "D":
                newState.move(0,1,False)
            elif step == "L":
                newState.move(-1,0,False)
            elif step == "R":
                newState.move(1,0,False)
            newState.pathSol += step
        
            if newState.is_completed():
                end = time.time()
                print("Time to find solution with UCS:",round(end -start,2),"seconds")
                print("Number of visited node with UCS:",node_generated)
                print("Solution:",newState.pathSol)
                game.step = len(newState.pathSol)
                game.time = round(end -start,2)
                return newState.pathSol

            if (newState.get_matrix() not in stateExplored) and (not is_deadlock(newState)):
                stateSet.put((len(newState.pathSol), newState))  # Add the cost to the queue
    end = time.time()
    print("Time to find solution:",round(end -start,2))
    print("Number of visited node:",node_generated)
    print("No Solution!")
    return "NoSol"

def IDSsolution(game):
    DEEPMAX = 1000000
    TIME_LIMITED = 300

    start = time.time()
    node_generated = 0

    for depth in range(1, DEEPMAX + 1,1):
        result = DLS(game, depth, start, TIME_LIMITED, node_generated, DEEPMAX)
        if result == "TimeOut":
            return "TimeOut"
        elif result == "NoSol":
            continue
        else:
            return result

    print("Exceeded maximum depth!")
    return "NoSol"

def DLS(game, depth, start, time_limit, node_generated, DEEPMAX):
    state = copy.deepcopy(game)
    state.heuristic = 0
    node_generated += 1

    stateSet = [state]
    stateExplored = set()

    while stateSet:
        if (time.time() - start) >= time_limit:
            print("Time Out!")
            return "TimeOut"

        currState = stateSet.pop()
        move = validMove(currState)
        stateExplored.add(tuple(map(tuple, currState.get_matrix())))

        if node_generated >= DEEPMAX:
            print("Exceeded maximum depth!")
            return "NoSol"

        for step in move:
            newState = copy.deepcopy(currState)
            node_generated += 1
            if step == "U":
                newState.move(0, -1, False)
            elif step == "D":
                newState.move(0, 1, False)
            elif step == "L":
                newState.move(-1, 0, False)
            elif step == "R":
                newState.move(1, 0, False)

            newState.pathSol += step

            if newState.is_completed():
                end = time.time()
                print("IDS")
                print("Time to find solution:", round(end - start, 2), "seconds")
                print("Number of visited node:", node_generated)
                print('Step:', len(newState.pathSol))
                print("Solution:", newState.pathSol)
                game.step = len(newState.pathSol)
                game.time = round(end - start, 2)
                return newState.pathSol

            if node_generated >= DEEPMAX:
                print("Exceeded maximum depth!")
                return "NoSol"

            if tuple(map(tuple, newState.get_matrix())) not in stateExplored and not is_deadlock(newState) and len(newState.pathSol) <= depth:
                stateSet.append(newState)

    return "NoSol"


def DFSsolution(game):
    DEEPMAX = 1000000
    TIME_LIMITED = 60  

    start = time.time()
    node_generated = 0
    state = copy.deepcopy(game)
    state.heuristic = 0
    node_generated += 1

    stateSet = [state]  
    stateExplored = set()

    print("Processing...")

    while stateSet:
        if (time.time() - start) >= TIME_LIMITED:
            print("Time Out!")
            return "TimeOut"

        currState = stateSet.pop()
        move = validMove(currState)
        stateExplored.add(tuple(map(tuple, currState.get_matrix())))

        if node_generated >= DEEPMAX:
            print("Exceeded maximum depth!")

        for step in move:
            newState = copy.deepcopy(currState)
            node_generated += 1
            if step == "U":
                newState.move(0, -1, False)
            elif step == "D":
                newState.move(0, 1, False)
            elif step == "L":
                newState.move(-1, 0, False)
            elif step == "R":
                newState.move(1, 0, False)

            newState.pathSol += step

            if newState.is_completed():
                end = time.time()
                print("DFS")
                print("Time to find solution:", round(end - start, 2), "seconds")
                print("Number of visited node:", node_generated)
                print('Step:', len(newState.pathSol))
                print("Solution:", newState.pathSol)
                game.step = len(newState.pathSol)
                game.time = round(end - start, 2)
                return newState.pathSol

            if node_generated >= DEEPMAX:
                print("Exceeded maximum depth!")

            if tuple(map(tuple, newState.get_matrix())) not in stateExplored and not is_deadlock(newState):
                stateSet.append(newState)

    end = time.time()
    print("Time to find solution:", round(end - start, 2))
    print("Number of visited node:", node_generated)
    print("No Solution!")
    return "NoSol"

def BFSsolution(game):
    start = time.time()
    node_generated = 0
    state = copy.deepcopy(game)                  
    node_generated += 1
    if is_deadlock(state):
        end = time.time()
        print("Time to find solution:",round(end -start,2))
        print("Number of visited node:",node_generated)
        print("No Solution!")
        return "NoSol"
    
    stateSet = queue.Queue()    
    stateSet.put(state)
    stateExplored = []          
    print("Processing...")
    while not stateSet.empty():
        if (time.time() - start) >= TIME_LIMITED:
            print("Time Out!")
            return "TimeOut"                    
        currState = stateSet.get()      
                        
        move = validMove(currState)                     
        stateExplored.append(currState.get_matrix())    
        for step in move:                               
            newState = copy.deepcopy(currState)
            node_generated += 1
            if step == "U":
                newState.move(0,-1,False)
            elif step == "D":
                newState.move(0,1,False)
            elif step == "L":
                newState.move(-1,0,False)
            elif step == "R":
                newState.move(1,0,False)
            newState.pathSol += step
        
            if newState.is_completed():
                end = time.time()
                print("Time to find solution:",round(end -start,2),"seconds")
                print("Number of visited node:",node_generated)
                print("Solution:",newState.pathSol)
                game.step = len(newState.pathSol)
                game.time = round(end -start,2)
                return newState.pathSol

            if (newState.get_matrix() not in stateExplored) and (not is_deadlock(newState)):
                stateSet.put(newState)
    end = time.time()
    print("Time to find solution:",round(end -start,2))
    print("Number of visited node:",node_generated)
    print("No Solution!")
    return "NoSol"

def GreedySolution(game):
   
    start = time.time()
    node_generated = 0
    state = copy.deepcopy(game)
    state.heuristic = get_distance(state)
    node_generated += 1
    if is_deadlock(state):
        end = time.time()
        print("Time to find solution:",round(end -start,2))
        print("Number of visited node:",node_generated)
        print("No Solution!")
        return "NoSol"                 
    stateSet = queue.PriorityQueue()    
    stateSet.put(state)
    stateExplored = []                 
    print("Processing...")
    while not stateSet.empty():
        if (time.time() - start) >= TIME_LIMITED:
            print("Time Out!")
            return "TimeOut"                        
        currState = stateSet.get()                      
        move = validMove(currState)                     
        stateExplored.append(currState.get_matrix())    
        
        for step in move:                              
            newState = copy.deepcopy(currState)
            node_generated += 1
            if step == "U":
                newState.move(0,-1,False)
            elif step == "D":
                newState.move(0,1,False)
            elif step == "L":
                newState.move(-1,0,False)
            elif step == "R":
                newState.move(1,0,False)
            newState.pathSol += step
           
            newState.heuristic = get_distance(newState)
        
            if newState.is_completed():
                end = time.time()
                print("Time to find solution:",round(end -start,2),"seconds")
                print("Number of visited node:",node_generated)
                print("Solution:",newState.pathSol)
                game.step = len(newState.pathSol)
                game.time = round(end -start,2)
                return newState.pathSol

            if (newState.get_matrix() not in stateExplored) and (not is_deadlock(newState)):
                stateSet.put(newState)
    end = time.time()
    print("Time to find solution:",round(end -start,2))
    print("Number of visited node:",node_generated)
    print("No Solution!")
    return "NoSol"

def playByBot(game,move):
    if move == "U":
        game.move(0,-1,False)
    elif move == "D":
        game.move(0,1,False)
    elif move == "L":
        game.move(-1,0,False)
    elif move == "R":
        game.move(1,0,False)
    else:
        game.move(0,0,False)

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
        sol = AstarSolution(game)
    if al == "UCS":
        sol = UCSsolution(game)
    if al == "BFS":
        sol = BFSsolution(game)
    if al == "DFS":
        sol = DFSsolution(game)
    if al == "Greedy":
        sol = GreedySolution(game)
    if al == "IDS":
        sol = IDSsolution(game)
    for move in sol:
        playByBot(game, move)
        print_game(game.get_matrix(), sur)
        screen.blit(sur, (0, 0))
        pygame.display.flip()
        i += 1
        time.sleep(0.025)

def run_solution2(screen, game2, sur2):
    i = 0
    global al2
    if al2 == "A*":
        sol2 = AstarSolution(game2)
    if al2 == "UCS":
        sol2 = UCSsolution(game2)
    if al2 == "BFS":
        sol2 = BFSsolution(game2)
    if al2 == "DFS":
        sol2 = DFSsolution(game2)
    if al2 == "Greedy":
        sol2 = GreedySolution(game2)
    if al2 == "IDS":
        sol2 = IDSsolution(game2)

    for move2 in sol2:
        playByBot(game2, move2)
        print_game(game2.get_matrix(), sur2)
        screen.blit(sur2, (730, 0))
        pygame.display.flip()
        i += 1
        time.sleep(0.025)

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
    button_reset = Button(screen,  300+710,  450,  100,  40, text='Reset',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: game2.reset() )
    
    button_bfs = Button(screen,  235+710,  500,  100,  40, text='BFS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: bfs2() )
    button_dfs = Button(screen,  365+710,  500,  100,  40, text='DFS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: dfs2() )
    button_ucs = Button(screen,  235+710,  550,  100,  40, text='UCS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: ucs2() )
    button_greedy = Button(screen,  365+710,  550,  100,  40, text='Greedy',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: greedy2() )
    button_astar = Button(screen,  235+710,  600,  100,  40, text='A*',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: a2() )
    button_bestfs = Button(screen,  365+710,  600,  100,  40, text='IDS',  fontSize=34,  margin=20, 
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

def ok():
    messagebox.showinfo("Hello", "BFS solve!")
def home():
    try:
        subprocess.Popen(["python", "menuSokoban.py"])
        sys.exit()
    except Exception as e:
        print(f"Error opening Menu.py: {e}")
if __name__ == "__main__":
    main()