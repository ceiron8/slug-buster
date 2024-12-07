import pygame
import random
import math
from pygame import mixer

# Initialize Pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((1024, 768))
pygame.display.set_caption("Slug Buster")
icon = pygame.image.load('Assets/ufo.png')
pygame.display.set_icon(icon)

# Background
background = pygame.image.load('Assets/startng.jpg')
background = pygame.transform.scale(background, (1024, 768))
mixer.music.load('Assets/Jeremy Blake.wav')
mixer.music.play(-1)

# Collision Sound
collision_sound = mixer.Sound('Assets/explosion.wav')
collision_sound.set_volume(0.5)

# Boss hit sound
boss_hit_sound = mixer.Sound('Assets/boss_hit.wav')
boss_hit_sound.set_volume(0.7)

# Fonts
font = pygame.font.Font('freesansbold.ttf', 32)
over_font = pygame.font.Font('freesansbold.ttf', 70)

# Player setup
playerImg = pygame.image.load('Assets/player1.png')
playerImg = pygame.transform.scale(playerImg, (132, 132))
playerX = 370
playerY = 620
playerX_change = 0

# Enemy setup
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 10
for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('Assets/Asteroid.png'))
    enemyImg[i] = pygame.transform.scale(enemyImg[i], (98, 98))
    enemyX.append(random.randint(30, 930))
    enemyY.append(random.randint(50, 150))
    enemyX_change.append(1)
    enemyY_change.append(40)

# Bullet setup
bulletImg = pygame.image.load('Assets/bullet.png')
bulletImg = pygame.transform.scale(bulletImg, (32, 32))
bulletX = []
bulletY = []
bullet_state = []
bulletY_change = 1.6

# Explosion setup
explosion_spritesheet = pygame.image.load('Assets/Explode.png')

# Extract explosion frames
spritesheet_width, spritesheet_height = explosion_spritesheet.get_size()
num_frames = 8
explosion_width = spritesheet_width // num_frames
explosion_height = spritesheet_height
explosion_frames = [
    pygame.transform.scale(
        explosion_spritesheet.subsurface((i * explosion_width, 0, explosion_width, explosion_height)), (98, 98)
    )
    for i in range(num_frames)
]

# Explosion variables
explosions = []

# Power-up setup
powerupImg = pygame.image.load('Assets/powerup.png')
powerupImg = pygame.transform.scale(powerupImg, (64, 64))
powerupX = random.randint(30, 930)
powerupY = -50
powerupY_change = 1
powerup_active = False
last_powerup_score = 0  # To track the last score when a power-up was spawned

# Boss setup (150x150, slower movement)
bossImg = pygame.image.load('Assets/boss.png')
bossImg = pygame.transform.scale(bossImg, (150, 150))
bossX = 437  # Centered start position
bossY = -200
bossX_change = 1  # Slower horizontal speed
bossY_change = 0.2  # Slower vertical speed
boss_active = False
boss_health = 10  # Boss starts with 10 health points
next_boss_score = 50  # Score threshold for the next boss appearance

# Score and Lives
score_value = 0
lives = 3

def main_menu():
    menu_font = pygame.font.Font('freesansbold.ttf', 64)
    start_button_img = pygame.image.load('Assets/start_btn.png')
    start_button_img = pygame.transform.scale(start_button_img, (200, 80))
    start_button_rect = start_button_img.get_rect()
    start_button_rect.center = (512, 350)

    exit_button_img = pygame.image.load('Assets/exit_btn.png')  # Load the exit button image
    exit_button_img = pygame.transform.scale(exit_button_img, (200, 80))  # Scale the exit button
    exit_button_rect = exit_button_img.get_rect()  # Get the rect for the button
    exit_button_rect.center = (512, 450)  # Position it below the start button

    running_menu = True
    while running_menu:
        screen.fill((0, 0, 0))
        screen.blit(background, (0, 0))
        title_text = menu_font.render("SLUG BUSTER", True, (255, 255, 255))
        screen.blit(title_text, (280, 220))
        screen.blit(start_button_img, start_button_rect)
        screen.blit(exit_button_img, exit_button_rect)  # Display the exit button

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button_rect.collidepoint(event.pos):
                    running_menu = False  # Start the game if the start button is clicked
                if exit_button_rect.collidepoint(event.pos):  # Check if the exit button is clicked
                    pygame.quit()  # Close the game
                    exit()

        pygame.display.update()

def show_score_and_lives(x, y):
    score_text = font.render(f"Score: {score_value}", True, (255, 255, 255))
    screen.blit(score_text, (x, y))
    lives_text = font.render(f"Lives: {lives}", True, (255, 255, 255))
    screen.blit(lives_text, (x, y + 40))

def show_boss_health(x, y):
    if boss_active:
        health_text = font.render(f"Boss Health: {boss_health}", True, (255, 0, 0))
        screen.blit(health_text, (x, y + 80))

def show_explosions():
    for explosion in explosions:
        x, y, frame_index, timer = explosion
        screen.blit(explosion_frames[frame_index], (x, y))
        timer -= 1
        if timer % 5 == 0:
            frame_index += 1
        if frame_index >= len(explosion_frames):
            explosions.remove(explosion)
        else:
            explosion[2] = frame_index
            explosion[3] = timer

def game_over():
    global score_value, lives, playerX, playerY, enemyX, enemyY, explosions, boss_active, next_boss_score, boss_health, powerup_active, last_powerup_score
    # Display Game Over message
    game_over_text = over_font.render("GAME OVER!", True, (255, 255, 255))
    screen.blit(game_over_text, (280, 250))
    pygame.display.update()
    
    # Wait for 2 seconds before going back to the main menu
    pygame.time.wait(2000)  # Wait for 2 seconds
    
    # Reset the game state and show the main menu again
    reset_game()  # Optionally reset game variables if needed
    main_menu()  # Show the main menu

# Global variables to track boss position
last_boss_x = 437  # Default starting position for the boss
last_boss_y = -200  # Initial vertical position of the boss

def reset_game():
    global score_value, lives, playerX, playerY, enemyX, enemyY, explosions, boss_active, next_boss_score, boss_health, powerup_active, last_powerup_score, last_boss_x, last_boss_y
    # Reset the game variables
    playerX = 370
    playerY = 620
    score_value = 0
    lives = 3
    explosions = []
    boss_active = False
    next_boss_score = 50
    boss_health = 15
    powerup_active = False
    last_powerup_score = 0
    for i in range(num_of_enemies):
        enemyX[i] = random.randint(30, 930)
        enemyY[i] = random.randint(50, 150)
    
    # Reset the boss to its last position
    global bossX, bossY
    bossX = last_boss_x
    bossY = last_boss_y

def player(x, y):
    screen.blit(playerImg, (x, y))

def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))

def fire_bullet(x, y):
    screen.blit(bulletImg, (x + 50, y + 10))

def draw_boss(x, y):
    screen.blit(bossImg, (x, y))

def draw_powerup(x, y):
    screen.blit(powerupImg, (x, y))

def check_enemy_reaches_player():
    global lives
    for i in range(num_of_enemies):
        # Check for collision with the player
        if math.sqrt((enemyX[i] - playerX)**2 + (enemyY[i] - playerY)**2) < 70:  # Adjust the collision range as needed
            lives -= 1
            enemyX[i] = random.randint(30, 930)  # Reset enemy position
            enemyY[i] = random.randint(50, 150)  # Reset enemy position
            collision_sound.play()  # Play collision sound
            if lives == 0:
                game_over()  # Trigger game over when lives reach 0



# Main Game Loop
main_menu()
running = True
while running:
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -0.9
            if event.key == pygame.K_RIGHT:
                playerX_change = 0.9
            if event.key == pygame.K_SPACE:
                bulletX.append(playerX)
                bulletY.append(playerY)
                bullet_state.append("fire")

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0

    playerX += playerX_change
    playerX = max(0, min(playerX, 930))

    # Enemy movement
    for i in range(num_of_enemies):
        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0 or enemyX[i] >= 930:
            enemyX_change[i] = -enemyX_change[i]
            enemyY[i] += enemyY_change[i]

        for idx in range(len(bulletY)):
            if math.sqrt((enemyX[i] - bulletX[idx])**2 + (enemyY[i] - bulletY[idx])**2) < 27:
                collision_sound.play()
                bulletY[idx] = playerY
                bullet_state[idx] = "ready"
                score_value += 1
                explosions.append([enemyX[i], enemyY[i], 0, 40])
                enemyX[i] = random.randint(30, 930)
                enemyY[i] = random.randint(50, 150)

        enemy(enemyX[i], enemyY[i], i)

    # Bullet movement
    for idx in range(len(bulletY)):
        if bullet_state[idx] == "fire":
            fire_bullet(bulletX[idx], bulletY[idx])
            bulletY[idx] -= bulletY_change
        if bulletY[idx] <= 0:
            bullet_state[idx] = "ready"

    # Power-up logic
    if powerup_active:
        powerupY += powerupY_change
        draw_powerup(powerupX, powerupY)
        if powerupY > 768:
            powerup_active = False
        elif math.sqrt((playerX - powerupX)**2 + (playerY - powerupY)**2) < 50:  # Player collects power-up
            lives += 1
            powerup_active = False
    elif score_value >= last_powerup_score + 20:  # Spawn power-up every 20 points
        powerupX = random.randint(30, 930)
        powerupY = -50
        powerup_active = True
        last_powerup_score = score_value

    # Boss logic
    if score_value >= next_boss_score and not boss_active:  # Activate boss at score thresholds
        boss_active = True
        boss_health = 15  # Reset health for new boss
        bossX = random.randint(30, 874)

    if boss_active:
        # Boss movement
        bossY += bossY_change
        bossX += bossX_change
        if bossX <= 0 or bossX >= 874:
            bossX_change = -bossX_change
        draw_boss(bossX, bossY)
        
        if bossY > 768:  # If boss reaches the bottom
            game_over()

        # Boss collision with bullets
        for idx in range(len(bulletY)):
            if bullet_state[idx] == "fire" and math.sqrt((bossX - bulletX[idx])**2 + (bossY - bulletY[idx])**2) < 75:
                boss_hit_sound.play()
                bulletY[idx] = playerY
                bullet_state[idx] = "ready"
                boss_health -= 1
                if boss_health <= 0:
                    boss_active = False
                    next_boss_score += 50  # Set score threshold for the next boss

    check_enemy_reaches_player()
    show_explosions()
    player(playerX, playerY)
    show_score_and_lives(10, 10)
    show_boss_health(10, 70)  # Display boss health
    pygame.display.update()