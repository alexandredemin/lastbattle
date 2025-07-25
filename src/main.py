import pygame
from enum import Enum

# === Theme and State Management ===
class MenuTheme:
    def __init__(self, font=None, font_size=48,
                 font_color=(200,200,200), selected_color=(255,100,100),
                 bg_color=(10,10,50), spacing=20):
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.selected_color = selected_color
        self.bg_color = bg_color
        self.spacing = spacing

class GameState(Enum):
    MAIN = 1
    MAP = 2
    PLAYERS = 3

class MenuItem:
    """
    Описывает один пункт меню с разными типами поведения:
      - action: обычный пункт, по Enter возвращает id
      - preset: выбор из списка опций
      - value: числовая настройка с инкрементом/декрементом
    """
    def __init__(self, item_type, id, label, **kwargs):
        self.type = item_type
        self.id = id
        self.label = label
        if self.type == 'preset':
            self.options = kwargs.get('options', {})
            self.keys = list(self.options.keys())
            self.current = kwargs.get('current', self.keys[0])
        elif self.type == 'value':
            self.value = kwargs.get('value', 0)
            self.min = kwargs.get('min', 0)
            self.max = kwargs.get('max', 100)
            self.step = kwargs.get('step', 1)
            self.suffix = kwargs.get('suffix', '')

    def display_text(self):
        if self.type == 'action':
            return self.label
        elif self.type == 'preset':
            return f"{self.label}: {self.current}"
        elif self.type == 'value':
            return f"{self.label}: {self.value}{self.suffix}"

class Menu:
    def __init__(self, surface, items, theme: MenuTheme):
        self.surface = surface
        self.font = pygame.font.Font(theme.font, theme.font_size)
        self.font_color = theme.font_color
        self.selected_color = theme.selected_color
        self.bg_color = theme.bg_color
        self.spacing = theme.spacing
        self.items = items
        self.selected_index = 0
        self.base_x = None  # Фиксированная позиция меню по горизонтали
        self._item_rects = []  # Инициализация прямоугольников для элементов
        self._rebuild_labels()

    def _rebuild_labels(self):
        self.labels = []
        for item in self.items:
            text = item.display_text()
            normal = self.font.render(text, True, self.font_color)
            selected = self.font.render(text, True, self.selected_color)
            self.labels.append((normal, selected))
        # Сброс base_x при изменении ширины меню
        # self.base_x = None

    def draw(self):
        self.surface.fill(self.bg_color)
        # Вычисляем общую высоту
        total_h = sum(lbl.get_height() for lbl,_ in self.labels) + self.spacing*(len(self.labels)-1)
        start_y = (self.surface.get_height() - total_h) // 2
        # Вычисление base_x только один раз, при первой отрисовке или после изменения меток
        if self.base_x is None:
            max_w = max(normal.get_width() for normal,_ in self.labels)
            self.base_x = (self.surface.get_width() - max_w) // 2
        # Рисуем пункты начиная от base_x
        self._item_rects = []
        for idx, (normal, selected) in enumerate(self.labels):
            surf = selected if idx == self.selected_index else normal
            x = self.base_x
            y = start_y + idx * (surf.get_height() + self.spacing)
            self.surface.blit(surf, (x, y))
            self._item_rects.append(pygame.Rect(x, y, surf.get_width(), surf.get_height()))

    def handle_event(self, event):
        current = self.items[self.selected_index]
        # Mouse move
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            for idx, rect in enumerate(self._item_rects):
                if rect.collidepoint(mx, my):
                    self.selected_index = idx
                    break
            return None
        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for idx, rect in enumerate(self._item_rects):
                if rect.collidepoint(mx, my):
                    item = self.items[idx]
                    if event.button == 1:
                        if item.type == 'action':
                            return item.id
                        elif item.type == 'preset':
                            k = item.keys.index(item.current)
                            item.current = item.keys[(k+1) % len(item.keys)]
                        elif item.type == 'value':
                            item.value = item.min if item.value + item.step > item.max else item.value + item.step
                    elif event.button == 3 and item.type == 'value':
                        item.value = item.max if item.value - item.step < item.min else item.value - item.step
                    self._rebuild_labels()
                    return None
        # Keyboard events (↑↓←→, Enter)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
                return None
            if event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
                return None
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                if current.type == 'preset':
                    k = current.keys.index(current.current)
                    delta = -1 if event.key == pygame.K_LEFT else 1
                    current.current = current.keys[(k + delta) % len(current.keys)]
                elif current.type == 'value':
                    delta = -current.step if event.key == pygame.K_LEFT else current.step
                    new = current.value + delta
                    if new > current.max:
                        current.value = self.items[self.selected_index].min
                    elif new < current.min:
                        current.value = self.items[self.selected_index].max
                    else:
                        current.value = new
                self._rebuild_labels()
                return None
            if event.key == pygame.K_RETURN and current.type == 'action':
                return current.id
        return None

# =======================
# Основная программа
# =======================
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    common_theme = MenuTheme(font=None, font_size=48,
                              font_color=(200,200,200), selected_color=(255,100,100),
                              bg_color=(10,10,50), spacing=20)

    main_items = [
        MenuItem('action', 'new_game', 'Новая игра'),
        MenuItem('action', 'load_game', 'Продолжить'),
        MenuItem('action', 'quit', 'Выход'),
    ]
    main_menu = Menu(screen, main_items, common_theme)

    map_items = [
        MenuItem('preset', 'size', 'Размер', options={
            'Маленькая': (50,30), 'Средняя': (100,60), 'Большая': (150,90)
        }, current='Средняя'),
        MenuItem('value', 'land', 'Суша', value=35, min=0, max=100, step=5, suffix='%'),
        MenuItem('action', 'continue_map', 'Продолжить'),
        MenuItem('action', 'back_map', 'Назад'),
    ]
    map_menu = Menu(screen, map_items, common_theme)

    players_items = []
    for i in range(5):
        players_items.append(
            MenuItem('preset', f'player_{i+1}_type', f'Игрок {i+1}',
                     options={'Человек':'human', 'Компьютер':'computer', 'Нет':None},
                     current='Человек' if i < 2 else 'Нет')
        )
    players_items.append(MenuItem('action', 'continue_players', 'Продолжить'))
    players_items.append(MenuItem('action', 'back_players', 'Назад'))
    players_menu = Menu(screen, players_items, common_theme)

    menus = {
        GameState.MAIN: main_menu,
        GameState.MAP: map_menu,
        GameState.PLAYERS: players_menu,
    }

    state = GameState.MAIN
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            result = menus[state].handle_event(event)
            if result:
                if result == 'new_game':
                    state = GameState.MAP
                elif result == 'back_map':
                    state = GameState.MAIN
                elif result == 'continue_map':
                    state = GameState.PLAYERS
                elif result == 'back_players':
                    state = GameState.MAP
                elif result == 'continue_players':
                    size_key = map_items[0].current
                    map_w, map_h = map_items[0].options[size_key]
                    land_ratio = map_items[1].value
                    player_types = [
                        item.options[item.current]
                        for item in players_items
                        if item.type == 'preset'
                    ]
                    print(f"Начинаем игру: карта {map_w}×{map_h}, суша={land_ratio}%")
                    print(f"Типы игроков: {player_types}")
                elif result == 'quit':
                    running = False

        menus[state].draw()
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()

