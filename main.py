from setup import *


class GameObject:
    '''
    заготовка для других классов
    '''
    def __init__(self, x=0, y=0) -> None:
        self.x = x
        self.y = y
        self.image = ' '


class Player(GameObject):
    '''
    класс игрока
    '''
    def __init__(self, speed=0) -> None:
        super().__init__()
        self.x = PLAYER_START_X
        self.y = PLAYER_START_Y
        self.max_speed = PLAYER_MAX_SPEED
        self.direction = 3
        self.speed = speed
        self.image = 'P'
        self.current_frame = PLAYER_START_FRAME
        self.state = 1


class BlackHole(GameObject):
    '''
    класс черной дыры
    кроме данных о самой дыре имеет методы для проверки нахождения
    игрока в своем радиусе и воздействия на игрока
    '''
    def __init__(self, x, y, frame, force=5) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.current_frame = frame
        self.force = force  # Радиус притяжения
        self.image = 'B'    # Обозначение на карте

    def affect_player(self, player) -> None:
        # Притягивание игрока
        if player.x > self.x:
            player.x -= 1
        elif player.x < self.x:
            player.x += 1

        if player.y > self.y:
            player.y -= 1
        elif player.y < self.y:
            player.y += 1

    def is_within_force_radius(self, player_x, player_y) -> bool:
        # Проверяет и возвращает, находится ли игрок в радиусе этой дыры
        x_left = self.x - self.force
        x_right = self.x + self.force
        y_top = self.y - self.force
        y_bottom = self.y + self.force
        coordinates = []
        for y in range(y_top, y_bottom):
            for x in range(x_left, x_right):
                coordinates.append((x, y))

        for coordinate in coordinates:
            if coordinate == (player_x, player_y):
                return True
        return False


class WhiteHole(GameObject):
    '''
    класс белой дыры
    кроме данных о самой дыре имеет методы для проверки нахождения
    игрока в своем радиусе и воздействия на игрока
    '''
    def __init__(self, x, y, frame, force=5) -> None:
        super().__init__()
        self.current_frame = frame
        self.force = force
        self.image = 'W'
        self.x = x
        self.y = y

    def affect_player(self, player) -> None:
        # Отталкивание игрока
        if player.x > self.x:
            player.x += 1
        elif player.x < self.x:
            player.x -= 1

        if player.y > self.y:
            player.y += 1
        elif player.y < self.y:
            player.y -= 1

    def is_within_force_radius(self, player_x, player_y) -> bool:
        # Проверяет и возвращает, находится ли игрок в радиусе этой дыры
        x_left = self.x - self.force
        x_right = self.x + self.force
        y_top = self.y - self.force
        y_bottom = self.y + self.force
        coordinates = []
        for y in range(y_top, y_bottom):
            for x in range(x_left, x_right):
                coordinates.append((x, y))

        for coordinate in coordinates:
            if coordinate == (player_x, player_y):
                return True
        return False


class MatterFragment(GameObject):
    '''
    класс для обломков материи
    '''
    def __init__(self, x, y, frame):
        super().__init__()
        self.x = x
        self.y = y
        self.current_frame = frame
        self.image = '\u2604'


class Base(GameObject):
    '''
    класс для базы
    '''
    def __init__(self, x, y, frame):
        super().__init__()
        self.x = x
        self.y = y
        self.current_frame = frame
        self.image = '\u2302'


class Field:
    '''
    класс поля
    основной класс
    в нем находится не только поле, но и методы для правильной работы игры,
    в том числе и основной цикл игры
    '''
    def __init__(self, cols=FRAME_WIDTH, rows=FRAME_HEIGHT, frames=9) -> None:
        self.cols = cols
        self.rows = rows
        self.player = Player()
        self.frames = frames
        self.field = self.make_field()
        self.holes = self.make_holes(HOLES)
        self.base = Base(BASE_X, BASE_Y, BASE_FRAME)
        self.menu = Menu()
        self.black_holes_coordinates, self.white_holes_coordinates = self.get_holes_coordiates()
        self.matter_fragments = self.make_matter_fragments()
        self.was_teleported = 0

    def make_field(self) -> None:
        # создает поле
        result = []
        for frame in range(self.frames):
            frame = []
            for row in range(self.rows):
                row = []
                for col in range(self.cols):
                    row.append([])
                frame.append(row)
            result.append(frame)
        return result

    def render(self) -> None:
        # отрисовывает поле
        current_frame = self.player.current_frame
        output = f'┏{'━' * FRAME_WIDTH}┓ \n'
        for row in range(1, self.rows + 1):
            output += '┃'
            output += '\033[44m'
            for col in range(1, self.cols + 1):
                if (col, row) == (self.player.x, self.player.y):
                    output += f'\033[31m{DIRECTION_ARROWS[
                        DIRECTIONS[abs(self.player.direction) - 1] # отрисовывает игрока
                    ]}\033[37m'
                elif (col, row, current_frame) == \
                        (
                            self.base.x,
                            self.base.y,
                            self.base.current_frame
                         ):
                        output += f'\033[32;43m{self.base.image}\033[37;44m' # отрисовывает базу
                else:
                    for hole in self.holes:
                        if (col, row, current_frame) == (hole.x, hole.y, hole.current_frame): # отрисовывает дыры
                            if isinstance(hole, BlackHole):
                                output += f'\033[37;40m{hole.force}\033[37;44m'
                                break
                            output += f'\033[30;47m{hole.force}\033[37;44m'
                            break
                        elif (col, row, current_frame) in self.matter_fragments: # отрисовывает обломки материи
                            output += '\u2756'
                            break
                    else: output += ' '
            output += '\033[40m'
            output += '┃\n'
        output += f'┗{'━' * FRAME_WIDTH}┛'
        print('\033[H', end='')  # Перемещаем курсор в начало экрана
        print(output, f'\n {self.show_map()}spd: {self.player.speed} \n', end='')
        print('\033[H ', end='')

    def make_holes(self, num) -> list:
        # создает список с дырами
        holes = []
        for frame in range(1, self.frames):
            holes.append(
                choice(
                    (
                        BlackHole(randint(1, FRAME_WIDTH), randint(1, FRAME_HEIGHT), frame, randint(3, 5)),
                        WhiteHole(randint(1, FRAME_WIDTH), randint(1, FRAME_HEIGHT), frame, randint(3, 5)),
                    )
                )
            )

        for i in range(num - self.frames):
            holes.append(
                choice(
                    (
                        BlackHole(randint(1, FRAME_WIDTH), randint(1, FRAME_HEIGHT), randint(1, 9), randint(3, 5)),
                        WhiteHole(randint(1, FRAME_WIDTH), randint(1, FRAME_HEIGHT), randint(1, 9), randint(3, 5)),
                    )
                )
            )
        return holes

    def make_matter_fragments(self):
        # создает список с обломками материи
        all_fragments = []
        available_coordinates = []
        to_remove = []
        leave_clear = [[-1, 0], [-1, 1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1]]

        for screen_idx, screen in enumerate(self.field): # создает список с координатами
            screen_coordinates = []
            for row_idx, row in enumerate(screen):
                for col_idx, _ in enumerate(row):
                    screen_coordinates.append((col_idx + 1, row_idx + 1, screen_idx + 1))
            available_coordinates.append(screen_coordinates)
        for coordinates in available_coordinates: # удаляет координаты, на которых нельзя разместить обломки
            if available_coordinates.index(coordinates) + 1 == PLAYER_START_FRAME:
                if (PLAYER_START_X, PLAYER_START_Y, PLAYER_START_FRAME) in coordinates:
                    coordinates.remove((PLAYER_START_X, PLAYER_START_Y, PLAYER_START_FRAME))
            for coord in leave_clear:
                to_remove.append(
                    (
                        PLAYER_START_X + coord[0],
                        PLAYER_START_Y + coord[1],
                        PLAYER_START_FRAME
                     )
                )
                to_remove.append(
                    (
                        PLAYER_START_X + coord[0],
                        PLAYER_START_Y + coord[1],
                        PLAYER_START_FRAME
                     )
                )
            for hole_coordinate in (*self.black_holes_coordinates, *self.white_holes_coordinates):
                to_remove.append(hole_coordinate)
            if available_coordinates.index(coordinates) + 1 in \
                 (1, 2, 3, 4, 5, 6):
                for coordinate in coordinates:
                    if FRAME_HEIGHT == coordinate[1]:
                        to_remove.append(coordinate)
            if available_coordinates.index(coordinates) + 1 in \
                (4, 5, 6, 7, 8, 9):
                for coordinate in coordinates:
                    if 1 == coordinate[1]:
                        to_remove.append(coordinate)
            if available_coordinates.index(coordinates) + 1 in \
                (1, 2, 4, 5, 7, 8):
                for coordinate in coordinates:
                    if FRAME_WIDTH == coordinate[0]:
                        to_remove.append(coordinate)
            if available_coordinates.index(coordinates) + 1 in \
                (2, 3, 5, 6, 8, 9):
                for coordinate in coordinates:
                    if 1 == coordinate[0]:
                        to_remove.append(coordinate)
            for coordinate in to_remove:
                try:
                    coordinates.remove(coordinate)
                except ValueError:
                    pass


        for frame in available_coordinates: # создает обломки
            shuffle(frame)
            for idx in range(randint(int(FRAME_WIDTH * 1.5), int(FRAME_WIDTH * 2))):
                all_fragments.append(frame[idx])

        return all_fragments

    def get_holes_coordiates(self) -> list:
        # создает два списка: с координатами всех белых и черных дыр
        bh_coordinates = []
        wh_coordinates = []
        for hole in self.holes:
            if isinstance(hole, BlackHole):
                bh_coordinates.append((hole.x, hole.y, hole.current_frame))
            else:
                wh_coordinates.append((hole.x, hole.y, hole.current_frame))
        return bh_coordinates, wh_coordinates

    def move_player(self) -> None:
        # передвгает игрока
        if self.player.direction == 1:
            self.player.x -= 1
        elif self.player.direction == 2:
            self.player.x -= 1
            self.player.y -= 1
        elif self.player.direction == 3:
            self.player.y -= 1
        elif self.player.direction == 4:
            self.player.y -= 1
            self.player.x += 1
        elif self.player.direction == 5:
            self.player.x += 1
        elif self.player.direction == 6:
            self.player.x += 1
            self.player.y += 1
        elif self.player.direction == 7:
            self.player.y += 1
        elif self.player.direction == 8:
            self.player.x -= 1
            self.player.y += 1

    def change_frame(self) -> None:
        # изменяет текущий 'экран'
        if self.player.x <= 0: # Перемещение налево
            if (self.player.current_frame - 1) % 3:
                self.player.current_frame -= 1
                self.player.x = FRAME_WIDTH
            else:
                self.player.x = 1
                self.player.speed = 0
        elif self.player.x >= FRAME_WIDTH + 1: # Перемещение направо
            if self.player.current_frame % 3:
                self.player.current_frame += 1
                self.player.x = 1
            else:
                self.player.x = FRAME_WIDTH
                self.player.speed = 0
        elif self.player.y <= 0: # Перемещение направо
            if self.player.current_frame - 3 > 0:
                self.player.current_frame -= 3
                self.player.y = FRAME_HEIGHT
            else:
                self.player.y = 1
                self.player.speed = 0
        elif self.player.y >= FRAME_HEIGHT + 1: # Перемещение направо
            if self.player.current_frame + 3 <= self.frames:
                self.player.current_frame += 3
                self.player.y = 1
            else:
                self.player.y = FRAME_HEIGHT
                self.player.speed = 0

    def change_player_direction(self) -> None:
        # изменяет направление игрока
        if arrow_states['left']:
            self.player.direction = self.player.direction - 1
            if self.player.direction - 1 < 0: self.player.direction = len(DIRECTIONS)
        elif arrow_states['right']:
            self.player.direction = self.player.direction + 1
            if self.player.direction > len(DIRECTIONS) - 1: self.player.direction = 0
        elif arrow_states['up']:
            self.player.speed += 1
            if self.player.speed > self.player.max_speed:
                self.player.speed = self.player.max_speed
        elif arrow_states['down']:
            self.player.speed -= 1
            if self.player.speed < 0:
                self.player.speed = 0

    def check_player_collision(self) -> None:
        # проверяет коллизию игрока
        for fragment in self.matter_fragments: # проверка коллизии с обломками
            if self.player.current_frame == fragment[-1]:
                if (self.player.x, self.player.y) == (fragment[0], fragment[1]):
                    self.player.state = 0
        for hole_coords in self.black_holes_coordinates: # проверка коллизии с черными дырами
            if (self.player.x, self.player.y, self.player.current_frame) == hole_coords:
                coords_add_after_tp = [[-1, 0], [-1, 1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1]]
                coords_after_tp = choice(self.white_holes_coordinates)
                new_coords_after_tp = [0, 0, coords_after_tp[2]]
                new_coords_after_tp[0] = coords_after_tp[0] + coords_add_after_tp[self.player.direction - 1][0]
                new_coords_after_tp[1] = coords_after_tp[1] + coords_add_after_tp[self.player.direction - 1][1]
                self.player.x, self.player.y, self.player.current_frame = \
                    new_coords_after_tp
        for white_hole in self.white_holes_coordinates: # проверка коллизии с черными дырами
            if self.player.current_frame == white_hole[-1]:
                if (self.player.x, self.player.y) == (white_hole[0], white_hole[1]):
                    if not self.was_teleported:
                        self.player.x = randint(1, FRAME_WIDTH)
                        self.player.y = randint(1, FRAME_HEIGHT)
        if self.player.current_frame == BASE_FRAME: # проверка коллизии с базой
            if (self.player.x, self.player.y) == (BASE_X, BASE_Y):
                self.player.state = 2

    def on_press(self, event) -> None:
        # запись нажатых клавиш
        if event.event_type == keyboard.KEY_DOWN:
            if event.name in arrow_states:
                arrow_states[event.name] = True
        elif event.event_type == keyboard.KEY_UP:
            if event.name in arrow_states:
                self.change_player_direction()
                arrow_states[event.name] = False

    def show_map(self) -> str:
        # отрисовка карты
        output = ''
        for i in range(1, self.frames + 1):
            if self.player.current_frame == i: output += 'P'
            else: output += '.'
            if not i % 3 and i != 0: output += '   \n '
        return output

    def main_game_cycle(self) -> None:
        # игра
        if self.player.state in (0, 2): # перезапуск игры
            self.player = Player
            self.field = self.make_field()
            self.holes = self.make_holes(HOLES)
            self.black_holes_coordinates, self.white_holes_coordinates = self.get_holes_coordiates()
            self.matter_fragments = self.make_matter_fragments()
        self.menu.game_started = 0
        self.player.state = 1
        self.player = Player()
        self.menu.show(3)
        os.system('cls')
        move_start_time = time.time()
        hole_start_time = time.time()
        keyboard.hook(self.on_press)
        while self.player.state == 1: # основной цикл игры
            self.check_player_collision()
            self.render()
            self.change_frame()
            try:
                if time.time() - move_start_time > 1 / self.player.speed:
                    move_start_time = time.time()
                    self.move_player()
                time.sleep(0.005)
            except ZeroDivisionError:
                continue
            if time.time() - hole_start_time >= 0.98:
                hole_start_time = time.time()
                for hole in self.holes:
                    if hole.is_within_force_radius(self.player.x, self.player.y) and \
                        hole.current_frame == self.player.current_frame:
                        hole.affect_player(self.player)
                        break
        else: # выход из цикла
            keyboard.unhook(field.on_press)
            self.menu.show(self.player.state)


class Menu():
    '''
    класс для меню
    здесь происходить отрисовка и взаимодействие с ним
    '''
    def __init__(self) -> None:
        self.game_started = 0
        self.menu_item = 0
        self.selected_menu_item = 0
        self.current_screen = 0
        self.tutorial_page = 0
        self.menu_items = [
            'Начать игру',
            'Обучение',
            'Выход',
        ]

    def on_press(self, event) -> None:
        # регистрация нажатых клавиш
        if event.event_type == keyboard.KEY_DOWN:
            if event.name in arrow_states:
                arrow_states[event.name] = True
        elif event.event_type == keyboard.KEY_UP:
            if event.name in arrow_states:
                self.change_menu_item()
                arrow_states[event.name] = False

    def show(self, state) -> None:
        # отрисовка меню
        keyboard.hook(self.on_press)
        os.system('cls')
        if state == 3:
            while not self.game_started:
                while self.current_screen == 0 and not self.game_started:
                    output = ''
                    output += LOGO + '\n'
                    for idx, item in enumerate(self.menu_items):
                        if idx == self.selected_menu_item:
                            output += f'>{item}\n'
                            continue
                        output +=f'\u00B7{item}\n'
                    print('\033[H', end='')
                    print(output)
                os.system('cls')
                while self.current_screen == 1:
                    self.show_tutorial()
                os.system('cls')
        elif state == 2: # отрисовка при победе
            os.system('cls')
            print('\033[H')
            print(MISSION_COMPLETE_TEXT)
            input('Нажмите ENTER для возврата в меню')
            field.main_game_cycle()
        elif state == 0: # отрисовка при проигрыше
            os.system('cls')
            print('\033[H')
            print(GAME_OVER_TEXT)
            input('Нажмите ENTER для возврата в меню')
            field.main_game_cycle()
        keyboard.unhook(self.on_press)

    def select_menu_item(self):
        # выбор пункта в меню
        if self.current_screen == 0:
            if self.selected_menu_item == 0:
                self.game_started = 1
            if self.selected_menu_item == 1:
                self.show_tutorial()
            if self.selected_menu_item == 2:
                os._exit(0)

    def show_tutorial(self):
        # отрисовка обучения
        self.current_screen = 1
        print('\033[H ', end='')
        print(f'{TUTORIAL_TEXT[self.tutorial_page]}\n\n\n{self.tutorial_page+1}/{len(TUTORIAL_TEXT)}\nВниз - главное меню')

    def change_menu_item(self):
        # смена пункта в меню
        if arrow_states['left']:
            if self.current_screen == 1 and self.tutorial_page > 0:
                self.tutorial_page -= 1
                os.system('cls')
        elif arrow_states['right']:
            if self.current_screen == 0:
                self.select_menu_item()
            elif self.current_screen == 1 and self.tutorial_page < len(TUTORIAL_TEXT) - 1:
                self.tutorial_page += 1
                os.system('cls')
        elif arrow_states['up']:
            if self.current_screen == 0:
                self.selected_menu_item -= 1
                if self.selected_menu_item == -1:
                    self.selected_menu_item = 0
        elif arrow_states['down']:
            if self.current_screen == 0:
                self.selected_menu_item += 1
                if self.selected_menu_item == len(self.menu_items):
                    self.selected_menu_item = len(self.menu_items) - 1
            if self.current_screen == 1:
                self.current_screen = 0


if __name__ == '__main__':
    # запуск
    field = Field()
    field.main_game_cycle()
