import pygame

def main():

    pygame.init()
    pygame.display.set_caption("Breakout:Force")
    clock= pygame.time.Clock()
    dt = 0
    resolution =(1920,1080)
    screen= pygame.display.set_mode(resolution)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False      
        #GAME LOGIC
        #Render and Display
        black = pygame.Color(0,0,0)
        screen.fill(black)
        pygame.display.flip()
        dt = clock.tick(12)
    pygame.quit()


if __name__ == "__main__":
    main()