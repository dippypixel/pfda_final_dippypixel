import pygame
import time
#------------------------------------------------------------------------
# CONSTANTS

SCRNWIDTH = 720
SCRNHEIGHT = 1080
#------------------------------------------------------------------------
class Striker(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0), radius=30):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.radius = radius
        self.image = pygame.Surface((self.radius*2,self.radius*2),pygame.SRCALPHA)
        self.rect = self.image.get_rect() 
        self.color = (0,0,255)
        self.colorbg = (255,0,0)
        #self.image.fill(self.colorbg)
        pygame.draw.circle(self.image, self.color,
                           (self.radius,self.radius),self.radius)
        self.wallhit = False

    def update(self,surface):
        x,y = pygame.mouse.get_pos()
        x =  min(x,SCRNWIDTH-self.radius)
        y = max(min(y,SCRNHEIGHT-self.radius),SCRNHEIGHT//2)

        self.vel_x = x - self.pos[0]
        self.vel_y = y - self.pos[1]
        self.pos = (x,y)
        self.draw(surface)  
     
    def draw(self,surface):
        self.rect.center = self.pos
        surface.blit(self.image,self.pos)


class Ball(pygame.sprite.Sprite):
    def __init__(self, pos=(0,0), radius=30):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.radius = radius
        self.pos_x,self.pos_y = self.pos
        self.vel_x = 0
        self.vel_y = 0
        self.image = pygame.Surface((self.radius*2,self.radius*2),pygame.SRCALPHA)
        self.rect = self.image.get_rect() 
        self.colorbg = (0,0,255)
        self.color = (0,255,0)
        self.was_colliding = False
        self.colliding_wall = False
        #self.image.fill(self.colorbg)
        pygame.draw.circle(self.image, self.color,
                           (self.radius,self.radius),self.radius)
        

    def update(self,dt,surface):
        self.vel_y += (dt*0.01)
        self.pos = (self.pos[0]+self.vel_x,self.pos[1]+self.vel_y)
        self.wall_collision()
        self.reset_position()
        self.draw(surface)       

    def draw(self,surface):
        self.rect.center = self.pos
        surface.blit(self.image,self.pos)

    def ball_striker_collision(self,striker):
            if abs(striker.vel_x)+abs(striker.vel_y)> 5:
                self.vel_x,self.vel_y = striker.vel_x,striker.vel_y
            else:
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
    all_sprites = pygame.sprite.Group()
    screen= pygame.display.set_mode(resolution)
    striker = Striker((SCRNWIDTH//2,SCRNHEIGHT//2)) 
    ball = Ball((SCRNWIDTH//2,0))
    ball_group = pygame.sprite.Group(ball)
    striker_group = pygame.sprite.Group(striker)   
    running = True
    while running:
        #QUIT DETECTION
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False   
        screen.fill(black)
        ball.update(dt,screen)
        striker.update(screen)
        print(f"{striker.vel_x,striker.vel_y}")
        collide_circle_group = pygame.sprite.spritecollide(striker,ball_group,False,pygame.sprite.collide_circle)
        for circle in collide_circle_group:
            if not circle.was_colliding:
                circle.ball_striker_collision(striker)
                print("Bounced!")
            circle.was_colliding = True
        for circle in ball_group:
            if circle not in collide_circle_group:
                circle.was_colliding = False
        pygame.display.flip()
        dt = clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()