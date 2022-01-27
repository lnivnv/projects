import pygame
import random
import os
import sys
import sqlite3

pygame.init()
screen_height = 750
screen_width = 746
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flaying Mario Menu')


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


def game():
    clock = pygame.time.Clock()
    fps = 60
    screen_width = 750
    screen_height = 746
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
    bg = load_image('projectbg.png')
    ground_img = load_image('ground.png')
    restart_img = load_image('restart_btn.png')
    score_img = load_image('score_btn.png')

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
            if flying is True:
                self.v += 0.5
                if self.v > 8:
                    self.v = 8
                if self.rect.bottom < 746:
                    self.rect.y += int(self.v)
            if game_over is False:
                if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                    self.clicked = True
                    self.v = -10
                if pygame.mouse.get_pressed()[0] == 0:
                    self.clicked = False
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
                self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
            elif position == -1:
                self.rect.topleft = [x, y + int(pipe_gap / 2)]

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
    sc_button = Restart(screen_width // 2 - 60, screen_height // 2 - 128, score_img)
    run = True
    while run:
        clock.tick(fps)
        screen.blit(bg, (0, 0))
        pipe_group.draw(screen)
        bird_group.draw(screen)
        bird_group.update()
        screen.blit(ground_img, (ground_scroll, 578))
        if len(pipe_group) > 0:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                    and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                    and pass_pipe is False:
                pass_pipe = True
            if pass_pipe is True:
                if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False
        draw_text(str(score), font, white, int(screen_width / 2), 20)
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
        if flappy.rect.bottom >= 600:
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
            if event.type == pygame.MOUSEBUTTONDOWN and flying is False and game_over is False:
                flying = True

        pygame.display.update()


def scores():
    screen_width = 750
    screen_height = 746
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Top Scores')
    f1 = pygame.font.SysFont('Comic Sans', 48)
    f2 = pygame.font.SysFont('Comic Sans', 36)
    text2 = f1.render("Top players", False,
                      (222, 241, 243))
    scores_list = []
    coord = [200, 275, 350, 425, 500]
    con = sqlite3.connect("top_score.sqlite")
    cur = con.cursor()
    result = cur.execute("""SELECT * FROM top_score""")
    for score in result:
        scores_list.append([score[2], score[1]])
    scores_list = sorted(scores_list)[::-1]
    y = 200
    run = True
    while run:
        screen.fill((140, 173, 172))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.draw.rect(screen, (64, 76, 77), (100, 200, 550, 450), 8)
        for x in range(5):
            text = f2.render(f'{x + 1} {scores_list[x][1]} - {scores_list[x][0]} points', False, (222, 241, 243))
            screen.blit(text, (150, coord[x]))
            y += 60
        screen.blit(text2, (text2.get_width(), 100))
        pygame.display.update()


class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action


start_button = Button(310, 210, load_image("start_btn.png"), 0.8)
exit_button = Button(310, 436, load_image("exit_btn.png"), 0.8)
score_button = Button(303, 636, load_image("score_btn.png"), 0.8)
run = True
while run:
    screen.fill((202, 228, 241))
    if start_button.draw(screen):
        game()
    if exit_button.draw(screen):
        run = False
    if score_button.draw(screen):
        scores()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    pygame.display.update()
pygame.quit()