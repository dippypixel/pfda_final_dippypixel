import pygame
#------------------------------------------------------------------------
# CONSTANTS

SCRNWIDTH = 720
SCRNHEIGHT = 1080
#------------------------------------------------------------------------
class Striker():

    def __init__(self, pos=(0,0), radius=60):
        self.pos = pos
        self.radius = radius
        self.color = pygame.Color(0,255,0)
        self._rect = pygame.Rect(0, 0, self.radius, self.radius)
    def update(self,surface):
        x,y = pygame.mouse.get_pos()
        x =  min(x,SCRNWIDTH-self.radius)
        y = max(min(y,SCRNHEIGHT-self.radius),SCRNHEIGHT//2)

        self.vel_x = x - self._rect.x
        self.vel_y = y - self._rect.y

        self._rect.update(x,y,self._rect.width, self._rect.height)
        self.draw(surface)  


    def draw(self,surface):
        pygame.draw.rect(surface, self.color, self._rect)

#------------------------------------------------------------------------
class Ball():

    def __init__(self, pos=(0,0), radius=60):
        self.pos = pos
        self.radius = radius
        self.pos_x,self.pos_y = self.pos
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.color = pygame.Color(255,255,255)
        self._rect = pygame.Rect(0, 0, self.radius, self.radius)
        self.vel_rect = pygame.Rect(0, 0, self.radius, self.radius)
        self._strikerhit = False
        self._wallhit = False
        self.fast = False

    def update(self,surface,dt):
        #Update Position
        self.out_of_bounds()
        self.vel_y += (dt*0.01)
        self.pos_x += self.vel_x
        self.pos_y += self.vel_y
        if self.fast == True:
            self.color = pygame.Color(255,0,0)
        else:
            self.color = pygame.Color(255,255,255)
        self._rect.update(self.pos_x,self.pos_y,self.radius, self.radius)
        self.draw(surface) 

    def out_of_bounds(self):
        if self.pos_y >= SCRNHEIGHT + self.radius:
            self.pos_x =SCRNWIDTH//2
            self.pos_y =0
            self.vel_x = 0.0
            self.vel_y = 0.0        

    def ball_striker_collision(self,striker):
        self.vel_rect = pygame.Rect(self.pos_x, 
                               self.pos_y + self.vel_y*2, 
                               self.radius*(1.5+(abs(self.vel_x)//15)), self.radius)
        self.vel_rect.centerx = self._rect.centerx
        if self.vel_rect.colliderect(striker._rect):
            if self._strikerhit == False:
                if abs(striker.vel_y) > 10:
                    self.vel_x = striker.vel_x
                else:
                    self.vel_x = (self._rect.x - striker._rect.x)//5
                if striker.vel_y < -10:
                    self.vel_y = striker.vel_y
                else:
                    self.vel_y *= -.7
                    
                if (abs(striker.vel_x) + abs(striker.vel_y))//2 > 40:
                    self.fast = True
                
                self._strikerhit = True
                if self.fast == False:
                    print("Hit Paddle")
                else:
                    print("Hit Superfast!")
        else:
            self._strikerhit = False
    def wall_collision(self):
        if self._wallhit == False:
            if self._rect.y <= 0 + self.radius and self.vel_y < 0:
                self.vel_y *= -.7
                self._wallhit = True
                print("Hit Cieling")
                self.fast = False
            if (self._rect.x <= 0 + self.radius-self.vel_x 
                or self._rect.x+self.vel_x  >= SCRNWIDTH - self.radius):
                self.vel_x *= -.7
                self._wallhit = True
                print("Hit Wall")
        else:
            self._wallhit = False

    def draw(self,surface):
        #pygame.draw.rect(surface, pygame.Color(144,144,144), self.vel_rect)
        pygame.draw.rect(surface, self.color, self._rect)

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
    striker = Striker()
    ball = Ball((SCRNWIDTH//2,0))
    running = True
    while running:
        #QUIT DETECTION
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False   
        screen.fill(black)      
        striker.update(screen)
        ball.update(screen,dt)    
        ball.ball_striker_collision(striker)   
        ball.wall_collision()
        pygame.display.flip()
        dt = clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()