import pygame
import random
import os
import sys

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 800
screen_height = 501

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flying Mario')
font = pygame.font.SysFont('Bauhaus 93', 60)
white = (255, 255, 255)
ground_scroll = 0
scroll_speed = 4
flying = False
game_over = False
pipe_gap = 150
pipe_frequency = 1500
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False


def load_image(name, colorkey=None):
    fullname = os.path.join('pygameGitHub/data', name)
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


bg = load_image('mybg.jpg')
ground_img = load_image('ground.png')
restart_img = load_image('restart.xcf')
score_img = load_image('score.xcf')
# start_img = load_image('start_img')


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score


class Mario(pygame.sprite.Sprite):

    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.img = []
        self.index = 0
        self.counter = 0
        for i in range(1, 3):
            img = load_image(f"flyingmario{i}.xcf")
            self.img.append(img)
        self.image = self.img[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.v = 0
        self.clicked = False

    def update(self):
        if flying == True:

            self.v += 0.5
            if self.v > 8:
                self.v = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.v)
        if game_over == False:
            # jump
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.v = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False
            # handle the animation
            flap_cooldown = 5
            self.counter += 1

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.img):
                    self.index = 0
                self.image = self.img[self.index]


            self.image = pygame.transform.rotate(self.img[self.index], self.v * -2)
        else:

            self.image = pygame.transform.rotate(self.img[self.index], -90)


class Pipe(pygame.sprite.Sprite):

    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_image("pipe2.png")
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 1.1)]
        elif position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 1.1)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()


class Restart():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True

        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


class Score():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action


pipe_group = pygame.sprite.Group()
bird_group = pygame.sprite.Group()
flappy = Mario(100, int(screen_height / 2))
bird_group.add(flappy)
res_button = Restart(screen_width // 2 - 60, screen_height // 2 + 50, restart_img)
sc_button = Score(screen_width // 2 - 60, screen_height // 2 - 27, score_img)
run = True
while run:
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    pipe_group.draw(screen)
    bird_group.draw(screen)
    bird_group.update()
    screen.blit(ground_img, (ground_scroll, 768))
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and pass_pipe == False:
            pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False
    draw_text(str(score), font, white, int(screen_width / 2), 20)
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True
    if flappy.rect.bottom >= 768:
        game_over = True
        flying = False
    if flying == True and game_over == False:
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
        pipe_group.update()
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

    if game_over == True:
        if res_button.draw():
            game_over = False
            score = reset_game()
        if sc_button.draw():
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True

    pygame.display.update()

pygame.quit()