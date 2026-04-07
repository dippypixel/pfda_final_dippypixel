import pygame

# CONSTANTS

SCRNWIDTH = 1920
SCRNHEIGHT = 1080

class Striker():

    def __init__(self, pos=(0,0), radius=30):
        print("Striker Exist")
        self.pos = pos
        self.radius = radius
        self.color = pygame.Color(0,255,0)
        self.surface = pygame.Surface((self.radius,self.radius),
                                                pygame.SRCALPHA)
        self._rect = pygame.Rect(0, 0, self.radius, self.radius)
    def update(self,surface):
        x,y = pygame.mouse.get_pos()
        x =  min(x,SCRNWIDTH-self.radius)
        y = max(min(y,SCRNHEIGHT-self.radius),SCRNHEIGHT//2)
        self._rect.update(x,y,self.radius, self.radius)
        self.draw(surface)
    def draw(self,surface):
        pygame.draw.rect(surface, self.color, self._rect)

class Ball(pygame.sprite.Sprite):

    def __init__(self, pos=(0,0), radius=60):
        print("Ball Exist")
        self.pos = pos
        self.radius = radius
        self.color = pygame.Color(255,255,255)
        self.surface = pygame.Surface((self.radius,self.radius),
                                                pygame.SRCALPHA)
        self._rect = pygame.Rect(0, 0, self.radius, self.radius)

        self.pos_x,self.pos_y = self.pos
        self.vel_y = 0.0

    def update(self,surface,dt):
        self.apply_gravity(dt)
        self._rect.update(self.pos_x,self.pos_y,self.radius, self.radius)
        self.draw(surface)

    def apply_gravity(self,dt):
        self.vel_y += (dt*0.01)
        self.pos_y += self.vel_y   

    def bounce(self,striker):
        if self._rect.colliderect(striker._rect):
            print("True")
            self.vel_y *= -.9   

    def draw(self,surface):
        pygame.draw.rect(surface, self.color, self._rect)

        
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
        ball.bounce(striker)   
        pygame.display.flip()
        dt = clock.tick(60)
        print(dt)
    pygame.quit()


if __name__ == "__main__":
    main()