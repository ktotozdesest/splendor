import os
import sys
import pygame
from image_for_sprite import *
from pathlib import Path
import random
import button
import deck_on_desk
import earls

COLORS = [pygame.Color(255, 0, 0), pygame.Color(0, 255, 0), pygame.Color(122, 32, 32),
          pygame.Color(0, 0, 255), pygame.Color(255, 255, 255)]


class GameRender:
    def __init__(self, surface, size, player_number, card_list, earl_list, full_code):
        self.player_number = player_number
        self.gem_list = [7 for _ in range(5)] + [5]
        self.inventory_gems = [0 for _ in range(6)]
        self.screen = surface
        self.card_list = card_list
        self.buttons_cards = []
        self.size = size
        self.earl_list = earl_list
        self.full_code = full_code
        self.now_player = 0
        self.selected = (-1, -1)
        for i in range(3):
            self.buttons_cards.append([])
            for j in range(4):
                self.buttons_cards[i].append(button.Button(self.screen, (0, 0, 0, 0), weight=-1))
        self.buttons_gems = []
        for i in range(6):
            self.buttons_gems.append(button.Button(self.screen, (0, 0, 0, 0), weight=-1))
        self.font = pygame.font.Font(None, size[1] // 40)
        self.font2 = pygame.font.Font('data/other/Standrag.otf', size[1] // 20)
        self.right_border = 170 * (self.size[1] / 9000)
        self.taken = [False] * (player_number + 1)
        self.font3 = pygame.font.Font(None, size[1] // 7)
        self.font4 = pygame.font.Font('data/other/Standrag.otf', size[1] // 10)
        self.buttons_players = []
        text_exit = self.font4.render('Exit', True, (0, 0, 0))
        text_move = self.font4.render('Do move', True, (0, 0, 0))
        self.button = button.Button(self.screen,
                                    (size[0] // 6 * 5, size[1] // 6 * 5, size[0] // 10, size[1] // 12),
                                    weight=-1, text=text_exit)
        self.button_move = button.Button(self.screen,
                                         (size[0] // 8 * 7, size[1] // 3 * 2, size[0] // 14, size[1] // 12),
                                         weight=-1, text=text_move)
        self.is_wrong = False
        self.text_wrong = self.font3.render('Wrong move', True, (255, 0, 0))
        text_back = self.font4.render('Back move', True, (0, 0, 0))
        self.button_back = button.Button(self.screen,
                                         (size[0] // 8 * 7, size[1] // 2, size[0] // 14, size[1] // 12),
                                         weight=-1, text=text_back)

    def render(self, cards, cards_price):
        all_sprites = pygame.sprite.Group()
        bg_sprites = pygame.sprite.Group()
        # задний план - заглушка
        sprite = pygame.sprite.Sprite(bg_sprites)
        sprite.image = load_image("bg3.png")
        sprite.image = pygame.transform.scale(sprite.image, (2000, 1500))
        sprite.rect = sprite.image.get_rect()
        bg_sprites.draw(self.screen)
        # фон инвентаря - заглушка
        sprite = pygame.sprite.Sprite(all_sprites)
        sprite.image = load_image("inventory.jpg")
        sprite.image = pygame.transform.scale(sprite.image,
                                              (sprite.image.get_size()[0] / sprite.image.get_size()[1] * self.size[1],
                                               self.size[1]))
        sprite.rect = sprite.image.get_rect()
        sprite.rect.x = self.size[0] - 300 * (self.size[1] / 1000)
        # размещение уровней
        card_dir = Path('data/cards')
        card_move = 0
        for card_lv in card_dir.glob('card_*'):
            sprite = pygame.sprite.Sprite(all_sprites)
            sprite.image = pygame.transform.scale(load_all_image(card_lv), (120 * (self.size[1] / 1000),
                                                                            170 * (self.size[1] / 1000)))
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = 50 * (self.size[1] / 1000)
            sprite.rect.y = 200 * (self.size[1] / 1000) * card_move + 185 * (self.size[1] / 1000)
            card_move += 1
        # размещение карт
        for i in range(12):

            card_group = pygame.sprite.Group()
            sprite = pygame.sprite.Sprite(card_group)
            sprite.image = pygame.transform.scale(load_image_card(f'{cards[i]}_mine.png'),
                                                  (120 * (self.size[1] / 1000),
                                                   170 * (self.size[1] / 1000)))
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = 50 * (self.size[1] / 1000) + 150 * (self.size[1] / 1000) * (i % 4 + 1)
            sprite.rect.y = 200 * (self.size[1] / 1000) * (i // 4) + 185 * (self.size[1] / 1000)
            self.buttons_cards[i // 4][i % 4].pos = (sprite.rect[0], sprite.rect[1], sprite.rect[2], sprite.rect[3])
            if i // 4 == self.selected[0] and i % 4 == self.selected[1]:
                pygame.draw.rect(self.screen, pygame.Color(0, 255, 0),
                                 (sprite.rect.x - 2, sprite.rect.y - 2, 120 * (self.size[1] / 1000) + 4,
                                  170 * (self.size[1] / 1000) + 4))
            card_group.draw(self.screen)
            price = deck_on_desk.CARDS[cards_price[i // 4][i % 4]][3]
            real_price = []
            for j in range(5):
                if price[j] != 0:
                    real_price.append(j)
            rad = 250 * (self.size[1] / 18000)
            up_border = 170 * (self.size[1] / 1000) - ((len(real_price)) * 2) * rad
            for j in range(len(real_price)):
                color = COLORS[real_price[j]]
                pygame.draw.circle(self.screen, color, (sprite.rect.x + self.right_border, sprite.rect.y + up_border),
                                   rad, width=0)
                text = self.font.render(str(price[real_price[j]]), True, (0, 0, 0))
                self.screen.blit(text,
                                 text.get_rect(center=(sprite.rect.x + self.right_border, sprite.rect.y + up_border)))
                up_border += 2.25 * rad
            text2 = self.font2.render(str(deck_on_desk.CARDS[cards_price[i // 4][i % 4]][2]), True,
                                      (100, 100, 100))
            self.screen.blit(text2, text2.get_rect(center=(sprite.rect.x + rad, sprite.rect.y + rad * 2)))

        # вельможи
        for i in range(self.player_number + 1):
            ears_group = pygame.sprite.Group()
            sprite = pygame.sprite.Sprite(ears_group)
            if self.taken[i]:
                sprite.image = pygame.transform.scale(load_image("ava.png"), (120 * (self.size[1] / 1000),
                                                                              120 * (self.size[1] / 1000)))
                sprite.rect = sprite.image.get_rect()
                sprite.rect.x = 150 * (self.size[1] / 1000) * i + 50 * (self.size[1] / 1000)
                sprite.rect.y = 50 * (self.size[1] / 1000)
                ears_group.draw(self.screen)
            else:
                sprite.image = pygame.transform.scale(load_image_earl(f"earl{i + 1}.png"),
                                                      (120 * (self.size[1] / 1000), 120 * (self.size[1] / 1000)))
                sprite.rect = sprite.image.get_rect()
                sprite.rect.x = 150 * (self.size[1] / 1000) * i + 50 * (self.size[1] / 1000)
                sprite.rect.y = 50 * (self.size[1] / 1000)
                ears_group.draw(self.screen)
                price = earls.EARLS[self.earl_list[i]]
                real_cost = []
                for j in range(len(price)):
                    if price[j] != 0:
                        real_cost.append(j)
                up_border_earl = 120 * (self.size[1] / 1000) - 15 * (self.size[1] / 1000) * len(real_cost) - \
                                 15 * (self.size[1] / 1000) * (len(real_cost) - 1)
                right_border = self.size[1] // 100
                for j in range(len(real_cost)):
                    color = COLORS[real_cost[j]]
                    pygame.draw.rect(self.screen, color,
                                     (sprite.rect.x + right_border, sprite.rect.y + up_border_earl,
                                      right_border * 2.5, 20 * (self.size[1] / 1000)),
                                     width=0)
                    text = self.font.render(str(earls.EARLS[self.earl_list[i]][real_cost[j]]), True, (0, 0, 0))
                    self.screen.blit(text, text.get_rect(
                        center=(right_border * 2 + sprite.rect.x, up_border_earl + right_border + sprite.rect.y)))
                    up_border_earl += 25 * (self.size[1] / 1000)
                text2 = self.font2.render('3', True, (100, 100, 100))
                self.screen.blit(text2, text2.get_rect(
                    center=(right_border * 1.2 + sprite.rect.x, sprite.rect.y + 30 * (self.size[1] / 1000))))

        # ресурсы
        gem_dir = Path('data/gems')
        gem_move = 0
        for gem in gem_dir.glob('*.png'):
            sprite = pygame.sprite.Sprite(all_sprites)
            sprite.image = pygame.transform.scale(load_all_image(gem), (80 * (self.size[1] / 1000),
                                                                        80 * (self.size[1] / 1000)))
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = 800 * (self.size[1] / 1000)
            sprite.rect.y = 100 * (self.size[1] / 1000) * gem_move + 175 * (self.size[1] / 1000)
            self.buttons_gems[gem_move].pos = (sprite.rect[0], sprite.rect[1], sprite.rect[2], sprite.rect[3])
            gem_move += 1
        # игроки
        for i in range(self.player_number):
            player_group = pygame.sprite.Group()
            sprite = pygame.sprite.Sprite(player_group)
            sprite.image = pygame.transform.scale(load_image("ava.png"), (120 * (self.size[1] / 1000),
                                                                          120 * (self.size[1] / 1000)))
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = 150 * (self.size[1] / 1000) * i + 50 * (self.size[1] / 1000)
            sprite.rect.y = self.size[1] - (50 * (self.size[1] / 1000) + sprite.image.get_size()[1])
            player_group.draw(self.screen)
            self.buttons_players.append(button.Button(self.screen, (sprite.rect.x,
                                                                    sprite.rect.y,
                                                                    (120 * (self.size[1] / 1000)),
                                                                    (120 * (self.size[1] / 1000))
                                                                    ),
                                                      weight=-1))
            if i == 0:
                text = self.font3.render('I', True, (0, 0, 0))
                self.screen.blit(text, text.get_rect(center=(sprite.rect.x + 60 * (self.size[1] / 1000),
                                                             sprite.rect.y + 80 * (self.size[1] / 1000))))

        all_sprites.draw(self.screen)
        font = pygame.font.Font(None, int(30 * (self.size[1] / 1000)))
        text = font.render(f"{self.inventory_gems[-1]}", True, (0, 0, 0))
        self.screen.blit(text, (
            self.size[0] - 60 * (self.size[1] / 1000), 30 * (self.size[1] / 1000) * 5 + 25 * (self.size[1] / 1000)))
        self.button.render()
        if self.full_code:
            self.button_move.render()
        if self.is_wrong:
            self.screen.blit(self.text_wrong, (self.size[0] // 5 * 3, self.size[1] // 2))
        self.button_back.render()

    def render_inventory(self, players):
        for i in range(5):
            # кол-во ресов в свободном доступе
            font = pygame.font.Font(None, int(75 * (self.size[1] / 1000)))
            text = font.render(f"{self.gem_list[i]} / 7", True, (0, 0, 0))
            self.screen.blit(text,
                             (900 * (self.size[1] / 1000),
                              100 * (self.size[1] / 1000) * i + 180 * (self.size[1] / 1000)))
            # в инвентаре
            font = pygame.font.Font(None, int(30 * (self.size[1] / 1000)))
            text = font.render(f"{self.inventory_gems[i]}", True, (0, 0, 0))
            self.screen.blit(text, (
                self.size[0] - 60 * (self.size[1] / 1000), 30 * (self.size[1] / 1000) * i + 25 * (self.size[1] / 1000)))

    def clicked(self, event):
        for i in range(3):
            for j in range(4):
                if self.buttons_cards[i][j].clicked(event):
                    self.selected = (i, j)
                    return i, j
        for i in range(6):
            if self.buttons_gems[i].clicked(event):
                return i + 1
        for i in range(self.player_number):
            if self.buttons_players[i].clicked(event):
                return (i + 1) * 10
        if self.button.clicked(event):
            return -1
        if self.full_code and self.button_move.clicked(event):
            return 100
        if self.button_back.clicked(event):
            return 101
        self.is_wrong = False


if __name__ == '__main__':
    pygame.init()
    try:
        size = 1920, 1024
        screen = pygame.display.set_mode(size)
        count_of_players = 4
        gems = ['diamond', 'emerald', 'onyx', 'ruby', 'sapphire']
        decks = deck_on_desk.set_decks()
        cards_on_desk = [[-1, -1, -1, -1], [-1, -1, -1, -1], [-1, -1, -1, -1]]
        # decks, cards_on_desk = deck_on_desk.set_desk(decks, cards_on_desk)
        cards = deck_on_desk.get_cards(cards_on_desk)
        earls_list = list(map(int, earls.get_earls(count_of_players).split('.')))
        print(earls_list)
        game = GameRender(screen, size, count_of_players, cards, earls_list, True)
        running = True
        while running:
            game.render(cards_on_desk)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    print(game.clicked(event))
            pygame.display.flip()

    except Exception as e:
        print(e)
