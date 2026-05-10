import pygame
import random

#------------------------------------------------------------------------
# CONSTANTS

SCRNWIDTH = 720
SCRNHEIGHT = 1080
#---------------------------------------------------------------------------
class Striker(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0)):
        pygame.sprite.Sprite.__init__(self)  
        #BOOLEANS
        self.wallhit = False

        #VARIABLES
        self.pos = pos
        self.radius = 30
        self.vel_x = 0
        self.vel_y = 0

        #SPRITES
        self.image = pygame.image.load("sprites/striker.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        x,y = pygame.mouse.get_pos()
        x =  min(x+self.radius,SCRNWIDTH-self.radius)
        y = max(min(y,SCRNHEIGHT-self.radius),SCRNHEIGHT//1.5)

        self.vel_x = x - self.pos[0]
        self.vel_y = y - self.pos[1]
        self.pos = (x,y)
     
    def draw(self,surface):
        self.rect.center = self.pos
        surface.blit(self.image,self.rect)

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class Ball(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0)):
        pygame.sprite.Sprite.__init__(self)
        
        #BOOLEANS
        self.colliding_withstriker = False
        self.colliding_withblock = False
        self.colliding_wall = False
        self.explosion_ready = False
        self.living = True

        #VARIABLES
        self.lives = 6
        self.pos = pos
        self.radius = 30
        self.pos_x,self.pos_y = self.pos
        self.vel_x = 0
        self.vel_y = 0

        #IMAGES
        self.sprite = pygame.image.load("sprites/ball.png").convert_alpha()
        self.expl_sprite = pygame.image.load("sprites/ball_expl.png").convert_alpha()

        #SPRITES
        self.image = self.sprite
        self.rect = self.image.get_rect()
        self.ball_mask = pygame.mask.from_surface(self.image)

        #LISTS
        self.trails  = []


    
    def update(self,dt):

        if self.pos[1] >= SCRNHEIGHT+self.rect.height:
            self.ball_die()
            pygame.time.delay(500)
            self.living = True
            self.pos = (SCRNWIDTH//2,SCRNHEIGHT//2)
        else:
            self.apply_gravity(dt)
            self.pos = (self.pos[0]+self.vel_x,self.pos[1]+self.vel_y)
            self.check_wallclsn()           

            total_velocity = abs(self.vel_x)+abs(self.vel_y)
            if total_velocity > 60 and self.vel_y<0:
                self.explosion_ready = True
                if self.image == self.sprite:
                    self.image = self.expl_sprite
                if not len(self.trails):
                    self.trails.append(ParticleTrail(self))
                self.trails[0].update(dt)
            else:
                if self.explosion_ready and total_velocity < 20:
                    self.explosion_ready = False
                if self.image == self.expl_sprite:
                    self.image = self.sprite
                if len(self.trails):
                    del self.trails[0]

    def apply_gravity(self,dt):
        self.vel_y += (dt*0.01)  

    def play_bounce_sfx(self,volume):
        sounds = (["sounds/bounce.wav","sounds/bounce1.wav",
                  "sounds/bounce2.wav"])
        bounce_sfx = pygame.mixer.Sound(random.choice(sounds))
        bounce_sfx.set_volume(volume)
        bounce_sfx.play()

    

    def check_wallclsn(self):
        if self.colliding_wall == False:
            if self.pos[1] <= 0 + self.radius and self.vel_y < 0:
                self.play_bounce_sfx(0.2)
                self.vel_y *= -.7
                self.colliding_wall = True
                self.fast = False
            if (self.pos[0] <= 0 + self.rect.width//2 or 
                self.pos[0]  >= SCRNWIDTH - self.rect.width//2):
                self.play_bounce_sfx(0.2)
                self.vel_x *= -.7
                self.colliding_wall = True
            if self.pos[0] <= 0 + self.rect.width//2:
                self.pos = (self.rect.width//2,self.pos[1])
            if self.pos[0]  >= SCRNWIDTH - self.rect.width//2:
                self.pos = (SCRNWIDTH - self.rect.width//2,self.pos[1])

        else:
            self.colliding_wall = False

    def ball_die(self):
            pygame.mixer.stop()
            pygame.mixer.Sound("sounds/lose.wav").play()

            self.vel_x = 0
            self.vel_y = 5
            self.lives -= 1

            self.colliding_withstriker = False 
            self.living = False
    def draw(self,surface):
        if not self.living:
            return
        self.rect.center = self.pos
        if self.trails:
            self.trails[0].draw(surface)
        surface.blit(self.image,self.rect)

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class Block(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0), spacing=30):
        pygame.sprite.Sprite.__init__(self)
        #VARIABLES
        self.pos = pos
        self.spacing = spacing
        #IMAGES
        self.image = pygame.image.load("sprites/block.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.ball_mask = pygame.mask.from_surface(self.image)
        
     
    def draw(self,surface):
        self.rect.center = self.pos
        surface.blit(self.image,self.rect)
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class BlockManager():
    def __init__(self):
        self.block_poslist = []
        self.block_group = pygame.sprite.Group()
        self.spacingx = 60
        self.spacingy = 30
        self.pos = (-30,self.spacingy//2)

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
        block_spawn_snd = pygame.mixer.Sound("sounds/blockhit.wav")
        block_spawn_snd.set_volume(0.1)
        block_spawn_snd.play()
#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0)):
        pygame.sprite.Sprite.__init__(self)
        self.age = 0
        self.life=200
        self.dead = False
        self.image = pygame.image.load("sprites/expl.png").convert_alpha()
        self.ball_mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.surf = pygame.Surface((self.rect.width,self.rect.height),
                                                    pygame.SRCALPHA)
        self.surf.blit(self.image)
        expl_sfx = pygame.mixer.Sound("sounds/expl.wav")
        expl_sfx.set_volume(0.5)
        expl_sfx.play()

    def update(self, dt):
        self.age += dt
        if self.age > self.life:
            self.dead = True
        self.alpha = 255 * (1-(self.age/self.life))
        self.surf.set_alpha(self.alpha)
    
    def draw(self, surface):
        if self.dead == True:     
            return
        surface.blit(self.surf,self.rect)

#---------------------------------------------------------------------------
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
        self.surf = pygame.Surface((self.rect.width,self.rect.height),
                                                    pygame.SRCALPHA)
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

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
class ParticleTrail():
    def __init__(self, ball_object):
        self.ball_object = ball_object
        self.rect = self.ball_object.rect
        self.pos = self.ball_object.rect.x,self.ball_object.rect.y
        self.image = ball_object.image
        self.life = 100
        self.particle_list = []

    def update(self,dt):
        particle = Particle(self.pos, image=self.image, life=self.life)
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
#------------------------------------------------------------------------   
#---------------------------------------------------------------------------     
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
    green=(0,255,0)
    block_spawndelay = 1

    #BOOLEANS
    program_running = True
    game_running = False
    game_playing = False
    on_title = True
    you_lost = False
    you_win = False
    intro_running = True

    #SCREEN
    screen = pygame.display.set_mode(resolution)
    bg_image = pygame.image.load("sprites/bg.png").convert_alpha()

    #OBJECTS
    blockmanager = BlockManager()
    striker = Striker((SCRNWIDTH//2,SCRNHEIGHT//1.2)) 
    ball = Ball((SCRNWIDTH//2,SCRNHEIGHT//2))
    explosion = None
    striker_group = pygame.sprite.GroupSingle(striker)
    particletrail = ParticleTrail(ball)
    blocks = blockmanager.block_group

    while program_running:

    
        #QUIT DETECTION
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                program_running = False 
            if event.type == pygame.KEYDOWN:
                if not game_running:
                    blockmanager.block_group.remove(blocks)
                    you_lost=False
                    you_win=False
                    game_running=True
                    intro_running = True
                    striker.pos = (SCRNWIDTH//2,SCRNHEIGHT//1.2)
                    ball.pos = (SCRNWIDTH//2,SCRNHEIGHT//2)
                    ball.vel_x,ball.vel_y =(0,0)
                    ball.lives = 6
                    block_idx=0
        if game_running:

            #DRAWING BG
            screen.fill(pygame.Color(80//max(1,ball.lives),25,38))
            screen.blit(bg_image,(0,0))

            #INTRO
            if intro_running:
                game_playing=False

                if not blockmanager.block_poslist:
                    blockmanager.map_block_positions()
                    
                if block_idx < len(blockmanager.block_poslist):
                    spawn_timer += 1
                    if spawn_timer>=block_spawndelay:
                            row = Block(blockmanager.block_poslist[block_idx],
                                                        blockmanager.spacingy)   
                            blocks.add(row)
                            block_idx+=1
                            spawn_timer = 0
                            blockmanager.play_spawn_snd()
                    blockmanager._draw_blocks(screen)  
                else:
                    intro_running = False
                    spawn_timer=0
                    game_playing = True
                    pygame.mixer.set_num_channels(256)
                ball.draw(screen)   
                striker.draw(screen)   

            #GAMEPLAY
            if game_playing == True:
                #COLLISION
                if ball.pos[1]<SCRNHEIGHT//2.5:
                    if check_ball_block_collision(ball,blocks):
                        if ball.explosion_ready == True:
                            explosion = Explosion(ball.pos)
                            pygame.sprite.spritecollide(explosion, blocks, True, pygame.sprite.collide_mask)
                            ball.explosion_ready = False   
                        if len(blocks) == 0:
                            game_running = False
                            you_win = True
                else:
                    check_ball_striker_collision(ball,striker_group)

                #UPDATE
                ball.update(dt)
                striker.update()
                particletrail.update(dt) 
                if explosion:
                    explosion.update(dt)
                    if explosion.dead == True:
                        explosion = None

                #DRAWING
                ball.draw(screen)   
                striker.draw(screen)
                blockmanager._draw_blocks(screen)
                if explosion:
                    explosion.draw(screen)
                draw_text(f"Lives: {ball.lives}",
                        white,30,(15,SCRNHEIGHT-45),screen,False)   
                         
                #GAMEOVER
                if ball.lives < 1:
                    blocks_smashed = (len(blockmanager.block_poslist) - 
                                    len(blocks))
                    game_running = False
                    you_lost = True
        if not game_running:
            if on_title:
                screen.fill(black)
                draw_text("Breakout: FORCE",
                        red,60,(SCRNWIDTH//2,SCRNHEIGHT//2),screen,True)
                draw_text(f"Press any key to play",
                        white,30,(SCRNWIDTH//2,SCRNHEIGHT//2+120),screen,True)

            if you_lost:
                screen.fill(black)
                draw_text("GAME OVER",
                        red,60,(SCRNWIDTH//2,SCRNHEIGHT//2),screen,True)
                draw_text(f"You have smashed {blocks_smashed} out of {block_idx} blocks!",
                        white,30,(SCRNWIDTH//2,SCRNHEIGHT//2+60),screen,True)
                draw_text(f"Press any key to try again!",
                        white,30,(SCRNWIDTH//2,SCRNHEIGHT//2+120),screen,True)
            if you_win:
                screen.fill(black)
                draw_text("YOU WIN!",
                        green,60,(SCRNWIDTH//2,SCRNHEIGHT//2),screen,True)
                draw_text(f"You have smashed all the blocks!",
                        white,30,(SCRNWIDTH//2,SCRNHEIGHT//2+60),screen,True)
                draw_text(f"Press any key to play again!",
                        white,30,(SCRNWIDTH//2,SCRNHEIGHT//2+120),screen,True)

        pygame.display.flip()
        dt = clock.tick(60) 
    pygame.quit()

def draw_text(text,color,size,pos,surface,centered):
    sys_font = pygame.font.match_font('orbitron')
    font_obj = pygame.font.Font(sys_font,size)
    text_img = font_obj.render(text, True,(color))
    text_rect = text_img.get_rect()
    if centered:
        surface.blit(text_img,(pos[0]-(text_rect.width//2),pos[1]-
                               (text_rect.height//2)))
    else:
        surface.blit(text_img,(pos[0],pos[1]))



def check_ball_striker_collision(ball, striker_group):
    striker = striker_group.sprites()[0]
    if pygame.sprite.spritecollide(ball, striker_group, False, 
                                   pygame.sprite.collide_mask):  
        striker_pos = pygame.math.Vector2((striker.pos[0]+striker.vel_x,
                                           striker.pos[1]))
        ball_pos = pygame.math.Vector2(ball.pos)
        bs_diff = striker_pos - ball_pos
        bs_dist = bs_diff.length()
        bs_mindist = ball.rect.height//2 + striker.rect.height//2
        if bs_dist !=0:
            bs_overlap = (bs_mindist - bs_dist)
            bs_normal = bs_diff.normalize()
            ball.pos -= bs_normal*bs_overlap
            if not ball.colliding_withstriker:
                    ball.play_bounce_sfx(1)
                    ball.vel_x = -bs_normal[0]+striker.vel_x
                    ball.vel_y = striker.vel_y
                    ball.vel_y = min(max(ball.vel_y,-60),-2)              
                    ball.colliding_withstriker = True 
    else:
        ball.colliding_withstriker = False     


def check_ball_block_collision(ball, block_group):
    collided_block_list = pygame.sprite.spritecollide(ball, block_group, 
                                        True, pygame.sprite.collide_mask)
    delete_sfx = pygame.mixer.Sound("sounds/blockhit.wav")
    delete_sfx.set_volume(0.5)
    if collided_block_list:
        if not ball.colliding_withblock:
            block = collided_block_list[0]
            block_pos = pygame.math.Vector2((block.rect.centerx,
                                             block.rect.centery))
            ball_pos = pygame.math.Vector2(ball.pos)
            bb_diff = block_pos - ball_pos
            if bb_diff[0] !=0:
                bb_angle = bb_diff.normalize()
                if -bb_angle[1]*(-ball.vel_y/60) > 0:
                    ball.vel_x = bb_angle[0]*-(ball.vel_x)
                    ball.vel_y = -bb_angle[1]*(-ball.vel_y)
            delete_sfx.play()
        ball.colliding_withblock = True
    else:
        ball.colliding_withblock = False
    return collided_block_list


if __name__ == "__main__":
    main()