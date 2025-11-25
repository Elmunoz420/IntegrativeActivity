import random

# ============================================
# Basic structures
# ============================================

class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Box:
    def __init__(self, bid, pos):
        self.id = bid
        self.pos = pos  # Vector2 or (-1,-1) if carried


class BoxStack:
    def __init__(self):
        self.boxes = []

    def height(self):
        return len(self.boxes)

    def can_add(self):
        return len(self.boxes) < 5

    def add_box(self, box):
        self.boxes.append(box)

    def remove_box(self):
        if not self.boxes:
            return None
        return self.boxes.pop()


class Cell:
    def __init__(self, x, y, cell_type="EMPTY"):
        self.pos = Vector2(x, y)
        self.type = cell_type  # EMPTY, WALL, DROP
        self.robot = None
        self.stack = None  # BoxStack or None

    def is_free(self):
        # CAMBIO 1: solo el robot bloquea el paso, las cajas no
        return self.robot is None


# ============================================
# Robot Agent
# ============================================

class Robot:
    def __init__(self, rid, x, y, zoneXS, zoneXE):
        self.id = rid
        self.pos = Vector2(x, y)
        self.zone_start = zoneXS
        self.zone_end = zoneXE

        self.carrying = False
        self.carried_box = None

        # intended action
        self.action = ("WAIT", 0, 0)  # type, dx, dy

    def perceive(self, env):
        # return list of 4 neighbors
        neigh = []
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for dx, dy in dirs:
            nx = self.pos.x + dx
            ny = self.pos.y + dy
            if env.in_bounds(nx, ny):
                neigh.append(env.grid[ny][nx])
            else:
                neigh.append(None)
        return neigh

    def select_action(self, env):
        neighbors = self.perceive(env)

        # If carrying a box -> go to drop zone
        if self.carrying:
            c = env.grid[self.pos.y][self.pos.x]
            # si estoy en DROP y hay espacio, suelto
            if c.type == "DROP":
                if c.stack is None or c.stack.can_add():
                    self.action = ("DROP", 0, 0)
                    return

            # Move toward nearest drop cell with capacity
            target = env.nearest_drop(self.pos)
            dx = 0 if target.x == self.pos.x else (-1 if target.x < self.pos.x else 1)
            dy = 0 if target.y == self.pos.y else (-1 if target.y < self.pos.y else 1)
            self.action = ("MOVE", dx, dy)
            return

        # If NOT carrying → look for adjacent boxes
        dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        for i, cell in enumerate(neighbors):
            if cell and cell.stack and cell.type != "DROP":
                if cell.stack.height() > 0:
                    dx, dy = dirs[i]
                    self.action = ("PICK", dx, dy)
                    return

        # If none adjacent, search box in zone
        target = env.nearest_box(self)

        if target is None:
            self.action = ("WAIT", 0, 0)
            return

        dx = 0 if target.x == self.pos.x else (-1 if target.x < self.pos.x else 1)
        dy = 0 if target.y == self.pos.y else (-1 if target.y < self.pos.y else 1)
        self.action = ("MOVE", dx, dy)

    def change_decision(self):
        dirs = [(0,1),(0,-1),(1,0),(-1,0)]
        dx, dy = random.choice(dirs)
        self.action = ("MOVE", dx, dy)


    def execute(self, env):
        t, dx, dy = self.action

        # MOVE
        if t == "MOVE":
            nx = self.pos.x + dx
            ny = self.pos.y + dy
            if env.in_bounds(nx, ny):
                target = env.grid[ny][nx]
                if target.is_free():
                    # move robot
                    env.grid[self.pos.y][self.pos.x].robot = None
                    target.robot = self
                    self.pos = Vector2(nx, ny)
                    env.total_moves += 1

        # PICK
        elif t == "PICK":
            nx = self.pos.x + dx
            ny = self.pos.y + dy
            if env.in_bounds(nx, ny):
                cell = env.grid[ny][nx]
                if cell.stack and not self.carrying:
                    box = cell.stack.remove_box()
                    if box:
                        self.carrying = True
                        self.carried_box = box
                        # caja marcada como "en el aire"
                        box.pos = Vector2(-1, -1)
                        if cell.stack.height() == 0:
                            cell.stack = None

        # DROP
        elif t == "DROP":
            if self.carrying:
                cell = env.grid[self.pos.y][self.pos.x]
                if cell.type == "DROP":
                    if cell.stack is None:
                        cell.stack = BoxStack()
                    if cell.stack.can_add():
                        cell.stack.add_box(self.carried_box)
                        # ahora sí actualizamos la posición real de la caja
                        self.carried_box.pos = Vector2(self.pos.x, self.pos.y)
                        self.carrying = False
                        self.carried_box = None

        self.action = ("WAIT", 0, 0)


# ============================================
# WAREHOUSE environment
# ============================================

class Warehouse:
    def __init__(self, W, H, K):
        self.W = W
        self.H = H
        self.K = K

        self.drop_row = 0
        self.grid = []
        self.boxes = []
        self.robots = []

        self.time = 0
        self.total_moves = 0

    def in_bounds(self, x, y):
        return 0 <= x < self.W and 0 <= y < self.H

    def init(self):
        # create grid
        self.grid = [[Cell(x, y, "DROP" if y == self.drop_row else "EMPTY")
                      for x in range(self.W)] for y in range(self.H)]

        # place boxes
        for i in range(self.K):
            while True:
                x = random.randint(0, self.W - 1)
                y = random.randint(1, self.H - 1)
                c = self.grid[y][x]
                if c.is_free():
                    break
            b = Box(i, Vector2(x, y))
            self.boxes.append(b)
            c.stack = BoxStack()
            c.stack.add_box(b)

        # place robots
        zone = self.W // 5
        for i in range(5):
            while True:
                x = random.randint(0, self.W - 1)
                y = random.randint(0, self.H - 1)
                if self.grid[y][x].is_free():
                    break
            r = Robot(i, x, y, i * zone, (i + 1) * zone - 1)
            self.grid[y][x].robot = r
            self.robots.append(r)

    def nearest_box(self, robot):
        best = None
        bestdist = 1e9
        for b in self.boxes:
            # 1) ignorar cajas ya en la fila DROP
            if b.pos.y == self.drop_row:
                continue
            # 2) ignorar cajas que están siendo cargadas (-1,-1)
            if b.pos.x < 0 or b.pos.y < 0:
                continue
            # 3) respetar la zona del robot
            if not (robot.zone_start <= b.pos.x <= robot.zone_end):
                continue

            dist = abs(b.pos.x - robot.pos.x) + abs(b.pos.y - robot.pos.y)
            if dist < bestdist:
                bestdist = dist
                best = b.pos
        return best

    def nearest_drop(self, pos):
        # Buscar primero drops con espacio (<5 cajas)
        best = None
        bestdist = 1e9
        for x in range(self.W):
            cell = self.grid[self.drop_row][x]
            if cell.stack is not None and not cell.stack.can_add():
                continue  # stack lleno, no sirve
            d = abs(x - pos.x) + abs(self.drop_row - pos.y)
            if d < bestdist:
                bestdist = d
                best = Vector2(x, self.drop_row)

        if best is not None:
            return best

        # Si todos están llenos, ir al más cercano de todos modos
        best = None
        bestdist = 1e9
        for x in range(self.W):
            d = abs(x - pos.x) + abs(self.drop_row - pos.y)
            if d < bestdist:
                bestdist = d
                best = Vector2(x, self.drop_row)
        return best

    def detect_conflicts(self):
        conflicts = []

        targets = {}
        robots_moving = {}

        # collect intentions
        for i, r in enumerate(self.robots):
            t, dx, dy = r.action
            if t == "MOVE":
                nx = r.pos.x + dx
                ny = r.pos.y + dy
                if self.in_bounds(nx, ny):
                    robots_moving[i] = (nx, ny)
                    if (nx, ny) not in targets:
                        targets[(nx, ny)] = []
                    targets[(nx, ny)].append(i)

        # same-cell
        for pos, lst in targets.items():
            if len(lst) > 1:
                conflicts.append(lst)

        # swap
        rM = robots_moving
        for i in rM:
            for j in rM:
                if i < j:
                    if rM[i] == (self.robots[j].pos.x, self.robots[j].pos.y) and \
                       rM[j] == (self.robots[i].pos.x, self.robots[i].pos.y):
                        conflicts.append([i, j])

        return conflicts

    def resolve_conflicts(self, conflicts):
        for group in conflicts:
            for idx in group:
                self.robots[idx].change_decision()

    def step(self):
        self.time += 1

        for r in self.robots:
            r.select_action(self)

        conflicts = self.detect_conflicts()
        if conflicts:
            self.resolve_conflicts(conflicts)

        for r in self.robots:
            r.execute(self)

    def all_organized(self):
        for b in self.boxes:
            if b.pos.y != self.drop_row:
                return False
        return True

    def run(self, max_steps=3000):
        while self.time < max_steps and not self.all_organized():
            self.step()

        print("Steps:", self.time)
        print("Moves:", self.total_moves)
        print("Organized:", self.all_organized())


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    sim = Warehouse(20, 10, 30)
    sim.init()
    sim.run(3000)
