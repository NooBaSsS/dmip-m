import os
from random import choice, randint, shuffle
import keyboard
import time


RULES = ''

PLAYER_MAX_SPEED = 10  # максимальная скорость игрока
FRAME_WIDTH = 40  # ширина поля
FRAME_HEIGHT = 20  # высота поля
HOLES = int((FRAME_HEIGHT * FRAME_WIDTH) / 40)  # общее количество дыр. подстраивается под размер экрана
PLAYER_START_X = FRAME_WIDTH - int(FRAME_WIDTH * 0.3)  # начальная позиция игрока по ширине. подстраивается под размер экрана так, чтобы игрок был чуть правее
PLAYER_START_Y = FRAME_HEIGHT - int(FRAME_HEIGHT * 0.3)  # начальная позиция игрока по высоте. подстраивается под размер экрана так, чтобы игрок был чуть ниже
PLAYER_START_FRAME = 9  # начальный 'экран', на котором размещается игрок
BASE_X = FRAME_WIDTH - int(FRAME_WIDTH * 0.7)  # начальная позиция базы по ширине. подстраивается под размер экрана так, чтобы база была чуть левее
BASE_Y = FRAME_WIDTH - int(FRAME_WIDTH * 0.9)  # начальная позиция базы по высоте. подстраивается под размер экрана так, чтобы база была чуть выше
BASE_FRAME = 1  # 'экран', на котором размещается база
arrow_states = {'left': False, 'right': False, 'up': False, 'down': False, 'enter': False, 'esc': False} # состояние клавиш, изменяется во время работы программы

DIRECTION_ARROWS = {  # стрелки для отображения направления игрока
    'Left': '←',
    'Up': '↑',
    'Right': '→',
    'Down': '↓',
    'UpperLeft': '↖',
    'UpperRight': '↗',
    'LowerRight': '↘',
    'LowerLeft': '↙',
}
DIRECTIONS = [  # возможные направления игрока
    'Left',
    'UpperLeft',
    'Up',
    'UpperRight',
    'Right',
    'LowerRight',
    'Down',
    'LowerLeft',
]


LOGO = "  _____       _                _       _ _            \n  \_   \_ __ | |_ ___ _ __ ___| |_ ___| | | __ _ _ __ \n   / /\/ '_ \| __/ _ \ '__/ __| __/ _ \ | |/ _` | '__|\n/\/ /_ | | | | ||  __/ |  \__ \ ||  __/ | | (_| | |   \n\____/ |_| |_|\__\___|_|  |___/\__\___|_|_|\__,_|_|   \n"
GAME_OVER_TEXT = " _____                        _____                \n|  __ \                      |  _  |               \n| |  \/ __ _ _ __ ___   ___  | | | |_   _____ _ __ \n| | __ / _` | '_ ` _ \ / _ \ | | | \ \ / / _ \ '__|\n| |_\ \ (_| | | | | | |  __/ \ \_/ /\ V /  __/ |   \n \____/\__,_|_| |_| |_|\___|  \___/  \_/ \___|_|   \n                                                   \n                                                   "
MISSION_COMPLETE_TEXT = "___  ____         _               _____                       _      _       \n|  \/  (_)       (_)             /  __ \                     | |    | |      \n| .  . |_ ___ ___ _  ___  _ __   | /  \/ ___  _ __ ___  _ __ | | ___| |_ ___ \n| |\/| | / __/ __| |/ _ \| '_ \  | |    / _ \| '_ ` _ \| '_ \| |/ _ \ __/ _ \ \n| |  | | \__ \__ \ | (_) | | | | | \__/\ (_) | | | | | | |_) | |  __/ ||  __/\n\_|  |_/_|___/___/_|\___/|_| |_|  \____/\___/|_| |_| |_| .__/|_|\___|\__\___|\n                                                       | |                   \n                                                       |_|                   "
CONTROL_HINTS = '\nУправление:\n    ↑ - ускориться\n    ↓ - замедлиться\n    ← - повернуть влево\n    → - повернуть вправо\n    Esc - выход\n    ENTER - убрать подсказки и легенду\n\nЛегенда:\n    \033[31m↑\033[37m - ваш корабль\n    \033[37;40m4\033[37;40m - черная дыра\n    \033[30;47m4\033[37;40m - белая дыра\n    \u2756 - обломок материи\n    \033[32;43m\u2302\033[37;40m - база\n'
TUTORIAL_TEXT = [
    '\033[1mИнтерстеллар: Путешествие сквозь бездну\033[0m\nВы – отважный космический исследователь, летящий на своём корабле сквозь звёздную пыль и обломки былых планет на окраинах Вселенной. Никто не мог предположить такого, но на Вашем пути оказывается слишком много препятствий.\n\nНа вашем пути – смертельные чёрные дыры, поглощающие всё вокруг, и загадочные белые дыры, отбрасывающие прочь всё, что приближается. Их гравитация играет с траекторией корабля, меняя его путь. Разбросанные по пространству обломки материи скрывают угрозу — столкновение с ними означает неминуемую гибель.\n\nЦель вашей миссии - добраться до базы. Преодолейте опасности, докажите, что даже в самом хаотичном и неизведанном пространстве можно найти дорогу. Удачи, капитан!',
    '\033[1mИнтерфейс\033[0m\n┏━┓\n┃\033[44m \033[40m┃\n┗━┛ - это поле. Под ним находится карта и скорость вашего корабля.\n\nКарта отображает на каком сейчас "экране" вы находитесь.\n\nСкорость показывает текущую скорость вашего корабля.',
    '\033[1mИгрок\033[0m\n↑ - это ваш корабль.\nВы можете управлять им с помощью стрелок на вашей клавиатуре:\n    вверх-ускориться\n    вниз-замедлиться\n    влево/вправо-повернуть в соответствующем направлении\nПри полной остановке корабля игра останавливается, так что вы сможете продумать свои будущие действия',
    '\033[1mЧерные и белые дыры\033[0m\nВ космосе вам могут встретиться черные и белые дыры.\n\n\033[37;40m4\033[37;40m - это черная дыра. Цифра обозначает радиус действия этой дыры. Попав в зону действия дыры она начинает притягивать ваш корабль. Если корабль попадет прямиком в дыру его выбросит из случайной былой дыры.\n\n\033[30;47m4\033[37;40m - это белая дыра. Цифра обозначает радиус действия этой дыры. Попав в зону действия этой дыры она начинает отталкивать ваш корабль. Если корабль попадет прямиком в дыру она оттолкнет его в случайную точку на текущем экране. Будьте осторожны - вас может отбросить прямо в обломки материи!',
    '\033[1mОбломки материи\033[0m\nКосмос заполнен обломками материи.\n\u2756 - это обломок материи. Они находятся на поле статично. При столкновении с ними ваш корабль разобьется и вы проиграете.',
    '\033[1mБаза\033[0m\nВаша цель - добраться до базы.\n\033[32;43m\u2302\033[37;40m - это база. Вам нужно прилететь на базу, сделав это вы завершите свою миссию.'
]