from random import randint


class BoardException(Exception):
    pass


class BoardOutExc(BoardException):
    def __str__(self):
        return 'Такого поля нет, попробуй еще раз.'


class BoardUseExc(BoardException):
    def __str__(self):
        return 'Еще раз сюда? Давай в другое место.'


class BoardShipExc(BoardException):
    pass


class Dot():
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship():
    def __init__(self, lenght, f, s):
        self.lenght = lenght
        self.f = f
        self.s = s
        self.lives = f

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.f):
            x1 = self.lenght.x
            y1 = self.lenght.y
            if self.s == 0:
                x1 += i
            elif self.s == 1:
                y1 += i
            ship_dots.append(Dot(x1, y1))
        return ship_dots

    def ripper(self, shot):
        return shot in self.dots


class Board():
    def __init__(self, hid=False, size=6):
        self.hid = hid
        self.size = 6
        self.rip = 0
        self.field = [['_'] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        paint = ''
        paint += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            paint += f'\n{i + 1} | ' + ' | '.join(row) + ' |'
        if self.hid:
            paint = paint.replace("■", "_")
        return paint

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near_ship = [(-1, 1), (-1, 0), (-1, -1), (1, 1), (1, 0), (1, -1), (0, 1), (0, 0), (0, -1)]
        for d in ship.dots:
            for dx, dy in near_ship:
                d1 = Dot(d.x + dx, d.y + dy)
                if not (self.out(d1)) and d1 not in self.busy:
                    if verb:
                        self.field[d1.x][d1.y] = "*"
                    self.busy.append(d1)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardShipExc
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutExc
        if d in self.busy:
            raise BoardUseExc
        self.busy.append(d)
        for ship in self.ships:
            if ship.ripper(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.rip += 1
                    self.contour(ship, verb=True)
                    print('Военный корабль идет на...')
                    return False
                else:
                    print('Попал!')
                    return True
        self.field[d.x][d.y] = '*'
        print('Мимо =(')
        return False

    def begin(self):
        self.busy = []


class Player():
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Мой ход: {d.x + 1}, {d.y + 1}')
        return d


class User(Player):
    def ask(self):
        while True:
            coord = input('Куда стреляем?: ')
            coord = coord.split()
            if len(coord) != 2:
                print('Введи 2 координаты\nПример: 2 3')
                continue

            x, y = coord
            if not (x.isdigit()) or not (y.isdigit()):
                print('Введи числовые координаты\nПример: 2 3')
                continue

            x = int(x)
            y = int(y)
            return Dot(x - 1, y - 1)


class Game():
    def game_board(self):
        leight = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        num = 0
        for i in leight:
            while True:
                num += 1
                if num > 1337:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardShipExc:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.game_board()
        return board

    def __init__(self, size=6):
        self.size = size
        man = self.random_board()
        comp = self.random_board()
        comp.hid = True
        self.ai = AI(comp, man)
        self.us = User(man, comp)

    def greet(self):
        print('Добро пожаловать в игру Морской Бой by Caramba v0.4\n____________')
        print('Правила игры:\nИгра против компьютера,\nДля выбора поля для атаки:')
        print('Введите координаты точки\nСначала координаты слева, далее координаты сверху\nПример: 2 4')

    def loop(self):
        step = 0
        while True:
            print('_________________\nТвое поле: ')
            print(self.us.board)
            print('_________________\nПоле компуктера: ')
            print(self.ai.board)
            print('_________________\n=================')
            if step % 2 == 0:
                print('Твой ход.')
                repeat = self.us.move()
            else:
                print('Ход компьютера: ')
                repeat = self.ai.move()
            if repeat:
                step -= 1
            if self.ai.board.rip == 7:
                print('Вражеский флот разбит!\n Слава игроку!')
                break
            if self.us.board.rip == 7:
                print('Твой флот потоплен =(')
                break
            step += 1

    def start(self):
        self.greet()
        self.loop()


go = Game()
print(go.start())
