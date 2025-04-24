import random
import requests
import pgzrun
CELL_SIZE, MAP_SIZE = 32, 32
SCREEN_WIDTH, SCREEN_HEIGHT = CELL_SIZE * MAP_SIZE, CELL_SIZE * MAP_SIZE
FLASK_SERVER_URL = "http://127.0.0.1:5000/api/get_game_state"
class Cat:
    def __init__(self, name, x=0, y=0):
        self.name, self.x, self.y, self.target_x, self.target_y = name, x, y, x, y
        self.speed = 2
        self.sprites = {d: [f"walk_{d.lower()}{i}" for i in range(4)] for d in ["Up", "Down", "Left", "Right"]}
        self.current_direction, self.current_frame, self.frame_timer = "Down", 0, 0
    def draw(self):
        screen.blit(self.sprites[self.current_direction][self.current_frame], (self.x * CELL_SIZE, self.y * CELL_SIZE))
        screen.draw.text(self.name, (self.x * CELL_SIZE, (self.y - 1) * CELL_SIZE), color="white", fontsize=16)
    def update(self):
        self.frame_timer += 1 / 60
        if self.frame_timer >= 0.2:
            self.frame_timer, self.current_frame = 0, (self.current_frame + 1) % len(self.sprites[self.current_direction])
        if self.x < self.target_x: self.x, self.current_direction = self.x + self.speed / CELL_SIZE, "Right"
        elif self.x > self.target_x: self.x, self.current_direction = self.x - self.speed / CELL_SIZE, "Left"
        if self.y < self.target_y: self.y, self.current_direction = self.y + self.speed / CELL_SIZE, "Down"
        elif self.y > self.target_y: self.y, self.current_direction = self.y - self.speed / CELL_SIZE, "Up"
cats, coins = {}, []
def generate_new_coin_position(existing_positions):
    while True:
        new_pos = {"x": random.randint(0, MAP_SIZE - 1), "y": random.randint(0, MAP_SIZE - 1)}
        if (new_pos["x"], new_pos["y"]) not in existing_positions:
            return new_pos
def update():
    global cats, coins
    try:
        data = requests.get(FLASK_SERVER_URL, timeout=5).json()
        players, coins = data["players"], data["coins"]
        for p in players:
            name = p["name"]
            if name not in cats:
                cats[name] = Cat(name=name, x=p["cat_x"], y=p["cat_y"])
            else:
                cats[name].target_x, cats[name].target_y = p["cat_x"], p["cat_y"]
        for cat in cats.values():
            cat.update()
        occupied = [(int(cat.x), int(cat.y)) for cat in cats.values()] + [(c["x"], c["y"]) for c in coins]
        for cat in cats.values():
            for coin in coins[:]:
                if int(cat.x) == coin["x"] and int(cat.y) == coin["y"]:
                    coins.remove(coin)
                    new_coin = generate_new_coin_position(occupied)
                    coins.append(new_coin)
                    requests.post("http://127.0.0.1:5000/api/update_coins", json={"coins": coins}, timeout=5)
                    player = next((p for p in players if p["name"] == cat.name), None)
                    if player:
                        requests.post("http://127.0.0.1:5000/api/update_player", json=player, timeout=5)
    except Exception:
        pass
def draw():
    screen.clear()
    for x in range(MAP_SIZE):
        for y in range(MAP_SIZE):
            screen.draw.rect(Rect((x * CELL_SIZE, y * CELL_SIZE), (CELL_SIZE, CELL_SIZE)), "gray")
    for coin in coins:
        screen.draw.filled_rect(Rect((coin["x"] * CELL_SIZE, coin["y"] * CELL_SIZE), (CELL_SIZE, CELL_SIZE)), "yellow")
    for cat in cats.values():
        cat.draw()
WIDTH, HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
pgzrun.go()