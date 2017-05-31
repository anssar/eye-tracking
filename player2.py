import socket
import sys


class Channel():
    def __init__(self, port):
        print('Ждем соединения с соперником')
        self._port = port
        self._sock = socket.socket()
        self._sock.bind(('', self._port))
        self._sock.listen(1)
        self._channel, self._addr = self._sock.accept()
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
        message = b''
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


class Game():
    def __init__(self, channel):
        self._channel = channel
        self.round = 1
        self.player_score = 0
        self.opponent_score = 0

    def game(self):
        print('Игра началась')
        while True:
            print('Раунд {}'.format(self.round))
            print('Счет {}:{}'.format(self.player_score, self.opponent_score))
            print('Ожидайте число от соперника')
            self._channel.recv()
            print('Нажмите enter или введите exit')
            command = input()
            if command == 'exit':
                print('Итоговый счет {}:{}'.format(
                self.player_score, self.opponent_score))
                self._channel.send('exit')
                break
            self._channel.send('OK')
            print('Введите 1 если соперник сказал правду и 0 если ложь')
            try:
                answer = int(input())
                if answer not in [0, 1]:
                    raise Exception
            except Exception:
                print('Вы ввели не 1 или 0, ваш ответ заменен на 1')
                answer = 1
            self._channel.send(str(answer))
            mes = self._channel.recv()
            try:
                mes = mes.split(';')
                number = int(mes[0])
                lie = bool(int(mes[1]))
            except:
                print('ОШИБКА: получено неверное сообщение от соперника,' +
                ' вам начислено 25 очков')
                self.player_score += 25
                self.round += 1
                continue
            print('Число раунда {}'.format(number))
            print('Соперник должен был ' + (
            'солгать' if lie else 'сказать правду'))
            if int(lie) != answer:
                self.player_score += 25
            if lie:
                if int(lie) == answer:
                    self.opponent_score += 30
            else:
                self.opponent_score += 5
            self.round += 1
        print('Игра окончена')


if __name__ == '__main__':
    channel = Channel(14456)
    game = Game(channel)
    game.game()
    channel.close()
