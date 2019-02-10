import pygame
import random
import numpy
import sys
import webbrowser
import os

sc = 40
esay_score = 50
medium_score = 160
hard_score = 500
flag_esay = False
flag_medium = False
flag_hard = False

size = width, height = 1000, 700
board_size = [700, 700]
banner_size = [width - height, height]
link = 'http://xn--80aafypuh.xn--80aa1agjdchjh2p.xn--p1ai/'
font = 'Georgia'
pygame.init()
screen = pygame.display.set_mode(size, pygame.RESIZABLE)
pygame.display.set_caption("Minesweeper")
h1 = pygame.font.SysFont(font, 40)
h2 = pygame.font.SysFont(font, 20)

music = pygame.mixer.music.load('music/ricchi_e_poveri_-_donna_musica.mp3')
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1, 0.0)


class Square:
    def __init__(self, state=0):
        self.state = state
        self.number = 1

        self.screened = True
        self.flagged = False

    def show_tiles(self, grid, ref):
        if self.flagged:
            return

        self.screened = False
        neighbours = [i for i in
                      [[ref[0] - 1, ref[1] - 1],
                      [ref[0], ref[1] - 1],
                      [ref[0] + 1, ref[1] - 1],
                      [ref[0] - 1, ref[1]],
                      [ref[0] + 1, ref[1]],
                      [ref[0] - 1, ref[1] + 1],
                      [ref[0], ref[1] + 1],
                      [ref[0] + 1, ref[1] + 1]]
                      if (0 <= i[0] < len(grid[0]) and 0 <= i[1] < len(grid))]

        for n in neighbours:
            if not grid[n[1]][n[0]].number and grid[n[1]][n[0]].screened:
                grid[n[1]][n[0]].show_tiles(grid, n)
            else:
                grid[n[1]][n[0]].screened = False


class Grid:
    colours = {1: (0, 0, 255),
               2: (50, 205, 50),
               3: (255, 140, 0),
               4: (255, 0, 0),
               5: (148, 0, 211),
               6: (220, 20, 60),
               7: (0, 206, 209),
               8: (255, 105, 180)}

    mine = 8

    def __init__(self, surf_size, square_size, blit_dest=[0, 0]):
        self.surf = pygame.Surface(surf_size)
        self.resolution = [int(i / square_size) for i in self.surf.get_size()]

        self.size = square_size
        self.blit_dest = blit_dest

        self.generated = False
        self.mines_count = int(numpy.prod(self.resolution) // self.mine)
        self.flags = self.mines_count

        self.grid = [[Square() for _ in range(self.resolution[0])] for _ in range(self.resolution[1])]
        self.font = pygame.font.SysFont(font, self.size)

    def generate(self, pos):
        count = 0
        while count < self.mines_count:
            for a, i in enumerate(self.grid):
                for b, j in enumerate(i):
                    if random.randint(1, self.mine) == 1 and not\
                            [b, a] in [i for i in [pos,
                                                   [pos[0] - 1, pos[1] - 1],
                                                   [pos[0], pos[1] - 1],
                                                   [pos[0] + 1, pos[1] - 1],
                                                   [pos[0] - 1, pos[1]],
                                                   [pos[0] + 1, pos[1]],
                                                   [pos[0] - 1, pos[1] + 1],
                                                   [pos[0], pos[1] + 1],
                                                   [pos[0] + 1, pos[1] + 1]]
                                       if (0 <= i[0] < len(self.grid[0]) and
                                           0 <= i[1] < len(self.grid))] and not\
                            j.number == -1 and count < self.mines_count:
                        j.number = -1
                        count += 1

        for y, row in enumerate(self.grid):
            for x, col in enumerate(row):
                surrounding_mines = 0

                if col.number == -1:
                    continue

                combinations = [[x - 1, y - 1], [x, y - 1], [x + 1, y - 1], [x - 1, y], [x + 1, y], [x - 1, y + 1],
                                [x, y + 1], [x + 1, y + 1]]
                for combination in combinations:
                    if 0 <= combination[0] < len(self.grid[0]) and 0 <= combination[1] < len(self.grid):
                        if self.grid[combination[1]][combination[0]].number == -1:
                            surrounding_mines += 1

                sq.number = surrounding_mines

        self.generated = True

    def move(self, pos, button):
        grid_ref = self.coords_to_grid_ref(pos)

        if grid_ref is None:
            return
        if not self.generated:
            self.generate(grid_ref)

        if button == 1 and not self.grid[grid_ref[1]][grid_ref[0]].flagged:
            if self.grid[grid_ref[1]][grid_ref[0]].number:
                self.grid[grid_ref[1]][grid_ref[0]].screened = False
            else:
                self.grid[grid_ref[1]][grid_ref[0]].show_tiles(self.grid, grid_ref)
        elif button == 3:
            if self.flags > 0 and not self.grid[grid_ref[1]][grid_ref[0]].flagged:
                self.grid[grid_ref[1]][grid_ref[0]].flagged = True
            elif self.grid[grid_ref[1]][grid_ref[0]].flagged:
                self.grid[grid_ref[1]][grid_ref[0]].flagged = False

            self.flags = self.mines_count - sum(sum(i.flagged for i in row) for row in self.grid)

    def coords_to_grid_ref(self, pos):
        if all(x < self.resolution[p] for p, x in
               enumerate([int((pos[i] - self.blit_dest[i]) // self.size) for i in range(2)])):
            return [int((pos[i] - self.blit_dest[i]) // self.size) for i in range(2)]
        else:
            return None

    def draw(self, surf):
        for y, row in enumerate(self.grid):
            for x, square in enumerate(row):
                if not square.screened:
                    pygame.draw.rect(self.surf, (255, 255, 255), (x * self.size, y * self.size, self.size, self.size),
                                     0)

                    if square.number == -1:
                        pygame.draw.circle(self.surf, (255, 0, 0),
                                           [int(x * self.size + (self.size / 2)), int(y * self.size + (self.size / 2))],
                                           int(self.size / 4), 0)
                    elif square.number:
                        message = self.font.render(str(square.number), True, self.colours[square.number])
                        self.surf.blit(message, message.get_rect(
                            center=[x * self.size + (self.size / 2), y * self.size + (self.size / 2)]))
                else:
                    pygame.draw.rect(self.surf, (150, 150, 150), (x * self.size, y * self.size, self.size, self.size),
                                     0)

                    if square.flagged:
                        pygame.draw.polygon(self.surf, (255, 0, 0),
                                            [[x * self.size + (0.3 * self.size), y * self.size + (0.2 * self.size)],
                                             [x * self.size + (0.4 * self.size), y * self.size + (0.2 * self.size)],
                                             [x * self.size + (0.4 * self.size), y * self.size + (0.22 * self.size)],
                                             [x * self.size + (0.8 * self.size), y * self.size + (0.4 * self.size)],
                                             [x * self.size + (0.4 * self.size), y * self.size + (0.6 * self.size)],
                                             [x * self.size + (0.4 * self.size), y * self.size + (0.8 * self.size)],
                                             [x * self.size + (0.3 * self.size), y * self.size + (0.8 * self.size)]], 0)

        for x in range(1, len(self.grid[0])):
            pygame.draw.line(self.surf, (0, 0, 0), [x * self.size, 0], [x * self.size, surf.get_height()], 1)
        for y in range(1, len(self.grid)):
            pygame.draw.line(self.surf, (0, 0, 0), [0, y * self.size], [surf.get_width(), y * self.size], 1)

        surf.blit(self.surf, self.blit_dest)

    def status(self):
        if not any(
                any(
                    (s.flagged and not s.number == -1) or (not s.flagged and s.number == -1) for s in row_) for row_ in
                self.grid) and all(
                all(not t.screened or (t.screened and t.flagged) for t in _row) for _row in self.grid):
            return True
        elif any(
                any(g.number == -1 and not g.screened for g in row) for row in self.grid):
            return False
        else:
            return None

    def reset(self, square_size=None):
        if square_size is not None:
            self.resolution = [int(i / square_size) for i in self.surf.get_size()]
            self.size = square_size
            self.mines_count = int(numpy.prod(self.resolution) // self.mine)
            self.font = pygame.font.SysFont(font, self.size)

        self.grid = [[Square() for _ in range(self.resolution[0])] for _ in range(self.resolution[1])]
        self.generated = False
        self.flags = self.mines_count


class Banner:

    def __init__(self, surf_size, grid, blit_dest):

        self.grid = grid
        self.surf = pygame.Surface(surf_size)

        self.t = pygame.time.get_ticks()
        self.blit_dest = blit_dest
        self.h1 = pygame.font.SysFont(font, 50)
        self.h2 = pygame.font.SysFont(font, 30)

    def update(self):
        self.surf.fill((250, 250, 255))
        pygame.draw.line(self.surf, (0, 0, 0), [0, 0], [0, self.surf.get_height()], 1)
        
        image1 = pygame.image.load(os.path.join('foto/photo.jpg'))
        image11 = pygame.transform.scale(image1, (200, 200))
        self.surf.blit(image11, (50, 450))             

        score = self.h2.render("best score: {}".format(sc), False, (0, 0, 0))
        self.surf.blit(score, score.get_rect(center=[self.surf.get_width() / 2, self.surf.get_height() / 5]))

        flag = self.h2.render("Flags: {}/{}".format(self.grid.flags, self.grid.mines_count), True, (0, 0, 0))
        self.surf.blit(flag, flag.get_rect(center=[self.surf.get_width() / 2, self.surf.get_height() / 2 - 50]))

        time_ = self.h2.render("Time: {}".format(int(pygame.time.get_ticks() - self.t)//1000), True, (0, 0, 0))
        self.surf.blit(time_, time_.get_rect(center=[self.surf.get_width() / 2, self.surf.get_height() / 2]))

        levels = {100: "Easy",
                  50: "Medium",
                  25: "Hard"}
        difficulty = self.h2.render("Difficulty: {}".format(levels[self.grid.size]), True, (0, 0, 0))
        self.surf.blit(difficulty, difficulty.get_rect(center=[self.surf.get_width() / 2,
                                                               self.surf.get_height() / 2 + 50]))

    def draw(self, surf):
        surf.blit(self.surf, self.blit_dest)

    def reset(self):
        self.t = pygame.time.get_ticks()


def menu():
    global sc, flag_medium, flag_hard, flag_esay
    standard = (150, 130, 238)
    selected = (150, 250, 98)
    n = 0

    head = pygame.font.SysFont(font, 50).render("Minesweeper", True, (0, 0, 0))

    button1 = pygame.Rect(screen.get_width() / 2 - 200, screen.get_height() / 5, 400, screen.get_height() * (3 / 20))
    button2 = pygame.Rect(screen.get_width() / 2 - 200, screen.get_height() * (2 / 5), 400,
                          screen.get_height() * (3 / 20))
    button3 = pygame.Rect(screen.get_width() / 2 - 200, screen.get_height() * (3 / 5), 400,
                          screen.get_height() * (3 / 20))
    button4 = pygame.Rect(screen.get_width() / 2 - 200, screen.get_height() * (4 / 5), 400,
                          screen.get_height() * (3 / 20))
    button5 = pygame.Rect(50, 425, 200, 100)
    button6 = pygame.Rect(50, 560, 200, 100)
    
    image1 = pygame.image.load(os.path.join('foto/boom.jpg'))
    image1_1 = pygame.transform.scale(image1, (200, 200))
    
    image2 = pygame.image.load(os.path.join('foto/flag.jpg'))    

    b1 = h1.render("Easy", True, (40, 150, 20))
    b2 = h1.render("Medium", True, (128, 0, 0))
    b3 = h1.render("Hard", True, (255, 0, 0))
    b4 = h1.render("Description", True, (0, 0, 0))
    b5 = h1.render("Fullscreen", True, (0, 0, 0))

    if not pygame.mixer.music.get_busy():
        b6 = h1.render("Music on", True, (0, 0, 0))
    elif pygame.mixer.music.get_busy():
        b6 = h1.render("Music off", True, (0, 0, 0))

    while True:
        mouse = pygame.Rect([i - 1 for i in pygame.mouse.get_pos()], [2, 2])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse.colliderect(button1):
                    sc = esay_score
                    flag_esay = True
                    return 100
                elif mouse.colliderect(button2):
                    flag_medium = True
                    sc = medium_score
                    return 50
                elif mouse.colliderect(button3):
                    flag_hard = True
                    sc = hard_score
                    return 25
                elif mouse.colliderect(button4):
                    webbrowser.open_new_tab(url=link)
                elif mouse.colliderect(button5) and n == 0:
                    pygame.display.set_mode(size, pygame.FULLSCREEN)
                    b5 = pygame.font.SysFont(font, 30).render("Window mode", True, (0, 0, 0))
                    n = 1
                elif mouse.colliderect(button5) and n == 1:
                    pygame.display.set_mode(size, pygame.RESIZABLE)
                    b5 = pygame.font.SysFont(font, 40).render("Fullscreen", True, (0, 0, 0))
                    n = 0
                elif mouse.colliderect(button6) and pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    b6 = pygame.font.SysFont(font, 40).render("Music on", True, (0, 0, 0))
                elif mouse.colliderect(button6) and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play()
                    b6 = pygame.font.SysFont(font, 40).render("Music off", True, (0, 0, 0))

        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, standard if not mouse.colliderect(button1) else selected, button1, 5)
        pygame.draw.rect(screen, standard if not mouse.colliderect(button2) else selected, button2, 5)
        pygame.draw.rect(screen, standard if not mouse.colliderect(button3) else selected, button3, 5)
        pygame.draw.rect(screen, standard if not mouse.colliderect(button4) else selected, button4, 5)
        pygame.draw.rect(screen, standard if not mouse.colliderect(button5) else selected, button5, 5)
        pygame.draw.rect(screen, standard if not mouse.colliderect(button6) else selected, button6, 5)

        screen.blit(head, head.get_rect(center=[screen.get_width() / 2, screen.get_height() / 10]))
        screen.blit(b1, b1.get_rect(center=button1.center))
        screen.blit(b2, b2.get_rect(center=button2.center))
        screen.blit(b3, b3.get_rect(center=button3.center))
        screen.blit(b4, b4.get_rect(center=button4.center))
        screen.blit(b5, b5.get_rect(center=button5.center))
        screen.blit(b6, b6.get_rect(center=button6.center))
        screen.blit(image1_1, (55, 90))
        screen.blit(image2, (805, 250))        

        pygame.display.flip()


start = pygame.time.get_ticks()


def result(grid, banner):

    global flag_medium, flag_hard, flag_esay
    global esay_score, medium_score, hard_score
    win = False
    screen = pygame.Surface(screen.get_size())
    screen.set_alpha(200)
    screen.fill((0, 0, 0))
    if grid.status():
        message = h1.render("You won", True, (255, 255, 255))
        win = True
    else:
        message = h1.render("You lost", True, (255, 255, 255))
    end = h2.render("Press any key to continue", True, (255, 255, 255))
    if pygame.time.get_ticks()-pygame.time.get_ticks() < sc:
        if flag_esay and win:
            esay_score = int(pygame.time.get_ticks()-start)//1000
            flag_esay = False
        if flag_medium and win:
            medium_score = int(pygame.time.get_ticks()-start)//1000
            flag_medium = False
        if flag_hard and win:
            hard_score = int(pygame.time.get_ticks()-start)//1000
            flag_hard = False

    screen.blit(message, message.get_rect(center=[screen.get_width() / 2, screen.get_height() / 2.5]))
    screen.blit(end, end.get_rect(center=[screen.get_width() / 2, screen.get_height() / 2]))

    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                return

        grid.draw(screen)
        banner.draw(screen)
        screen.blit(screen, (0, 0))

        pygame.display.flip()


def main():
    square_size = menu()
    grid = Grid(board_size, square_size)
    banner = Banner(banner_size, grid, [grid.surf.get_width(), 0])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                grid.move(pygame.mouse.get_pos(), event.button)

        banner.update()

        grid.draw(screen)
        banner.draw(screen)

        pygame.display.flip()

        if grid.status() is not None:

            result(grid, banner)
            square_size = menu()
            grid.reset(square_size)
            banner.reset()


if __name__ == "__main__":
    main()
