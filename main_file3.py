import pygame
import start_window
import main_window
import music
import setting_window
import game_window
import deck_on_desk
import earls
import sys
import connection_window
import urllib.parse as up
import psycopg2
import copy
import time
import finish_window
import reset

# код на первой строке номер кода
# коды во второй строке -1 начальный 10 + игрок 11 - игрок 12 начало игры 1 взять гем 2 взять карту
# коды а третей строке параметр для взятия xx - два гема xyz - три гема xy - карта каждая буква вид гема
# код в четвёртой если при взятии гемов стало > 10 в виде x, xx, xxx, xy, xxy, xyz
# заготовка для использования золота
# код в 5 строке определять состояние игры 0 - не подключён хост 1 - игра начата 2 - закончилась
is_host = False
last_code = [(0, -1), (1, -1), (2, -1), (3, -1), (4, -1)]
count_of_players = 1
connected = False
start_game = False
id = 0
turn = 0
full_code = False
times = time.time()
result = False


def connection(link):
    try:
        up.uses_netloc.append("postgres")
        url = up.urlparse(link)

        conn = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password,
                                host=url.hostname,
                                port=url.port)
        return conn
    except psycopg2.OperationalError:
        return -1


def update(conn):
    cur = conn.cursor()
    cur.execute("""SELECT * FROM codes;""")
    result = cur.fetchall()
    cur.close()
    return result


def do_move(conn, move):
    cur = conn.cursor()
    for i in range(5):
        cur.execute(f"""UPDATE codes SET code={move[i]} WHERE id = {i}""")
    cur.close()
    conn.commit()


def create_table(conn):
    cur = conn.cursor()
    cur.execute("""DROP TABLE codes;""")
    cur.execute("""CREATE TABLE IF NOT EXISTS codes (
                        id integer,
                        code integer);""")
    for i in range(5):
        cur.execute(f"""INSERT INTO codes VALUES ({i}, 0);""")
    cur.close()
    conn.commit()


def create_second_table(conn):
    cur = conn.cursor()
    cur.execute('DROP TABLE data;')
    cur.execute("""CREATE TABLE data (
                        id integer,
                        data text);""")
    for i in range(2):
        cur.execute(f"""INSERT INTO data VALUES ({i}, '');""")
    cur.close()
    conn.commit()


def set_table(conn, data):
    cur = conn.cursor()
    for i in range(2):
        cur.execute(f"""UPDATE data SET data='{data[i]}' WHERE id={i}""")
    cur.close()
    conn.commit()


def get_data(conn):
    cur = conn.cursor()
    cur.execute("""SELECT * FROM data;""")
    result = cur.fetchall()
    cur.close()
    return result


def online(conn):
    global is_host
    global last_code
    global count_of_players
    global connected
    global start_game
    global id
    global players
    global turn
    global cards_on_desk
    global game
    global result
    cur = conn.cursor()
    cur.execute('''SELECT * FROM codes''')
    code = cur.fetchall()
    print(is_host)
    if code[4][1] == 0:
        print(4)
        is_host = True
    if is_host and code[0][1] == 0 and not connected:
        create_table(conn)
        do_move(conn, [code[0][1] + 1, 0, 0, 0, 1])
        id = 0
        connected = True
    elif not is_host and not connected:
        do_move(conn, [code[0][1] + 1, 10, 0, 0, 1])
        count_of_players = code[0][1]
        connected = True
        id = code[0][1]
    if code[0][1] != last_code[0][1]:
        if code[1][1] == 10:
            count_of_players += 1
        elif code[1][1] == 11:
            count_of_players -= 1
        elif code[1][1] == 12:
            start_game = True
        elif code[1][1] == 1:
            for j in range(len(str(code[2][1]))):
                players[turn][0][int(str(code[2][1])[j]) - 1] += 1
            print(players)
            turn += 1
            turn %= 2
        elif code[1][1] == 2:
            card = deck_on_desk.CARDS[cards_on_desk[int(str(code[2][1])[0]) - 1][int(str(code[2][1])[1]) - 1]]
            print(card)
            players[turn][1][card[1]] += 1
            for j in range(5):
                price_c = card[3][j] - players[turn][1][j]
                if price_c < 0:
                    price_c = 0
                players[turn][0][j] -= price_c
            for q in range(len(earls_list)):
                get_earl = True
                for j in range(5):
                    if players[turn][1][j] != earls.EARLS[earls_list[q]][j]:
                        get_earl = False
                        break
                if get_earl:
                    game.taken[q] = True
                    players[turn][2] += 3
            players[turn][2] += card[2]
            if players[turn][2] >= 15:
                do_move(conn, (code[0][1] + 1, 3, 0, 0, 0))
                if turn == id:
                    result = True
            turn += 1
            turn %= 2
            cards_on_desk[int(str(code[2][1])[0]) - 1][int(str(code[2][1])[1]) - 1] = code[3][1]
            print(players)
        elif code[1][1] == 3:
            start_game = 2
    print(last_code)
    last_code = copy.deepcopy(code)
    print(code, count_of_players, is_host)
    print(id, turn)


pygame.init()
info = pygame.display.Info()
wight, height = 300, 340
sc = pygame.display.set_mode((wight, height))
pygame.display.set_caption('Splendor')
win = start_window.StartWindow(sc, info.current_w, info.current_h)

clock = pygame.time.Clock()
fps = 60

running = True
with open('data/other/settings.txt') as file:
    settings = file.read().split('\n')
    file.close()

if settings[1] == '0':
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                win.checkbox1.change_flag(event)
                win.checkbox2.change_flag(event)
                if win.button.clicked(event):
                    win.save_settings()
                    running = False

                elif win.button_expand.clicked(event):
                    win.expand()

                elif win.is_expand:
                    x, y = event.pos
                    if 202 < x < 218 and 202 < y < 218:
                        win.up()

                    elif 202 < x < 218 and 242 < y < 258:
                        win.down()

                    elif 80 < x < 220 and 200 < y < 260:
                        win.select((y - 200) // 20)
        win.render()
        pygame.display.flip()
        clock.tick(fps)

with open('data/other/settings.txt') as file:
    settings = file.read().split('\n')
    file.close()
pygame.quit()
pygame.init()
size = wight, height = list(map(int, settings[0].split('x')))
sc = pygame.display.set_mode((wight, height))
if settings[2] == '1':
    pygame.display.toggle_fullscreen()
window = main_window.MainWindow(sc, size)
music.play_bg_music()
music.music_volume(float(settings[5]))
running = True
FPS = 60
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            output = window.clicked(event)
            if output == 0:
                running = False
            elif output == 1:
                window_set = setting_window.SettingWindow(sc, size)
                clock2 = pygame.time.Clock()
                running_2 = True
                while running_2:
                    events = pygame.event.get()
                    window_set.volume_input.update(events)
                    for event in events:
                        if event.type == pygame.QUIT:
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            output = window_set.clicked(event)
                            if output == 1:
                                if window_set.chechbox.flag:
                                    window_set.save()
                                running_2 = False
                    window_set.render()
                    pygame.display.flip()
                    clock2.tick(FPS)
            elif output == 2:
                running_2 = True
                with open('data/other/settings.txt') as file:
                    link = file.read().split('\n')[3]
                    file.close()
                window_conn = connection_window.ConnectWindow(sc, is_host, size)
                conn = connection(link)
                online(conn)
                times = time.time()
                while running_2:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            output = window_conn.clicked(event, count_of_players)
                            if output == -1:
                                sys.exit()
                            elif output == 1:
                                create_second_table(conn)
                                do_move(conn, [0, 12, 0, 0, 1])
                                gems = ['diamond', 'emerald', 'onyx', 'ruby', 'sapphire']
                                player_st = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], 0]
                                players = []
                                for i in range(count_of_players):
                                    players.append(copy.deepcopy(player_st))
                                print(players)
                                decks = deck_on_desk.set_decks()
                                cards_on_desk = [[-1, -1, -1, -1], [-1, -1, -1, -1], [-1, -1, -1, -1]]
                                decks, cards_on_desk = deck_on_desk.set_desk(decks, cards_on_desk)
                                cards = deck_on_desk.get_cards(cards_on_desk)
                                earls_list = earls.get_earls(count_of_players)
                                set_table(conn, (deck_on_desk.get_code(cards_on_desk), earls_list))
                                earls_list = list(map(int, earls_list.split('.')))
                                game = game_window.GameRender(sc, size, count_of_players, cards,
                                                              earls_list, full_code)
                                code = []
                                running_3 = True
                                while running_3:
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            sys.exit()
                                        elif event.type == pygame.MOUSEBUTTONDOWN:
                                            game.selected = (-1, -1)
                                            output = game.clicked(event)
                                            print(output)
                                            if output == -1:
                                                sys.exit()
                                            elif not game.full_code and type(output) == int and output < 9 and turn == id:
                                                if output in code and len(code) == 1:
                                                    code.append(output)
                                                    game.full_code = True
                                                elif len(code) == 2:
                                                    code.append(output)
                                                    game.full_code = True
                                                else:
                                                    code.append(output)
                                            elif type(output) == int and 9 < output < 99:
                                                print(output)
                                            elif game.full_code and output == 100 and turn == id:
                                                output_code = ''
                                                for elem in code:
                                                    output_code = f'{output_code}{elem}'
                                                print(code, output_code)
                                                if len(code) == 2 or (len(code) == 3 and code[2] != 0):
                                                    do_move(conn, [last_code[0][1] + 1, 1, output_code, 0, 1])
                                                else:
                                                    try:
                                                        new_card = decks[code[0] - 1].pop(0)
                                                    except IndexError:
                                                        new_card = -1
                                                    do_move(conn, [last_code[0][1] + 1, 2, output_code, new_card, 1])
                                                code = []
                                                game.full_code = False
                                            elif not game.full_code and type(output) == tuple and not code and turn == id:
                                                price = deck_on_desk.CARDS[cards_on_desk[output[0]][output[1]]][3]
                                                can_buy = True
                                                for i in range(5):
                                                    if not players[id][0][i] + players[id][1][i] >= price[i]:
                                                        can_buy = False
                                                        break
                                                if can_buy:
                                                    code.append(output[0] + 1)
                                                    code.append(output[1] + 1)
                                                    code.append(0)
                                                    game.full_code = True
                                            elif output == 101:
                                                code = []
                                                game.full_code = False
                                            elif game.full_code and output is not None:
                                                game.is_wrong = True
                                    if times + 2 < time.time():
                                        times = time.time()
                                        online(conn)
                                        if start_game == 2:
                                            running_3 = False
                                            reset.reset()
                                    cards = deck_on_desk.get_cards(cards_on_desk)
                                    game.render(cards, cards_on_desk)
                                    pygame.display.flip()
                                running_3 = True
                                fin_win = finish_window.FinishWindow(sc, wight, height, result)
                                while running_3:
                                    fin_win.render()
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                                            sys.exit()
                                    pygame.display.flip()
                            elif start_game:
                                data = get_data(conn)
                                cards_on_desk, earls_list = data[0][1], data[1][1]
                                cards_on_desk = cards_on_desk.split('-')
                                player_st = [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], 0]
                                players = []
                                for i in range(count_of_players):
                                    players.append(copy.deepcopy(player_st))
                                for i in range(3):
                                    cards_on_desk[i] = list(map(int, cards_on_desk[i].split(',')))
                                earls_list = list(map(int, earls_list.split('.')))
                                cards = deck_on_desk.get_cards(cards_on_desk)
                                game = game_window.GameRender(sc, size, count_of_players, cards,
                                                              earls_list, full_code)
                                code = []
                                running_3 = True
                                while running_3:
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                            sys.exit()
                                        elif event.type == pygame.MOUSEBUTTONDOWN:
                                            game.selected = (-1, -1)
                                            output = game.clicked(event)
                                            print(output)
                                            if output == -1:
                                                sys.exit()
                                            elif not game.full_code and type(
                                                    output) == int and output < 9 and turn == id:
                                                if output in code and len(code) == 1:
                                                    code.append(output)
                                                    game.full_code = True
                                                elif len(code) == 2:
                                                    code.append(output)
                                                    game.full_code = True
                                                else:
                                                    code.append(output)
                                            elif type(output) == int and 9 < output < 99:
                                                print(output)
                                            elif game.full_code and output == 100 and turn == id:
                                                output_code = ''
                                                for elem in code:
                                                    output_code = f'{output_code}{elem}'
                                                print(code, output_code)
                                                if code[0] == code[1] or (len(code) == 3 and code[2] != 0):
                                                    do_move(conn, [last_code[0][1] + 1, 1, output_code, 0, 1])
                                                else:
                                                    do_move(conn, [last_code[0][1] + 1, 2, output_code, 0, 1])
                                                code = []
                                                game.full_code = False
                                            elif not game.full_code and type(
                                                    output) == tuple and not code and turn == id:
                                                price = deck_on_desk.CARDS[cards_on_desk[output[0]][output[1]]][3]
                                                can_buy = True
                                                for i in range(5):
                                                    if not players[id][0][i] + players[id][1][i] >= price[i]:
                                                        can_buy = False
                                                        break
                                                if can_buy:
                                                    code.append(output[0] + 1)
                                                    code.append(output[1] + 1)
                                                    code.append(0)
                                                    game.full_code = True
                                            elif output == 101:
                                                code = []
                                                game.full_code = False
                                            elif game.full_code and output is not None:
                                                game.is_wrong = True
                                    if times + 2 < time.time():
                                        times = time.time()
                                        online(conn)
                                        if start_game == 2:
                                            running_3 = False
                                    cards = deck_on_desk.get_cards(cards_on_desk)
                                    game.render(cards, cards_on_desk)
                                    pygame.display.flip()
                                running_3 = True
                                fin_win = finish_window.FinishWindow(sc, wight, height, result)
                                while running_3:
                                    fin_win.render()
                                    for event in pygame.event.get():
                                        if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                                            sys.exit()
                                    pygame.display.flip()
                    if times + 2 < time.time():
                        times = time.time()
                        online(conn)
                        window_conn.is_host = is_host
                    window_conn.render(count_of_players)
                    pygame.display.flip()
    window.render()
    pygame.display.flip()
