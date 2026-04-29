import pygame
import random

#------------------------------------------------------------------------
# CONSTANTS

SCRNWIDTH = 720
SCRNHEIGHT = 1080
#------------------------------------------------------------------------
class Striker(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0)):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.radius = 30
        self.vel_x = 0
        self.vel_y = 0

        self.image = pygame.image.load("striker.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.wallhit = False

    def update(self):
        x,y = pygame.mouse.get_pos()
        x =  min(x+self.radius,SCRNWIDTH-self.radius)
        y = max(min(y,SCRNHEIGHT-self.radius),SCRNHEIGHT//2)

        self.vel_x = x - self.pos[0]
        self.vel_y = y - self.pos[1]
        self.pos = (x,y)
     
    def draw(self,surface):
        self.rect.center = self.pos
        surface.blit(self.image,self.rect)


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0)):
        pygame.sprite.Sprite.__init__(self)
        self.lives = 3
        self.pos = pos
        self.radius = 30
        self.pos_x,self.pos_y = self.pos
        self.vel_x = 0
        self.vel_y = 0

        self.image = pygame.image.load("ball.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.ball_mask = pygame.mask.from_surface(self.image)

        self.colliding_withstriker = False
        self.colliding_withblock = False
        self.colliding_wall = False
    
    def update(self,dt):
        self.apply_gravity(dt)
        self.pos = (self.pos[0]+self.vel_x,self.pos[1]+self.vel_y)
        self.wall_collision()
        self.reset_position()  

    def apply_gravity(self,dt):
        self.vel_y += (dt*0.01)  

    def play_bounce_sfx(self,volume):
        sounds = ["bounce.wav","bounce1.wav","bounce2.wav"]
        bounce_sfx = pygame.mixer.Sound(random.choice(sounds))
        bounce_sfx.set_volume(volume)
        bounce_sfx.play()

    def wall_collision(self):
        if self.colliding_wall == False:
            #colliding from the top
            if self.pos[1] <= 0 + self.radius and self.vel_y < 0:
                self.play_bounce_sfx(0.2)
                self.vel_y *= -.7
                self.colliding_wall = True
                self.fast = False
            #colliding with the sides
            if (self.pos[0] <= 0 + self.rect.width//2 or 
                self.pos[0]  >= SCRNWIDTH - self.rect.width//2):
                self.play_bounce_sfx(0.2)
                self.vel_x *= -.7
                self.colliding_wall = True
            #reseting position if it goes past the walls
            if self.pos[0] <= 0 + self.rect.width//2:
                self.pos = (self.rect.width//2,self.pos[1])
            if self.pos[0]  >= SCRNWIDTH - self.rect.width//2:
                self.pos = (SCRNWIDTH - self.rect.width//2,self.pos[1])

        else:
            self.colliding_wall = False

    def reset_position(self):
            if self.pos[1] >= SCRNHEIGHT+self.radius:
                self.colliding_withstriker = False 
                self.pos = (SCRNWIDTH//2,SCRNHEIGHT//2)
                self.vel_x = 0
                self.vel_y = 5
                self.lives -= 1
    def draw(self,surface):
        self.rect.center = self.pos
        surface.blit(self.image,self.rect)
#---------------------------------------------------------------------------
class Particle():

    def __init__(self, pos=(0,0), image=0, life=1000):
        self.pos = pos
        self.image = image
        self.rect = self.image.get_rect()
        self.alpha = 255
        self.age = 0 
        self.life = life
        self.dead = False 
        self.surf = pygame.Surface((self.rect.width,self.rect.height),pygame.SRCALPHA)
        self.surf.blit(self.image,self.rect)

    def update(self, dt):
        self.age += dt
        if self.age > self.life:
            self.dead = True
        self.alpha = 255 * (1-(self.age/self.life))
        self.surf.set_alpha(self.alpha)
    
    def draw(self, surface):
        if self.dead == True:     
            return
        surface.blit(self.surf,self.pos)


class ParticleTrail():
    def __init__(self, ball_object):
        self.ball_object = ball_object
        self.rect = self.ball_object.rect
        self.pos = self.ball_object.rect.x,self.ball_object.rect.y
        self.image = ball_object.image
        self.life = 1000
        self.particle_list = []

    def update(self,dt):
        particle = Particle(self.pos, image=self.image, life=500)
        self.particle_list.insert(0, particle)
        self._update_pos()
        self._update_particles(dt)

    def _update_pos(self):
        x, y = (self.ball_object.rect.x,self.ball_object.rect.y)
        self.pos = (x,y)

    def _update_particles(self,dt):
        for idx,particle in enumerate(self.particle_list):
            if particle.dead:
                del self.particle_list[idx]
            particle.update(dt)

    def draw(self,surface):
        for particle in self.particle_list:
            particle.draw(surface)
#---------------------------------------------------------------------------
class Block(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0), spacing=30):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.spacing = spacing
        self.image = pygame.image.load("block.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.ball_mask = pygame.mask.from_surface(self.image)
        
     
    def draw(self,surface):
        self.rect.center = self.pos
        surface.blit(self.image,self.rect)
#---------------------------------------------------------------------------
class BlockManager():
    def __init__(self):
        self.block_poslist = []
        self.block_group = pygame.sprite.Group()
        self.spacingx = 60
        self.spacingy = 30
        self.pos = (-30,self.spacingy)

    def map_block_positions(self):
        x,y=self.pos[0],self.pos[1]
        for column in range(0,10):
            for row in range(0,SCRNWIDTH,self.spacingx):
                x+=self.spacingx
                self.pos = (x,y)
                self.block_poslist.append(self.pos)
            x = -self.spacingx//2
            y+=30
        return True

    def _draw_blocks(self,surface):
        for idx,block in enumerate(self.block_group):
            block.draw(surface)    
    

    def play_spawn_snd(self):
        pygame.mixer.set_num_channels(1)
        block_spawn_snd = pygame.mixer.Sound("blockhit.wav")
        block_spawn_snd.set_volume(0.1)
        block_spawn_snd.play()
#------------------------------------------------------------------------        
def main():

    pygame.init()
    pygame.font.init
    pygame.display.set_caption("Breakout:Force")
    pygame.mouse.set_visible(False)
    clock= pygame.time.Clock()
    
    #VALUES
    dt = 0.0
    resolution =(SCRNWIDTH,SCRNHEIGHT)
    black = pygame.Color(0,0,0)
    spawn_timer = 0
    block_idx = 0
    blocks_smashed = 0
    red=(255,0,0)
    white=(255,255,255)

    #BOOLEANS
    running = True
    playing = False
    game_over = False
    spawning_blocks = True

    #OBJECTS
    screen= pygame.display.set_mode(resolution)

    blockmanager = BlockManager()

    striker = Striker((SCRNWIDTH//2,SCRNHEIGHT//1.2)) 
    ball = Ball((SCRNWIDTH//2,SCRNHEIGHT//2))

    ball_group = pygame.sprite.GroupSingle(ball)
    striker_group = pygame.sprite.GroupSingle(striker)
    particletrail = ParticleTrail(ball)


    blockmanager.map_block_positions()

    while running:
    
        #QUIT DETECTION
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
            if game_over == True:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        blockmanager.block_group.remove(blockmanager.block_group)
                        game_over=False
                        playing=False
                        ball.lives = 3
                        block_idx=0
                        spawning_blocks = True

            #if r key is pressed and game over is true
                #restart the game by setting playing to false and spawning blocks to true
        screen.fill(black)

        #SPAWNING BLOCKS
        if spawning_blocks:
            if block_idx < len(blockmanager.block_poslist):
                spawn_timer += 1
                if spawn_timer>=1:
                        row = Block(blockmanager.block_poslist[block_idx],blockmanager.spacingy)   
                        blockmanager.block_group.add(row)
                        block_idx+=1
                        spawn_timer = 0
                        blockmanager.play_spawn_snd()
                blockmanager._draw_blocks(screen)  
                total_blocks = block_idx
            else:
                 spawning_blocks = False
                 spawn_timer=0
                 playing = True
                 pygame.mixer.set_num_channels(256)
            ball.draw(screen)   
            striker.draw(screen)   

        #game running
        if playing == True and not game_over:

            #checking for collision
            if ball.pos[1]<SCRNHEIGHT//2:
                check_ball_block_collision(ball,blockmanager.block_group)
            else:
                check_ball_striker_collision(ball,striker_group)

            #updating
            ball.update(dt)
            striker.update()
            particletrail.update(dt)

            #drawing on screen
            particletrail.draw(screen)
            ball.draw(screen)   
            striker.draw(screen)
            blockmanager._draw_blocks(screen)
            draw_text(f"Lives: {ball.lives}",
                      white,30,(0,SCRNHEIGHT-30),screen,False)            

            #checking for gameover
            if ball.lives < 1:
                blocks_smashed = (len(blockmanager.block_poslist) - 
                                  len(blockmanager.block_group))
                playing = False
                game_over = True
        #game over
        if game_over == True and not playing:
            draw_text("GAME OVER",
                      red,60,(SCRNWIDTH//2,SCRNHEIGHT//2),screen,True)
            draw_text(f"you have smashed {blocks_smashed} out of {block_idx} blocks!",
                      white,30,(SCRNWIDTH//2,SCRNHEIGHT//2+60),screen,True)
            draw_text(f"press r to try again",
                      white,30,(SCRNWIDTH//2,SCRNHEIGHT//2+120),screen,True)

        #add win condition

        pygame.display.flip()
        dt = clock.tick(60)
    pygame.quit()

def draw_text(text,color,size,pos,surface,centered):
    sys_font = pygame.font.get_default_font()
    font_obj = pygame.font.Font(sys_font,size)
    text_img = font_obj.render(text, False,(color))
    text_rect = text_img.get_rect()
    if centered:
        surface.blit(text_img,(pos[0]-(text_rect.width//2),pos[1]-
                               (text_rect.height//2)))
    else:
        surface.blit(text_img,(pos[0],pos[1]))



def check_ball_striker_collision(ball, striker_group):
    #set striker varaible 
    striker = striker_group.sprites()[0]
    #if the ball is touching the striker
    if pygame.sprite.spritecollide(ball, striker_group, False, pygame.sprite.collide_mask):  
        #set positions of each ball
        striker_pos = pygame.math.Vector2((striker.pos[0]+striker.vel_x,striker.pos[1]))
        ball_pos = pygame.math.Vector2(ball.pos)
        #determine the distance 
        bs_diff = striker_pos - ball_pos
        bs_dist = bs_diff.length()
        bs_mindist = ball.rect.height//2 + striker.rect.height//2
        #prevenets normalizing a zero variable
        if bs_dist !=0:
            bs_overlap = (bs_mindist - bs_dist)
            bs_normal = bs_diff.normalize()
            #pops out ball before it renders
            ball.pos -= bs_normal*bs_overlap
            #if it wasnt originally colliding
            if not ball.colliding_withstriker:
                    ball.play_bounce_sfx(1)
                    #set ball velocity to the strikers velocity
                    ball.vel_x = -bs_normal[0]+striker.vel_x
                    ball.vel_y = striker.vel_y
                    #cap vertical velocity at -60
                    ball.vel_y = min(max(ball.vel_y,-60),-2)    
                    #set it as true to prevent it repeating each frame             
                    ball.colliding_withstriker = True 
    #if ball is not touching the striker, set it to 0.
    else:
        ball.colliding_withstriker = False     


def check_ball_block_collision(ball, block_group):
    #gets a list of all of the blocks
    collided_block_list = pygame.sprite.spritecollide(ball, block_group, True, pygame.sprite.collide_mask)
    #sound stuff
    delete_sfx = pygame.mixer.Sound("blockhit.wav")
    delete_sfx.set_volume(0.5)

    if collided_block_list:
        if not ball.colliding_withblock:
            #plays sound
            #set the position of the first block that it collides list
            block = collided_block_list[0]
            #set the positions of each
            block_pos = pygame.math.Vector2((block.rect.centerx,block.rect.centery))
            ball_pos = pygame.math.Vector2(ball.pos)
            #calculates the different between the positions 
            bb_diff = block_pos - ball_pos
            #to avoid normalizing 0
            if bb_diff[0] !=0:
                #calcuates angle the ball will go in
                bb_angle = bb_diff.normalize()
                if -bb_angle[1]*(-ball.vel_y/60) > 0:
                    ball.vel_x = bb_angle[0]*-(ball.vel_x)
                    ball.vel_y = -bb_angle[1]*(-ball.vel_y)
                    print(f"({ball.vel_x},{ball.vel_y})")
                    delete_sfx.play()
        ball.colliding_withblock = True
    else:
        ball.colliding_withblock = False            


if __name__ == "__main__":
    main()