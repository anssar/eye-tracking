import socket
import sys
import random
import string
import time


class Channel():
    def __init__(self, ip, port):
        print('Ждем соединения с соперником')
        self._ip = ip
        self._port = port
        try:
            self._channel = socket.socket()
            self._channel.connect((self._ip, self._port))
        except Exception:
            print('Не удалось установить соединение')
            sys.exit()
        print('Соединение установлено')

    def send(self, message):
        attempt = 1
        try:
            self._channel.send(message.encode())
        except Exception:
            if attempt == 3:
                print('Соединение разорвано')
                sys.exit()
            attempt += 1

    def recv(self):
        attempt = 1
        try:
            message = self._channel.recv(1024)
            return message.decode()
        except Exception:
            if attempt == 3:
                print('Соединение разорвано')
                sys.exit()
            attempt += 1

    def close(self):
        try:
            self._channel.close()
            print('Соединение закрыто')
        except Exception:
            print('Соединение разорвано')
            sys.exit()


class Timestamper():
    def __init__(self):
        self._session = ''.join(random.choice(string.ascii_uppercase)
        for i in range(8))
        self._log = open('timestamps' + self._session, 'w')

    def write(self, round, start, finish):
        self._log.write(';'.join([str(x) for x in [round, start, finish]])
        + '\n')

    def close(self):
        self._log.close()


class Game():
    def __init__(self, channel, timestamper):
        self._channel = channel
        self._timestamper = timestamper
        self.round = 1
        self.player_score = 0
        self.opponent_score = 0

    def game(self):
        print('Игра началась')
        while True:
            number = random.randrange(10)
            lie = bool(random.randrange(2))
            print('Раунд {}'.format(self.round))
            print('Счет {}:{}'.format(self.player_score, self.opponent_score))
            print('Нажмите enter или введите exit')
            command = input()
            if command == 'exit':
                print('Итоговый счет {}:{}'.format(
                self.player_score, self.opponent_score))
                break
            print('Число раунда {}'.format(number))
            print(('Солгите' if lie else 'Скажите правду') +
            ', после чего нажмите enter')
            start = int(time.time() * 1000000)
            input()
            self._channel.send('OK')
            mes = self._channel.recv()
            if mes == 'exit':
                print('Соперник закончил игру')
                print('Итоговый счет {}:{}'.format(
                self.player_score, self.opponent_score))
                break
            finish = int(time.time() * 1000000)
            try:
                answer = int(self._channel.recv())
                if answer not in [0,1]:
                    raise Exception
            except Exception:
                print('ОШИБКА: соперник прислал некорректный ответ')
                answer = 1
            print('Соперник считает, что вы ' + (
            'говорите правду' if bool(answer) else 'лжете'))
            if answer != int(lie):
                self.opponent_score += 25
            if not lie:
                self.player_score += 5
            else:
                if answer == int(lie):
                    self.player_score += 30
            self._channel.send(str(number) + ';' + str(int(lie)))
            self._timestamper.write(self.round, start, finish)
            self.round += 1
        print('Игра окончена')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Введите ip соперника в качестве аргумента')
        sys.exit()
    timestamper = Timestamper()
    channel = Channel(sys.argv[1], 14457)
    game = Game(channel, timestamper)
    game.game()
    channel.close()
    timestamper.close()
