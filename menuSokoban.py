import subprocess
import sys
import pygame
import time
pygame.init()

class Button():
    def __init__(self, x, y, width, height, color, text, onclick):
        self.x = x 
        self.y = y 
        self.width = width 
        self.height = height 
        self.color = color 
        self.text = text 
        self.onclick = onclick 
        self.surface = pygame.Surface((self.width, self.height)) 
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height) 
        self.font = pygame.font.SysFont("Arial", 32) 
        self.text_surf = self.font.render(self.text, True, (0, 0, 0)) 
    def draw(self, screen):
        self.surface.fill(self.color) 
        self.surface.blit(self.text_surf, (self.width // 2 - self.text_surf.get_width() // 2, self.height // 2 - self.text_surf.get_height() // 2)) # Blit the text on the center of the surface
        screen.blit(self.surface, (self.x, self.y)) 
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN: 
            mouse_pos = pygame.mouse.get_pos() 
            if self.rect.collidepoint(mouse_pos): 
                self.onclick() 
                
screen = pygame.display.set_mode((1448, 758))
pygame.display.set_caption("Sokoban")
backgroundmenu = pygame.image.load("img/background.jpg")
backgroundGame = pygame.image.load("img/backgroundGameNau.jpg")

def startMenu_game():
    try:
        subprocess.Popen(["python", "single.py"])
        sys.exit()
    except Exception as e:
        print(f"Error opening Menu.py: {e}")
def endMenu_game():
    global running
    print("End the game")
    running = False
def multiplePlay_game():
    try:
        subprocess.Popen(["python", "2vs2.py"])
        sys.exit()
    except Exception as e:
        print(f"Error opening Menu.py: {e}")
# Nut start game   
start_time = None
step_count = 0
game_states = []
def startPlayer_game():
    global start_time
    global step_count
    print("Go game")
    # Record the start time
    start_time = time.time()
    step_count = 0
def undo():
    global game_states
    if game_states:
        # Remove the last game state
        game_states.pop()
        print("Undo last step")
# Nut end game
def endPlayer_game():
    global current_interface
    print("End game")
    current_interface = "menu"
    
def toggle_mode():
    if mode_button.text == "Player Mode":
        mode_button.text = "AI Mode"
        print("Switched to AI Mode")
    else:
        mode_button.text = "Player Mode"
        print("Switched to Player Mode")
#giao dien       
def switch_interface():
    try:
        subprocess.Popen(["python", "AI.py"])
        sys.exit()
    except Exception as e:
        print(f"Error opening Menu.py: {e}")
#next level
def next_level():
    print("Next level")
    
current_interface = "menu"
#Button for Menu
switch_button = Button(1100, 400, 150, 75, (255, 255, 255), "AI", switch_interface)
startMenu_button = Button(1100, 300, 150, 75, (255, 255, 255), "PLAY", startMenu_game)
endMenu_button = Button(1100, 600, 150, 75, (255, 255, 255), "Quit", endMenu_game)
multiplePlay_button = Button(1100, 500, 150, 75, (255, 255, 255), "MULTIPLE", multiplePlay_game)

mode_button = Button(1100, 400, 125, 75, (255, 255, 255), "Mode", toggle_mode)

#Button for Mode Player
startPlayer_button = Button(1150, 150, 140, 75, (255, 255, 255), "StartGame", startPlayer_game)
endPlayer_button = Button(1150, 250, 140, 75, (255, 255, 255), "QuitGame", endPlayer_game)
next_button = Button(1250, 400, 125, 75, (255, 255, 255), "Next", next_level)
undo_button = Button(1050, 400, 125, 75, (255, 255, 255), "Undo", undo)
#label time
font = pygame.font.Font(None, 36)
#Map game
# Get the size of the game window
window_width, window_height = screen.get_size()

# Set the size of the game map
map_width, map_height = 500, 500
#Chay game 
running = True

while running:
    if current_interface == "menu":
        # Draw interface 1
        screen.blit(backgroundmenu, (0, 0))
        startMenu_button.draw(screen)
        endMenu_button.draw(screen)
        switch_button.draw(screen)
        multiplePlay_button.draw(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                startMenu_button.handle_event(event)
                endMenu_button.handle_event(event)
                switch_button.handle_event(event)
                multiplePlay_button.handle_event(event)

    else:
        screen.blit(backgroundGame, (0, 0))
        startPlayer_button.draw(screen)
        endPlayer_button.draw(screen)
        next_button.draw(screen)
        undo_button.draw(screen)


        # vi tri map
        map_x = (window_width - map_width) // 2
        map_y = (window_height - map_height) // 2

        # ve map
        pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(map_x, map_y, map_width, map_height), 2)

        if start_time is not None:
            # Tinh thoi gian
            elapsed_time = time.time() - start_time

            # chuyen doi thoi gian
            minutes = int(elapsed_time // 60)
            seconds = int(elapsed_time % 60)

            # Render the time as a Surface
            time_surface = font.render(f"{minutes}:{seconds}", True, (255, 255, 255))

            # Render the label as a Surface
            label_surface = font.render("Time:", True, (255, 255, 255))
            step_surface = font.render(f"Step: {step_count}", True, (255, 255, 255))
            # Draw the label and the time onto the screen
            screen.blit(label_surface, (120, 50))
            screen.blit(time_surface, (200, 50))
            screen.blit(step_surface, (120, 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                startPlayer_button.handle_event(event)
                endPlayer_button.handle_event(event)
                next_button.handle_event(event)
                undo_button.handle_event(event)


    pygame.display.update()
pygame.quit()