import sys
import tkinter as tk
import pygame
import queue
import copy
import time
from pygame_widgets.button import Button
from pygame_widgets.combobox import ComboBox
from tkinter import messagebox
from queue import PriorityQueue
import subprocess
import pygame_widgets
TIME_LIMITED = 1800
window_size = (1000,600)
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
        self.time = 0
        self.current_level = 1  
    
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
                stateSet.put((len(newState.pathSol), newState))  
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
                print("Greedy")
                print("Time to find solution:",round(end -start,2),"seconds")
                print("Number of visited node:",node_generated)
                print("Step:",len(newState.pathSol))
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

def a(screen,game,game_surface):
    sol = AstarSolution(game)
    for move in sol:
        playByBot(game,move)
        print_game(game.get_matrix(),pygame.display.get_surface())
        pygame.display.flip()
        screen.blit(game_surface, (0, 0))
        time.sleep(0.01)    

def ucs(game):
    sol = UCSsolution(game)
    for move in sol:
        playByBot(game,move)
        print_game(game.get_matrix(),pygame.display.get_surface())
        pygame.display.flip()
        time.sleep(0.01)

def dfs(game):
    i=0
    sol= DFSsolution(game)
    for move in sol:
        playByBot(game,move)
        print_game(game.get_matrix(),pygame.display.get_surface())
        pygame.display.flip()
        i+=1
        time.sleep(0.01)
def ids(game):
    i=0
    sol= IDSsolution(game)
    for move in sol:
        playByBot(game,move)
        print_game(game.get_matrix(),pygame.display.get_surface())
        pygame.display.flip()
        i+=1
        time.sleep(0.01)

def bfs(game):
    i=0
    sol= BFSsolution(game)
    for move in sol:
        playByBot(game,move)
        print_game(game.get_matrix(),pygame.display.get_surface())
        pygame.display.flip()
        i+=1
        time.sleep(0.01)
def greedy(game):
    i=0
    sol= GreedySolution(game)
    for move in sol:
        playByBot(game,move)
        print_game(game.get_matrix(),pygame.display.get_surface())
        pygame.display.flip()
        i+=1
        time.sleep(0.01)

def display_history(level):
    history_file_path = f'history/{level}.txt'

    try:
        with open(history_file_path, 'r') as file:
            history_content = file.read()

            window = tk.Tk()

            window.geometry("1100x400")  

            algorithm_sections = history_content.split('\n\n')

            level_frame = tk.Frame(window)
            level_label = tk.Label(level_frame, text=f"Level: {level}", font=("Courier", 16, "bold"))
            level_label.pack()

            separator_line = tk.Label(window, text="------------------------", font=("Courier", 12))
            separator_line.grid(row=1, column=0, columnspan=3)

            for i, section in enumerate(algorithm_sections):
                algorithm_label = tk.Label(window, text=section, justify=tk.LEFT, font=("Courier", 14))
                algorithm_label.grid(row=(i // 3) + 2, column=i % 3)

            level_frame.grid(row=0, column=0, columnspan=3)

            # Increase spacing between columns
            for i in range(3):
                window.columnconfigure(i, weight=10)

            window.mainloop()

    except FileNotFoundError:
        print(f"History file not found for level {level}")


def main():
    game = Game(map_open('map/game01.txt'))
    pygame.init()
    pygame.display.init()
    pygame.display.set_caption("Sokoban")

    screen = pygame.display.set_mode(window_size)
    screen.fill((41,41,41))

    #Game surface hiện trò chơi
    game_surface_size = (720, 400)
    game_surface = pygame.Surface(game_surface_size)
    game_surface.fill((41,41,41))

    print_game(game.get_matrix(),game_surface)

    font = pygame.font.Font(None, 36)

    #Button trong game
    button_reset = Button(screen,  815,  50,  100,  40, text='Reset',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: game.reset() )
    
    button_bfs = Button(screen,  750,  100,  100,  40, text='BFS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: bfs(game) )
    button_dfs = Button(screen,  880,  100,  100,  40, text='DFS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: dfs(game) )
    button_ucs = Button(screen,  750,  150,  100,  40, text='UCS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: ucs(game) )
    button_greedy = Button(screen,  880,  150,  100,  40, text='Greedy',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: greedy(game) )
    button_astar = Button(screen,  750,  200,  100,  40, text='A*',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: a(screen,game,game_surface) )
    button_bestfs = Button(screen,  880,  200,  100,  40, text='IDS',  fontSize=34,  margin=20, 
                          inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: ids(game) )
    button_nextlevel = Button(screen,  880,  350,  100,  40, text='Next',  fontSize=34,  margin=20, 
                               inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: load_next_map(game,game_surface) )
    button_previouslevel = Button(screen,  750,  350,  100,  40, text='Previous',  fontSize=34,  margin=20,  
                                  inactiveColour=(200, 50, 0), hoverColour=(150, 0, 0), pressedColour=(0, 200, 20),  onClick=lambda: load_previous_map(game,game_surface) )
    button_Home = Button(screen,  815,  300,  100,  40, text='Home',  fontSize=34,  margin=20, 
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
                elif event.key == pygame.K_a:
                    sol = AstarSolution(game)
                    flagAuto = 1
                elif event.key == pygame.K_p:
                    sol = UCSsolution(game)
                    flagAuto = 1
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
        time_label = font.render(f"Time: {game.time}s", True, (255, 255, 255))

        lavel_label = font.render(f"Level: {game.current_level}", True, (255, 255,255))
        
        state_label=font.render(f"State: {game.state}", True, (255, 255, 255))
        screen.blit(steps_label, (80, game_surface.get_height() + 10))
        screen.blit(time_label, (260, game_surface.get_height() + 10))
        screen.blit(state_label, (520, game_surface.get_height() + 10))
        screen.blit(lavel_label,(400, game_surface.get_height() + 10))
        screen.blit(game_surface, (0, 0))

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