import json
import os
import random
import time

LEARNING_DATA_FILE = os.path.join(os.path.dirname(__file__), 'learn_data.json')


def load_learning_data():
    if os.path.exists(LEARNING_DATA_FILE):
        with open(LEARNING_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'heuristics': {
            'collector_exploration_rate': 0.18,
            'protector_detection_range': 6,
            'enemy_random_move_prob': 0.2,
            'protector_attack_power': 2
        },
        'episodes': []
    }


def save_learning_data(data):
    with open(LEARNING_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


class Enemy:
    def __init__(self, x, y, health=5):
        self.x = x
        self.y = y
        self.health = health

    def step(self, sim):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        home_x, home_y = sim.home_x, sim.home_y
        best = None
        best_dist = None
        for dx, dy in directions:
            nx = (self.x + dx) % sim.width
            ny = (self.y + dy) % sim.height
            d = abs(nx - home_x) + abs(ny - home_y)
            if best_dist is None or d < best_dist:
                best_dist = d
                best = (nx, ny)

        if random.random() < sim.enemy_random_move_prob:
            dx, dy = random.choice(directions)
            self.x = (self.x + dx) % sim.width
            self.y = (self.y + dy) % sim.height
        else:
            self.x, self.y = best

        for ant in list(sim.ants):
            if abs(ant.x - self.x) + abs(ant.y - self.y) == 1:
                ant.health -= 1
                if ant.health <= 0:
                    try:
                        sim.ants.remove(ant)
                    except ValueError:
                        pass


class Ant:
    def __init__(self, x, y, grid_width, grid_height, role='collector'):
        self.x = x
        self.y = y
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.carrying_food = False
        self.path = []
        self.return_path = []
        self.role = role
        self.health = 3

    def move(self, pheromone_map, food_map, home_x, home_y, enemies, sim):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        neighbors = []
        for dx, dy in directions:
            nx = (self.x + dx) % self.grid_width
            ny = (self.y + dy) % self.grid_height
            neighbors.append((nx, ny))

        exploration_rate = sim.collector_exploration_rate
        pheromone_bias = 1.0

        if self.role == 'protector':
            nearest = None
            best_d = None
            for e in enemies:
                d = abs(e.x - self.x) + abs(e.y - self.y)
                if best_d is None or d < best_d:
                    best_d = d
                    nearest = e
            if nearest and best_d <= sim.protector_detection_range:
                tx, ty = nearest.x, nearest.y
                neighbors.sort(key=lambda pos: abs(pos[0] - tx) + abs(pos[1] - ty))
                next_x, next_y = neighbors[0]
            else:
                neighbors.sort(key=lambda pos: abs(pos[0] - home_x) + abs(pos[1] - home_y))
                if random.random() < exploration_rate:
                    next_x, next_y = random.choice(neighbors)
                else:
                    next_x, next_y = neighbors[0]
        else:
            self.path.append((self.x, self.y))
            if len(self.path) > 200:
                self.path.pop(0)
            if random.random() < exploration_rate:
                next_x, next_y = random.choice(neighbors)
            else:
                weights = []
                for nx, ny in neighbors:
                    weights.append(pheromone_bias + pheromone_map[ny][nx])
                total = sum(weights)
                if total <= 0:
                    next_x, next_y = random.choice(neighbors)
                else:
                    r = random.random() * total
                    upto = 0
                    chosen = neighbors[0]
                    for w, pos in zip(weights, neighbors):
                        upto += w
                        if r <= upto:
                            chosen = pos
                            break
                    next_x, next_y = chosen

        if self.role != 'protector' and not self.carrying_food and food_map[self.y][self.x] > 0:
            self.carrying_food = True
            food_map[self.y][self.x] -= 1
            self.return_path = list(reversed(self.path))
            if self.return_path and self.return_path[0] == (self.x, self.y):
                self.return_path.pop(0)
            self.path = []
            print(f"Ant found food at ({self.x}, {self.y})")

        if self.carrying_food and self.return_path:
            next_pos = self.return_path.pop(0)
            next_x, next_y = next_pos

        if self.carrying_food and self.x == home_x and self.y == home_y:
            self.carrying_food = False
            self.return_path = []
            print(f"Ant returned home with food at ({self.x}, {self.y})")

        self.x = next_x
        self.y = next_y

        deposit = 2 if self.carrying_food else 1
        pheromone_map[self.y][self.x] += deposit


class AntSimulation:
    def __init__(self, width=20, height=10, num_ants=10, food_sources=3):
        self.width = width
        self.height = height
        self.num_ants = num_ants
        self.ants = []
        self.enemies = []
        self.pheromone_map = [[0 for _ in range(width)] for _ in range(height)]
        self.food_map = [[0 for _ in range(width)] for _ in range(height)]
        self.home_x = width // 2
        self.home_y = height // 2
        self.home_health = 10
        self.steps = 0
        self.learning_data = load_learning_data()
        self.collector_exploration_rate = self.learning_data['heuristics'].get('collector_exploration_rate', 0.18)
        self.protector_detection_range = self.learning_data['heuristics'].get('protector_detection_range', 6)
        self.enemy_random_move_prob = self.learning_data['heuristics'].get('enemy_random_move_prob', 0.2)
        self.protector_attack_power = self.learning_data['heuristics'].get('protector_attack_power', 2)
        self._place_ants()
        self._place_food(food_sources)

    def _place_ants(self):
        num_protectors = max(1, int(self.num_ants * 0.3))
        for i in range(self.num_ants):
            role = 'protector' if i < num_protectors else 'collector'
            ant = Ant(self.home_x, self.home_y, self.width, self.height, role=role)
            self.ants.append(ant)

    def _place_food(self, food_sources):
        for _ in range(food_sources):
            x = random.randrange(self.width)
            y = random.randrange(self.height)
            if (x, y) == (self.home_x, self.home_y):
                continue
            self.food_map[y][x] += random.randint(1, 3)

    def spawn_enemy(self, x=None, y=None, health=5):
        if x is None:
            x = random.randrange(self.width)
        if y is None:
            y = random.randrange(self.height)
        if (x, y) == (self.home_x, self.home_y):
            return
        self.enemies.append(Enemy(x, y, health))

    def evaporate_pheromones(self, rate=0.05):
        for y in range(self.height):
            for x in range(self.width):
                self.pheromone_map[y][x] *= (1 - rate)
                if self.pheromone_map[y][x] < 0.01:
                    self.pheromone_map[y][x] = 0

    def update_learning_heuristics(self):
        episodes = self.learning_data.get('episodes', [])
        if not episodes:
            return
        last = episodes[-1]
        if last.get('home_health', 0) >= 9:
            self.collector_exploration_rate = max(0.05, self.collector_exploration_rate - 0.01)
        else:
            self.collector_exploration_rate = min(0.4, self.collector_exploration_rate + 0.01)
        self.learning_data['heuristics']['collector_exploration_rate'] = self.collector_exploration_rate
        save_learning_data(self.learning_data)

    def record_episode(self):
        food_collected = sum(1 for ant in self.ants if ant.carrying_food)
        self.learning_data.setdefault('episodes', []).append({
            'home_health': self.home_health,
            'food_collected': food_collected,
            'enemies_defeated': 0,
            'steps': self.steps,
            'success': self.home_health > 0
        })
        if len(self.learning_data['episodes']) > 20:
            self.learning_data['episodes'].pop(0)
        save_learning_data(self.learning_data)

    def step(self):
        self.steps += 1
        for ant in list(self.ants):
            ant.move(self.pheromone_map, self.food_map, self.home_x, self.home_y, self.enemies, self)

        for ant in list(self.ants):
            if ant.role == 'protector':
                for e in list(self.enemies):
                    if e.x == ant.x and e.y == ant.y:
                        e.health -= self.protector_attack_power
                        print(f"Protector ant attacked enemy at ({e.x}, {e.y}); enemy hp={e.health}")
                        if e.health <= 0:
                            try:
                                self.enemies.remove(e)
                            except ValueError:
                                pass

        for e in list(self.enemies):
            e.step(self)
            if (e.x, e.y) == (self.home_x, self.home_y):
                self.home_health -= 1
                print(f"Enemy attacked the nest! Home health: {self.home_health}")
                if self.home_health <= 0:
                    print("The nest has been destroyed!")

        self.evaporate_pheromones()
        if self.steps % 50 == 0:
            self.record_episode()
            self.update_learning_heuristics()

    def render(self):
        symbol_map = [["." for _ in range(self.width)] for _ in range(self.height)]
        symbol_map[self.home_y][self.home_x] = "H"
        for y in range(self.height):
            for x in range(self.width):
                if self.food_map[y][x] > 0:
                    symbol_map[y][x] = "F"
        for e in self.enemies:
            symbol_map[e.y][e.x] = "E"
        for ant in self.ants:
            symbol_map[ant.y][ant.x] = "P" if ant.role == 'protector' else "A"
        print(f"Step {self.steps}  HomeHP={self.home_health}")
        for row in symbol_map:
            print("".join(row))
        print("Pheromone levels: ")
        for row in self.pheromone_map:
            print("".join(f"{int(val):2d}" for val in row))
        print("\n")


def main():
    simulation = AntSimulation(width=20, height=10, num_ants=5, food_sources=4)
    for _ in range(50):
        simulation.step()
        simulation.render()
        time.sleep(0.15)


if __name__ == '__main__':
    main()
