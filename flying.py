import pygame
import random
import os
import sys
import sqlite3


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
    font = pygame.font.SysFont('Comic Sans', 60)
    ground_scroll = 0
    scroll_speed = 4
    flying = False
    game_over = False
    pipe_gap = 150
    pipe_frequency = 1500
    last_pipe = pygame.time.get_ticks() - pipe_frequency
    score = 0
    pass_pipe = False
    bg = load_image(f'projectbg.png')
    ground_img = load_image('ground.png')
    restart_img = load_image('restart_btn.png')
    score_img = load_image('addscore_btn.png')
    menu_img = load_image('menu_btn.png')

    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

    class Mario(pygame.sprite.Sprite):
        def __init__(self, x, y):
            pygame.sprite.Sprite.__init__(self)
            self.img = []
            self.index = 0
            self.counter = 0
            for i in range(1, 3):
                img = load_image(f"p{i}.png")
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
                self.rect.bottomleft = [x, y - int(pipe_gap / 1.7)]
            elif position == -1:
                self.rect.topleft = [x, y + int(pipe_gap / 1.7)]

        def update(self):
            self.rect.x -= scroll_speed
            if self.rect.right < 0:
                self.kill()
    pipe_group = pygame.sprite.Group()
    mario_group = pygame.sprite.Group()
    flappy = Mario(100, int(screen_height / 2))
    mario_group.add(flappy)
    res_button = Button(270, 500, restart_img, 0.8)
    sc_button = Button(270, 350, score_img, 0.8)
    m_button = Button(284, 200, menu_img, 0.8)
    run = True
    while run:
        clock.tick(fps)
        screen.blit(bg, (0, 0))
        pipe_group.draw(screen)
        mario_group.draw(screen)
        mario_group.update()
        screen.blit(ground_img, (ground_scroll, 578))
        if len(pipe_group) > 0:
            if mario_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                    and mario_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                    and pass_pipe is False:
                pass_pipe = True
            if pass_pipe is True:
                if mario_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                    score += 1
                    pass_pipe = False
        draw_text(str(score), font, (63, 90, 93), int(screen_width / 2), 20)
        if pygame.sprite.groupcollide(mario_group, pipe_group, False, False) or flappy.rect.top < 0:
            game_over = True
        if flappy.rect.bottom >= 600:
            game_over = True
            flying = False
        if flying is True and game_over is False:
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
        if game_over is True:
            if res_button.draw(screen):
                game()
                exit()
            if sc_button.draw(screen):
                add_username(score)
            if m_button.draw(screen):
                menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and flying is False and game_over is False:
                flying = True
        pygame.display.flip()


def about_game():
    screen_width = 750
    screen_height = 746
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('About game')
    f1 = pygame.font.SysFont('Comic Sans', 48)
    f2 = pygame.font.SysFont('Comic Sans', 21)
    text1 = f1.render("О игре", False, (0, 0, 0))
    file = list(open("flying_mario_rules.txt", 'r', encoding="utf-8"))
    file = [line.rstrip() for line in file]
    run = True
    coordx = [200, 240, 280, 320, 360, 400, 440, 480, 520]
    while run:
        screen.fill((241, 245, 230))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.draw.rect(screen, (64, 76, 77), (100, 200, 550, 450), 8)
        screen.blit(text1, (300, 100))
        for x in range(len(file)):
            text = f2.render(file[x], False, (0, 0, 0))
            screen.blit(text, (110, coordx[x]))
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


def add_username(score):
    screen_width = 750
    screen_height = 746
    screen = pygame.display.set_mode((screen_width, screen_height))
    f1 = pygame.font.SysFont('Comic Sans', 24)
    text1 = f1.render("Чтобы добавить свой результат введите имя/ник", False, (0, 0, 0))
    clock = pygame.time.Clock()
    input_box = pygame.Rect(100, 200, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        con = sqlite3.connect("score.db")
                        cur = con.cursor()
                        result = cur.execute("""INSERT INTO score (name, point) VALUES (?, ?)""", (str(text), score, ))
                        con.commit()
                        text = ''
                        run = False
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((241, 245, 230))
        screen.blit(text1, (50, 100))
        txt_surface = f1.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()
        clock.tick(30)


def keyFunc(item):
    return item[0]


def scores():
    screen_width = 750
    screen_height = 746
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Top Scores')
    f1 = pygame.font.SysFont('Comic Sans', 48)
    f2 = pygame.font.SysFont('Comic Sans', 20)
    text2 = f1.render("Top players", False,
                      (222, 241, 243))
    scores_list = []
    coord = [200, 235, 270, 305, 340, 375, 410, 445, 480, 515, 550, 585, 620, 655, 690, 725]
    print(len(coord))
    con = sqlite3.connect("score.db")
    cur = con.cursor()
    result = cur.execute("""SELECT * FROM score""")
    for sc in result:
        scores_list.append([sc[2], sc[1]])
    scores_list.sort(key=keyFunc)
    scores_list = scores_list[::-1]
    y = 200
    run = True
    q = 13
    while run:
        screen.fill((140, 173, 172))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.draw.rect(screen, (64, 76, 77), (100, 200, 550, 450), 8)
        if len(scores_list) < 13:
            q = len(scores_list)
        for x in range(q):
            text = f2.render(f'{x + 1}) {scores_list[x][1]} - {scores_list[x][0]} points', False, (222, 241, 243))
            screen.blit(text, (110, coord[x]))
            y += 30
        screen.blit(text2, (text2.get_width(), 100))
        pygame.display.update()


def menu():
    pygame.init()
    screen_height = 750
    screen_width = 746
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Flaying Mario Menu')
    start_button = Button(265, 150, load_image("start_btn.png"), 0.8)
    score_button = Button(265, 300, load_image("score_btn.png"), 0.8)
    exit_button = Button(284, 450, load_image("exit_btn.png"), 0.8)
    rules_button = Button(0, 650, load_image("rules_btn.png"), 0.8)
    run = True
    while run:
        screen.fill((140, 173, 172))
        if start_button.draw(screen):
            game()
        if exit_button.draw(screen):
            run = False
        if score_button.draw(screen):
            scores()
        if rules_button.draw(screen):
            about_game()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.update()
    pygame.quit()
    exit()


menu()
