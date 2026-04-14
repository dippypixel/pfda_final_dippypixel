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

        self.image = pygame.image.load("striker.png").convert_alpha()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        #self.mask_image = self.mask.to_surface()

        self.wallhit = False

    def update(self):
        x,y = pygame.mouse.get_pos()
        x =  min(x,SCRNWIDTH-self.radius)
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

    def ball_striker_collision(self,striker):
            if abs(striker.vel_x)+abs(striker.vel_y)> 5:
                self.vel_x,self.vel_y = striker.vel_x,striker.vel_y
            else:
                self.vel_x = (self.rect.centerx-striker.rect.centerx)*.1
                self.vel_y *= -.7
                self.vel_y = min(self.vel_y,-2)
            print("Hit Paddle")

    def wall_collision(self):
        if self.colliding_wall == False:
            #from top
            if self.pos[1] <= 0 + self.radius and self.vel_y < 0:
                self.vel_y *= -.7
                self.colliding_wall = True
                print("Hit Cieling")
                self.fast = False
            if (self.pos[0] <= 0 + self.radius//2
                or self.pos[0]  >= SCRNWIDTH - self.radius*2):
                self.vel_x *= -.7
                self.colliding_wall = True
                print("Hit Wall")
        else:
            self.colliding_wall = False

    def reset_position(self):
            if self.pos[1] >= SCRNHEIGHT+self.radius:
                self.pos = (SCRNWIDTH//2,SCRNHEIGHT//5)
                self.vel_x = 0
                self.vel_y = 5


class Ball_Particle(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0),color=(0,255,0)):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.radius = 30
        self.age=0
        self.image = pygame.Surface((self.radius*2,self.radius*2),pygame.SRCALPHA)
        self.color = (0,255,0)
        pygame.draw.circle(self.image, self.color,
                           (self.radius,self.radius),self.radius)
        

    def update(self,dt):
        self.age += dt   
        if self.age > self.life:
            self.dead = True 

    def draw(self,surface):
        self.rect.center = self.pos
        if self.dead:
            return
        else:
            surface.blit(self.image,self.rect)
                
#---------------------------------------------------------------------------
class Block(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0), radius=30):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.radius = radius
        self.image = pygame.Surface((self.radius,self.radius),pygame.SRCALPHA)
        self.rect = self.image.get_rect() 
        self.rect.width *=0.9
        self.rect.height *=0.9
        self.color = (255,0,0)
        self.colorbg = (0,0,0)
        self.image.fill(self.colorbg)
        pygame.draw.rect(self.image, self.color,self.rect)
        self.wallhit = False
     
    def draw(self,surface):
        self.rect.center = self.pos
        surface.blit(self.image,self.rect)
#---------------------------------------------------------------------------
class BlockManager():
    def __init__(self):
        self.block_list = []
        self.block_group = pygame.sprite.Group()
        self.spacing = 30
        self.pos = (0,self.spacing)

    def spawn_blocks(self):
        x,y=self.pos[0],self.pos[1]
        for column in range(0,10):
            print("column")
            for row in range(0,SCRNWIDTH-self.spacing,self.spacing):
                x+=self.spacing
                self.pos = (x,y)
                row = Block(self.pos,self.spacing)   
                self.block_group.add(row)
            x = 0
            y+=30

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

    # blockmanager = BlockManager()
    # blockmanager.spawn_blocks()

    striker = Striker((SCRNWIDTH//2,SCRNHEIGHT//2)) 
    ball = Ball((SCRNWIDTH//2,SCRNHEIGHT//2))

    ball_group = pygame.sprite.Group(ball)
    striker_group = pygame.sprite.Group(striker)

    running = True
    while running:
        #QUIT DETECTION
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False   
        screen.fill(black)
        ball.update(dt)
        striker.update()
        # blockmanager._draw_blocks(screen)
    # ball_striker_collide = pygame.sprite.spritecollide(striker,ball_group,False,pygame.sprite.collide_mask)

    # for circle in ball_striker_collide:
    #     if not circle.was_colliding:
    #         circle.pos = circle.pos[0],(striker.pos[1]-(circle.radius*2)+striker.vel_y)
    #         circle.ball_striker_collision(striker)
    #         print("Bounced!")
    #     circle.was_colliding = True
    # for circle in ball_group:
    #     if circle not in ball_striker_collide:
    #         circle.was_colliding = False

        ball.draw(screen)   
        striker.draw(screen)  

        if pygame.sprite.spritecollide(ball, striker_group, False, pygame.sprite.collide_mask):
            if not ball.was_colliding:
                ball.ball_striker_collision(striker)
                print("Bounced!")
            ball.was_colliding = True
        else:
            ball.was_colliding = False

        # ball_block_collide = pygame.sprite.spritecollide(ball,blockmanager.block_group,True)
        # if ball_block_collide:
        #     ball.vel_y *= -.9   

    

        pygame.display.flip()
        dt = clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()