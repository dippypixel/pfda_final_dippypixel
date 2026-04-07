import pygame

# CONSTANTS

SCRNWIDTH = 1920
SCRNHEIGHT = 1080

class Striker():

    def __init__(self, pos=(0,0), size=30):
        print("Striker Exist")
        self.pos = pos
        self.size = size
        self.color = pygame.Color(0,255,0)
        self.surface = pygame.Surface((self.size,self.size),pygame.SRCALPHA)
        self.shape = pygame.Rect(0, 0, self.size, self.size)
    def update(self,surface):
        x,y = pygame.mouse.get_pos()
        x = min(x,SCRNWIDTH-self.size)
        y = max(min(y,SCRNHEIGHT-self.size),SCRNHEIGHT//2)
        self.pos = (x,y)
        self.draw(surface)
    def draw(self,surface):
        pygame.draw.ellipse(self.surface, self.color, self.shape)
        surface.blit(self.surface,self.pos)
def main():

    pygame.init()
    pygame.display.set_caption("Breakout:Force")
    pygame.mouse.set_visible(False)
    clock= pygame.time.Clock()
    #values
    dt = 0.0
    resolution =(SCRNWIDTH,SCRNHEIGHT)
    black = pygame.Color(0,0,0)
    screen= pygame.display.set_mode(resolution)
    striker = Striker()
    running = True
    while running:
        #QUIT DETECTION
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False   
        screen.fill(black)
        striker.update(screen)
        pygame.display.flip()
        dt = clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    main()