import pygame
import os
import random
import pygame.sprite

pygame.init()
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Escape")

# Load images
RED_SPACE_SHIP = pygame.transform.rotate(pygame.image.load(os.path.join("assets", "redship.png")),180)
RED_SPACE_SHIP = pygame.transform.scale(RED_SPACE_SHIP, (80, 80))

GREEN_SPACE_SHIP = pygame.transform.rotate(pygame.image.load(os.path.join("assets", "greenship.png")),180)
GREEN_SPACE_SHIP = pygame.transform.scale(GREEN_SPACE_SHIP, (60, 60))

BLUE_SPACE_SHIP = pygame.transform.rotate(pygame.image.load(os.path.join("assets", "blueship.png")),180)
BLUE_SPACE_SHIP = pygame.transform.scale(BLUE_SPACE_SHIP, (50, 50))

# Player spaceship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "spaceship.png"))
YELLOW_SPACE_SHIP = pygame.transform.scale(YELLOW_SPACE_SHIP, (90, 90))

#Boss
BOSS_SPACE_SHIP = pygame.image.load(os.path.join("assets", "boss1.png"))
BOSS_SPACE_SHIP = pygame.transform.scale(BOSS_SPACE_SHIP, (200, 200))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
SHOOT_SOUND = pygame.mixer.Sound(os.path.join("assets", "pew.wav"))
ENEMY_DEATH_SOUND = pygame.mixer.Sound(os.path.join("assets", "expl3.wav"))

# Items
HEALTH_PACK = pygame.image.load(os.path.join("assets", "health_pack.png"))
HEALTH_PACK = pygame.transform.scale(HEALTH_PACK, (50,50))

LASER_BEAM = pygame.image.load(os.path.join("assets", "laser_beam.png"))
LASER_BEAM = pygame.transform.scale(LASER_BEAM, (50, 50))

SHIELD = pygame.image.load(os.path.join("assets", "shield.png"))
SHIELD = pygame.transform.scale(SHIELD, (50, 50))

#destruction animation
destruction_effects = pygame.sprite.Group()

#background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "bg.jpg")), (WIDTH, HEIGHT))

class Laser: #Laser 
    def __init__(self, x, y, img): #initial area
        self.x = x - 5 #its position in the x axis.
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window): #draw
        window.blit(self.img, (self.x, self.y))

    def move(self, vel): #moving 
        self.y += vel

    def off_screen(self, height): #goes off screen
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        if isinstance(obj, Player) and obj.is_shielded:
            return False #if shielded then dont allow collision for lasers and player
        return collide(self, obj)


class Ship: #Ship. General... Will be used for Player and Enemy
    COOLDOWN = 30 #shooting speed

    def __init__(self, x, y, health=100): #100 for health
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window): #draw the lasers
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers: 
            laser.draw(window)

    def move_lasers(self, vel, obj): #move lasers depending on cool down so they hve spaces in between
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel) #move in a certain velocity
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj): #if playe hits an enemy then the enemy's health -5
                obj.health -= 5
                self.lasers.remove(laser) #remove laser

    def cooldown(self): #cooldown for the spaces between continuous shooting
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self): #shooting of player
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            SHOOT_SOUND.play()
            

    def get_width(self): #get with of the image of ship
        return self.ship_img.get_width()

    def get_height(self): #height of the ship
        return self.ship_img.get_height()

class Player(Ship): #player
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER #the ship
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.equipped_item = None #init
        self.is_shielded = False #not yet shielded
        self.shield_end_time = 0 #count time for shield
        self.points = 0 #points in game
        
        

    def move_lasers(self, vel, objs): #lasers moving
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT): #remove if goes out
                self.lasers.remove(laser)
            else:
                for obj in objs: #if laser hits enemy
                    if laser.collision(obj):
                        obj.health -= self.get_laser_damage() #minus health
                        try:
                            self.lasers.remove(laser)
                        except ValueError:
                            pass
                        if obj.health <= 0: #if health is 0 then remove
                        
                            destruction_effect = DestructionEffect(obj.x+30, obj.y)
                            destruction_effects.add(destruction_effect)
                            objs.remove(obj)
                            

                            if isinstance(obj, Boss):  # Check if the defeated enemy is the boss
                                #sound of boss death
                                BOSS_DEFEAT_SOUND = pygame.mixer.Sound(os.path.join("assets", "bossdeath.wav"))
                                BOSS_DEFEAT_SOUND.play()  # Play the boss defeat sound
                            else:
                                #normal enemy death
                                ENEMY_DEATH_SOUND.play()
                                
                            
                        if obj.ship_img == BLUE_SPACE_SHIP:
                            self.points += 1 #1 pt for blue ship
                        elif obj.ship_img == GREEN_SPACE_SHIP:
                            self.points += 2 #2 pts for green ship
                        elif obj.ship_img == RED_SPACE_SHIP:
                            self.points += 3 #3 pts for red ship


    def draw(self, window): #draw the spaceship 
        super().draw(window)
        self.healthbar(window)

        # Draw equipped item (laserbeam)(middle of spaceship)
        if self.equipped_item is not None:
            window.blit(self.equipped_item.img, (self.x + self.ship_img.get_width() // 2 - self.equipped_item.img.get_width() // 2, self.y + self.ship_img.get_height() // 2 - self.equipped_item.img.get_height() // 2))

        # Draw shield around the spaceship
        if self.is_shielded:
            pygame.draw.circle(window, (0, 255, 0), (self.x + self.ship_img.get_width() // 2, self.y + self.ship_img.get_height() // 2), self.ship_img.get_width() // 2, 2)

        
        # Draw points label
        points_label = pygame.font.SysFont("futura", 30).render(f"Points: {self.points}", 1, (255, 255, 255))
        window.blit(points_label, (10, 50))

    def healthbar(self, window): #draw the healthbar
        pygame.draw.rect(window, (225, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10)) #red
        if not self.is_shielded: #turn the green to gray
            pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))
        else: #previous health... green again. (add the laser damage to the health)
            previous_health = self.health + self.get_laser_damage()
            pygame.draw.rect(window, (128, 128, 128), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (previous_health / self.max_health), 10))

        # Display current health
        health_label = pygame.font.SysFont("futura", 20).render(f"Health: {self.health}", 1, (255, 255, 255))
        window.blit(health_label, (self.x, self.y + self.ship_img.get_height() + 25))


    def equip_item(self, item): #equip an item
        self.equipped_item = item

    def get_laser_damage(self): #laser damage
        return 5

    def update(self): #update for when it has items
        if self.is_shielded and pygame.time.get_ticks() >= self.shield_end_time:
            self.is_shielded = False #if shield for 10s end. remove shield effect

        if self.equipped_item is not None and isinstance(self.equipped_item, LaserBeam) and self.equipped_item.is_active:
            if pygame.time.get_ticks() >= self.equipped_item.start_time + self.equipped_item.duration:
                self.equipped_item.update(self)
                #remove laser beam effect after 10 seconds



class Enemy(Ship): #enemy spaceships
    #different colors and their health
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER, 15),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER, 10),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER, 5)
    }

    def __init__(self, x, y, color, health=None):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img, self.max_health = self.COLOR_MAP[color]
        self.health = health if health is not None else self.max_health
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.is_boss = False


    def move(self, vel): #moveee
        self.y += vel

    def shoot(self): #shooting of the enemy
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser) 
            self.cool_down_counter = 1

    def draw(self, window): #draw spacehips for enemies
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window): #healthbar of enemy
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))

class Boss(Ship): #boss enemy 
    def __init__(self, x, y, health=60): #initial health of 60
        super().__init__(x, y, health)
        self.ship_img = BOSS_SPACE_SHIP
        self.laser_img = RED_LASER
        self.max_health = health
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.cool_down_counter = 0
        self.is_boss = True
        

    def move(self, vel):
        self.y += vel

    def shoot(self): #Its 2 lasers
        if self.cool_down_counter == 0:
            #two lasers for boss
            laser1 = Laser(self.x-40, self.y + self.ship_img.get_height(), self.laser_img)
            laser2 = Laser(self.x + self.ship_img.get_width() - 40, self.y + self.ship_img.get_height(), self.laser_img)
            
            self.lasers.append(laser1)
            self.lasers.append(laser2)

            self.cool_down_counter = 1

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

        # Draw health number on top of the boss's head
        health_font = pygame.font.SysFont("futura", 20)
        health_label = health_font.render(f"Health: {self.health}", 1, (255, 255, 255))
        window.blit(health_label, (self.x + self.ship_img.get_width() // 2 - health_label.get_width() // 2, self.y - health_label.get_height() - 5))

    def healthbar(self, window):#boss healthbar
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))


class Item: #ITEMS
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        
        return collide(self, obj)


class HealthPack(Item): #HEALTHPACK
    def __init__(self, x, y):
        super().__init__(x, y, HEALTH_PACK)

    def apply_effect(self, player):
        player.health = player.max_health  # Restore full health 


class LaserBeam(Item): #LASERBEAM
    def __init__(self, x, y):
        super().__init__(x, y, LASER_BEAM)
        self.duration = 10000  # Duration of the laser beam effect in milliseconds
        self.start_time = 0  # Start time of the laser beam effect
        self.is_active = False  # Flag to track if the laser beam effect is active

    def apply_effect(self, player):
        if not player.equipped_item or (player.equipped_item and not isinstance(player.equipped_item, LaserBeam)):
            player.equip_item(self)  # Equip the laser beam
            player.COOLDOWN -= 10 #Make shooting faster
            self.start_time = pygame.time.get_ticks()  # Record the start time
            self.is_active = True  # Activate the laser beam effect
            

    def update(self, player):
        if self.is_active and pygame.time.get_ticks() >= self.start_time + self.duration:
            player.COOLDOWN += 10 #back to normal shooting speed
            self.is_active = False #remove
            player.equipped_item = None  # Remove the laser beam from the player's equipped item


class Shield(Item): #SHIELD
    def __init__(self, x, y):
        super().__init__(x, y, SHIELD)

    def apply_effect(self, player):
        player.is_shielded = True
        player.shield_end_time = pygame.time.get_ticks() + 10000  # Shield lasts for 10 seconds

    def update(self, player): #After set amount of time, shield fades
        if player.is_shielded and pygame.time.get_ticks() >= player.shield_end_time:
            player.is_shielded = False


def collide(obj1, obj2):#collision check for the two objects that collide
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

class DestructionEffect(pygame.sprite.Sprite): #for destruction animation
    def __init__(self, x, y):
        super().__init__()
        frames = [
            pygame.transform.scale(pygame.image.load(os.path.join("assets", "expl1.png")), (50, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("assets", "expl2.png")), (50, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("assets", "expl3.png")), (50, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("assets", "expl4.png")), (50, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("assets", "expl5.png")), (50, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("assets", "expl6.png")), (50, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("assets", "expl7.png")), (50, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("assets", "expl8.png")), (50, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("assets", "expl9.png")), (50, 50)),
            ]

        self.frames = frames
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.frame_index = 0
        self.animation_speed = 0.5  # Adjust the speed of the animation

    def update(self):
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.frames):
            self.kill()  # Remove the sprite from the group
        else:
            self.image = self.frames[int(self.frame_index)]

########################################################MAIN
def main():
    run = True
    FPS = 60
    level = 0
    lives = 5

    main_font = pygame.font.SysFont("futura", 30)
    lost_font = pygame.font.SysFont("futura", 30)

    enemies = []
    items = []  # Added items list
    wave_length = 5
    enemy_vel = 1

    player_vel = 5
    laser_vel = 5

    player = Player(300, 630)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    def create_enemies(level):
        enemy_colors = ["blue"]
        if level >= 2:
            enemy_colors.append("green")
        if level >= 3:
            enemy_colors.append("red")

        if level % 4 == 0:  # Check if level is divisible by 4
            boss_sound = pygame.mixer.Sound(os.path.join("assets", "boss.wav"))
            boss_sound.play()
            boss_health = 60 + 10 * ((level - 1) // 4) if level != 4 else 60

            boss = Boss(WIDTH // 2 - BOSS_SPACE_SHIP.get_width() // 2, -150, health=boss_health)
            enemies.append(boss)

            
        else:
            for i in range(wave_length):
                color = random.choice(enemy_colors)
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100), color)
                enemies.append(enemy)


            for it in range(5):  # Spawn a maximum of 5 items in each level
                spawn_item = random.choice([HealthPack, LaserBeam, Shield])
                item = spawn_item(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100))
                items.append(item)



    def redraw_window():
        WIN.blit(BG, (0, 0))

        # Draw lives and level. update real time
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))
        
        # Get the widths of the labels
        level_width = level_label.get_width()

        WIN.blit(lives_label, (10, 10)) 
        WIN.blit(level_label, (WIDTH - level_width - 10, 10))

        for enemy in enemies: #draw the enemies
            enemy.draw(WIN)

        player.draw(WIN) #draw player
        
        player.healthbar(WIN)  #draw the healthbar and player health txt
        destruction_effects.draw(WIN)

        for item in items: #draw items
            item.draw(WIN)

        if lost: #if lost display "you lost"
            lost_label = lost_font.render("You Lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        #control the player forward,backward,and sideward
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:
             player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False


        #GAME OVER
        if lives <= 0:
            lost = True
            lost_count += 1 
            if lost_count > FPS * 3: #after 3 seconds the game will end
                run = False
                continue

        if lost: #if lost then continue
            continue
        
        #If player health is 0 for current life bar
        if player.health <= 0:
            player.health = 100 #then make it 100  again 
            lives -= 1 #because the life goes down everytime it refreshes

        #If there are no enemies in the current 
        if len(enemies) == 0:
            level += 1 #go to the next level
            wave_length += 5 #make the wave bigger (more enemies)
            create_enemies(level)

        #ENEMY MOVEMENT
        for enemy in enemies[:]: #move the enemy
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player) #and its lasers


            if random.randrange(0, 2 * 60) == 1: #so not all shoot right after it comes out. Random
                enemy.shoot()


            #ENEMY COLLIDES WITH PLAYER
            if collide(enemy, player):  # If enemy and player collide
                if isinstance(enemy, Boss):  # Check if it's a boss enemy
                    lives = 0  # Set lives to 0 to trigger game over
                    break  # Exit the loop

                player.health -= 10  # -10 health for player
                enemies.remove(enemy)  # remove enemy

            #ENEMY PASSING
            elif enemy.y + enemy.get_height() > HEIGHT: #if enemy not shot and passes by
                if isinstance(enemy, Boss):  # Check if it's a boss enemy
                    lives = 0  # Set lives to 0 to trigger game over
                    break  # Exit the loop
                else:
                    lives -= 1 #-1 in life
                    enemies.remove(enemy) #remove it

            
                
        #ITEM USAGE
        for item in items[:]:
            item.move(enemy_vel) #spawn like enemy
            if collide(item, player): #if collide with player
                item_pickup_sound = pygame.mixer.Sound(os.path.join("assets", "equip.wav"))
                item_pickup_sound.play()

                item.apply_effect(player) #use effect
                items.remove(item)

        

        player.move_lasers(-laser_vel, enemies)
        player.update()
        destruction_effects.update()

    pygame.quit()

#For the home screen
def main_menu():
    pygame.mixer.music.load(os.path.join("assets", "background_music.mp3"))
    pygame.mixer.music.play(-1)
    title_font = pygame.font.SysFont("futura", 90)  # Increase the font size for the title
    subtitle_font = pygame.font.SysFont("futura", 30)  # Define a smaller font size for the subtitle
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("SPACE ESCAPE", 1, (255, 255, 255))  # Add the title "Space Escape"
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 200))  # Position the title at the center
        subtitle_label = subtitle_font.render("Press any key to begin...", 1, (255, 255, 255))  # Use the smaller font size for the subtitle
        WIN.blit(subtitle_label, (WIDTH / 2 - subtitle_label.get_width() / 2, 400))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

main_menu()
