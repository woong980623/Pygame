import pygame
import time

pygame.font.init()

# 보드 초기 상태
initial_board = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7]
]

class Grid:
    def __init__(self, rows, cols, width, height):
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.cubes = [[Cube(initial_board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]
        self.model = None
        self.update_model()
        self.selected = None
        self.wrong_message = False

    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    def place_number(self, value):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            if self.is_valid(value, (row, col)):
                self.cubes[row][col].set(value)
                self.update_model()
                self.wrong_message = False
            else:
                self.cubes[row][col].temp = 0
                self.wrong_message = True

    def is_valid(self, num, pos):
        # 행 검사
        for i in range(len(self.model[0])):
            if self.model[pos[0]][i] == num and pos[1] != i:
                return False

        # 열 검사
        for i in range(len(self.model)):
            if self.model[i][pos[1]] == num and pos[0] != i:
                return False

        # 박스 검사
        box_x = pos[1] // 3
        box_y = pos[0] // 3

        for i in range(box_y*3, box_y*3 + 3):
            for j in range(box_x*3, box_x*3 + 3):
                if self.model[i][j] == num and (i,j) != pos:
                    return False

        return True

    def clear_temp(self):
        for row in self.cubes:
            for cube in row:
                cube.temp = 0

    def is_full(self):
        for row in self.model:
            if 0 in row:
                return False
        return True

    def draw(self, win):
        # 그리드 라인 그리기
        gap = self.width / 9
        for i in range(self.rows + 1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(win, (0, 0, 0), (0, i * gap), (self.width, i * gap), thick)
            pygame.draw.line(win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # 큐브 그리기
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(win)

        # 선택된 셀 하이라이트
        if self.selected:
            row, col = self.selected
            pygame.draw.rect(win, (255, 0, 0), (col * gap, row * gap, gap, gap), 3)

    def select(self, row, col):
        # 이전 선택 해제
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        # 새로운 큐브 선택
        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def move_selection(self, key):
        if self.selected:
            row, col = self.selected
            if key == pygame.K_LEFT and col > 0:
                col -= 1
            elif key == pygame.K_RIGHT and col < self.cols - 1:
                col += 1
            elif key == pygame.K_UP and row > 0:
                row -= 1
            elif key == pygame.K_DOWN and row < self.rows - 1:
                row += 1
            self.select(row, col)

    def click(self, pos):
        """
        유효한 위치를 클릭하면 (row, col)을 반환하고, 그렇지 않으면 None을 반환
        """
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        else:
            return None

    def sketch(self, value):
        row, col = self.selected
        self.cubes[row][col].temp = value

class Cube:
    rows = 9
    cols = 9

    def __init__(self, value, row, col, width, height):
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def set(self, val):
        self.value = val
        self.temp = 0

    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)
        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap

        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128, 128, 128))
            win.blit(text, (x + 5, y + 5))
        elif self.value != 0:
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))

        if self.selected:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

def redraw_window(win, board, time, message):
    win.fill((255, 255, 255))
    # 시간 그리기
    fnt = pygame.font.SysFont("comicsans", 40)
    text = fnt.render("Time: " + format_time(time), 1, (0, 0, 0))
    win.blit(text, (540 - 160, 560))
    
    # 메시지 그리기
    if message:
        fnt = pygame.font.SysFont("comicsans", 60)
        text = fnt.render(message, 1, (255, 0, 0))
        win.blit(text, (540 / 2 - text.get_width() / 2, 540 / 2 - text.get_height() / 2))
    
    # 그리드 및 보드 그리기
    board.draw(win)

def format_time(secs):
    sec = secs % 60
    minute = (secs // 60) % 60
    hour = secs // 3600
    return " {:02}:{:02}:{:02}".format(hour, minute, sec)

def main():
    win = pygame.display.set_mode((700, 700))
    pygame.display.set_caption("Sudoku")
    board = Grid(9, 9, 540, 540)
    key = None
    run = True
    start = time.time()
    message = None
    
    while run:
        play_time = round(time.time() - start)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4, pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9]:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        key = int(event.unicode)
                    else:
                        key = int(event.unicode[-1])  # 넘버패드 키에서 숫자를 가져오기
                if event.key == pygame.K_DELETE:
                    if board.selected:
                        row, col = board.selected
                        board.cubes[row][col].set(0)
                        board.update_model()
                        key = None
                if event.key == pygame.K_RETURN:
                    if message:
                        board = Grid(9, 9, 540, 540)
                        start = time.time()
                        message = None
                    elif board.selected:
                        i, j = board.selected
                        if board.cubes[i][j].temp != 0:
                            board.place_number(board.cubes[i][j].temp)
                            key = None
                            if board.is_full():
                                message = "Clear!"
                if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                    board.move_selection(event.key)
                    key = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None

        if board.selected and key is not None:
            board.sketch(key)
            key = None

        redraw_window(win, board, play_time, "Incorrect!" if board.wrong_message else message)
        pygame.display.update()

main()
pygame.quit()
