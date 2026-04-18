import pygame
import time

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
        #self.mask_image = self.mask.to_surface()

        self.wallhit = False

    def update(self):
        x,y = pygame.mouse.get_pos()
        x =  min(x+self.radius,SCRNWIDTH-self.radius)
        y = max(min(y,SCRNHEIGHT-self.radius),SCRNHEIGHT//2)

        self.vel_x = x - self.pos[0]
        self.vel_y = y - self.pos[1]
        self.pos = (x,y)
        #self.draw(surface)  
     
    def draw(self,surface):
        self.rect.center = self.pos
        surface.blit(self.image,self.rect)


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0)):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.radius = 30
        self.pos_x,self.pos_y = self.pos
        self.vel_x = 0
        self.vel_y = 0

        self.image = pygame.image.load("ball.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.ball_mask = pygame.mask.from_surface(self.image)
        #self.ball_mask_image = self.ball_mask.to_surface()

        self.was_colliding = False
        self.colliding_wall = False
        #self.image.fill(self.colorbg)
        

    def update(self,dt):
        self.vel_y += (dt*0.01)
        self.pos = (self.pos[0]+self.vel_x,self.pos[1]+self.vel_y)
        self.wall_collision()
        self.reset_position()
        #self.draw(surface)       

    def draw(self,surface):
        self.rect.center = self.pos
        surface.blit(self.image,self.rect)

    def wall_collision(self):
        if self.colliding_wall == False:
            #from top
            if self.pos[1] <= 0 + self.radius and self.vel_y < 0:
                self.vel_y *= -.7
                self.colliding_wall = True
                #print("Hit Cieling")
                self.fast = False
            if (self.pos[0] <= 0 + self.rect.width//2 or 
                self.pos[0]  >= SCRNWIDTH - self.rect.width//2):
                self.vel_x *= -.7
                self.colliding_wall = True
                #print("Hit Wall")
            if self.pos[0] <= 0 + self.rect.width//2:
                self.pos = (self.rect.width//2,self.pos[1])
            if self.pos[0]  >= SCRNWIDTH - self.rect.width//2:
                self.pos = (SCRNWIDTH - self.rect.width//2,self.pos[1])

        else:
            self.colliding_wall = False

    def reset_position(self):
            if self.pos[1] >= SCRNHEIGHT+self.radius:
                self.pos = (SCRNWIDTH//2,SCRNHEIGHT//2)
                self.vel_x = 0
                self.vel_y = 5
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
        self.block_list = []
        self.block_group = pygame.sprite.Group()
        self.spacingx = 60
        self.spacingy = 30
        self.pos = (-30,self.spacingy)

    def spawn_blocks(self):
        x,y=self.pos[0],self.pos[1]
        for column in range(0,10):
            for row in range(0,SCRNWIDTH,self.spacingx):
                x+=self.spacingx
                self.pos = (x,y)
                #row = Block(self.pos,self.spacingy)   
                #self.block_group.add(row)
                self.block_list.append(self.pos)
                #print(self.block_list)
            x = -self.spacingx//2
            y+=30
        return True

    def _draw_blocks(self,surface):
        for idx,block in enumerate(self.block_group):
            block.draw(surface)    
#------------------------------------------------------------------------        
def main():

    pygame.init()
    pygame.display.set_caption("Breakout:Force")
    pygame.mouse.set_visible(False)
    clock= pygame.time.Clock()
    
    #VALUES
    dt = 0.0
    resolution =(SCRNWIDTH,SCRNHEIGHT)
    black = pygame.Color(0,0,0)

    #OBJECTS
    screen= pygame.display.set_mode(resolution)

    blockmanager = BlockManager()

    striker = Striker((SCRNWIDTH//2,SCRNHEIGHT//1.2)) 
    ball = Ball((SCRNWIDTH//2,SCRNHEIGHT//2))

    ball_group = pygame.sprite.Group(ball)
    striker_group = pygame.sprite.Group(striker)

    running = True
    game_running = False
    big_hit_occurring = False
    spawning_blocks = True
    blockmanager.spawn_blocks()
    spawn_timer = 0
    block_idx = 0
    while running:
        #QUIT DETECTION
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False   
        screen.fill(black)
        #SPAWNING BLOCKS
        if spawning_blocks:
            if block_idx < len(blockmanager.block_list):
                spawn_timer += 1
                if spawn_timer>=1:
                        row = Block(blockmanager.block_list[block_idx],blockmanager.spacingy)   
                        blockmanager.block_group.add(row)
                        block_idx+=1
                        spawn_timer = 0
                blockmanager._draw_blocks(screen)
                ball.draw(screen)   
                striker.draw(screen)                 
            else:
                 spawning_blocks = False
                 spawn_timer=0
        
        if not spawning_blocks and not big_hit_occurring:
            #checking for collision
            if ball.pos[1]<SCRNHEIGHT//2:
                check_ball_block_collision(ball,blockmanager.block_group)
            else:
                check_ball_striker_collision(ball,striker_group)
            #updating
            ball.update(dt)
            striker.update()
            blockmanager._draw_blocks(screen)
            #drawing on screen
            #pygame.draw.line(screen,pygame.Color(255,0,0),(ball.pos[0],ball.pos[1]),(striker.pos[0],striker.pos[1]),10)
            ball.draw(screen)   
            striker.draw(screen)  

        pygame.display.flip()
        dt = clock.tick(60)
    pygame.quit()

def check_ball_striker_collision(ball, striker_group):
    striker = striker_group.sprites()[0]
    if pygame.sprite.spritecollide(ball, striker_group, False, pygame.sprite.collide_mask):  
        striker_pos = pygame.math.Vector2((striker.pos[0]+striker.vel_x,striker.pos[1]+striker.vel_y))
        ball_pos = pygame.math.Vector2(ball.pos)
        diff = striker_pos - ball_pos
        dist = diff.length()
        mindist = ball.rect.height//2 + striker.rect.height//2
        if dist !=0:
            overlap = mindist - dist
            normal = diff.normalize()
            ball.pos -= normal*overlap
            if not ball.was_colliding:
                    ball.vel_x = normal[0]+striker.vel_x
                    ball.vel_y = normal[1]+(striker.vel_y/2)
                    ball.vel_y = min(max(ball.vel_y,-60),-2)                 
                    ball.was_colliding = True
    else:
        ball.was_colliding = False    


def check_ball_block_collision(ball, block_group):
    collided_block_list = pygame.sprite.spritecollide(ball, block_group, True, pygame.sprite.collide_mask)
    if collided_block_list:
        print(collided_block_list)
        if not ball.was_colliding:
            for idx,block in enumerate(collided_block_list):
                block_pos = pygame.math.Vector2((block.rect.centerx,block.rect.centery))
            ball_pos = pygame.math.Vector2(ball.pos)
            angle = block_pos - ball_pos
            if angle[0] !=0 and angle[0] !=0:
                angle.normalize()
                print(angle)
                if -angle[1]*(-ball.vel_y/60) > 0:
                    ball.vel_x = angle[0]*-(ball.vel_x/60)
                    ball.vel_y = -angle[1]*(-ball.vel_y/60)
        ball.was_colliding = True
    else:
        ball.was_colliding = False            


if __name__ == "__main__":
    main()