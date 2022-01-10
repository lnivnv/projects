import os, sys, pygame

pygame.init()
width = 800
height = 600

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Mario')



# load img
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
pygame.quit()