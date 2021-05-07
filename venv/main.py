from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.sky import Sky
import random

#전역변수 지정
boxs=[]
monsters=[]
box_count = 0

app = Ursina()

class Monster(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.collider = 'sphere'
        self.speed = 4
        self.last_time = time.time()
        self.turn_time = time.time()
        self.body = []
        self.hits = 0
        self.position=(0,0,0)
        self.direction = Vec3(10, 10, 10)
        self.turn = True
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        if time.time() - self.turn_time > 3:
            self.turn_time=time.time()
            self.turn= True

        if len(boxs)>100 and self.turn:
            try:
                self.direction = Vec3(boxs[random.randint(0,100)].position-self.position).normalized()
                self.turn = False
            except:
                self.turn = True

        self.position += self.direction * self.speed * time.dt * 1

        self.move_body()

    def move_body(self):
        """몸체이동"""
        if len(self.body) > 0:
            self.body[0].position = self.position
        if time.time() - self.last_time > 0.2:
            self.last_time = time.time()
            for i in range(len(self.body) - 1, 0, -1):
                self.body[i].position = self.body[i - 1].position

class AirpersonController(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.collider = 'sphere'
        self.speed = 5
        self.origin_y = -.5
        self.camera_pivot = Entity(parent=self, y=2)
        self.hits = 0
        self.last_time = time.time()
        self.body = []

        camera.parent = self.camera_pivot
        camera.position = (0, 0, -8)
        camera.rotation = (0, 0, 0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(self.forward * (1 - held_keys['s']) + self.right * (held_keys['d'] - held_keys['a'])
                              +self.up *self.camera_pivot.rotation_x/-80* (1 - held_keys['s'])).normalized()
        origin = self.world_position
        self.position += self.direction * self.speed * time.dt*0.5
        if len(self.body)>3:
            for i in self.body[6:]:
                hit_info = self.intersects(i)
                if hit_info.hit:
                    exit()

        self.move_body()

    def move_body(self):
        if len(self.body)>0:
            self.body[0].position = self.position
        if time.time()-self.last_time>0.2:
            self.last_time=time.time()
            for i in range(len(self.body)-1, 0, -1):
                self.body[i].position = self.body[i-1].position

class Voxel(Entity):
    def __init__(self, position =(0,0,0)):
        super().__init__(
            parent = scene,
            position = position,
            model = 'cube',
            texture = 'white_cube',
            color = color.color(0,0,random.uniform(0.9,1)),
            collider = 'box'
        )
        self.lasttime = time.time()
        self.hits = 0

    def update(self):
        global box_count
        #회전
        #self.rotation_y += time.dt*100

        #색상변경
        # if time.time()- self.lasttime > 1:
        #     self.lasttime = time.time()
        #     self.color=color.rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))


        hit_info = self.intersects(player1)
        if hit_info.hit:
            player1.hits += 1
            print_on_screen(f'hits count {player1.hits}', position=(0,0.4), origin=(0,0), scale=2, duration= 2)
            box_count -= 1
            for i in range(4):
                follows = Entity(parent=scene, model='sphere', collider='sphere',
                                 color=color.rgb(random.randint(0, 255), random.randint(0, 255),
                                                 random.randint(0, 255)), position=(-15,-15,-15))
                player1.body.append(follows)
            del boxs[boxs.index(self)]
            destroy(self)

        for monster in monsters:
            hit_info = self.intersects(monster)
            if hit_info.hit:
                monster.turn= True
                box_count -= 1
                for i in range(4):
                    follows = Entity(parent=scene, model='sphere', collider='sphere',
                                    texture='reflection_map_3',position=(-15,-15,-15))
                    monster.body.append(follows)
                del boxs[boxs.index(self)]
                destroy(self)


#플레이어 생성
player1 = AirpersonController(model='sphere', texture='reflection_map_3')

#몬스터 생성
for i in range(20):
    monsters.append(Monster(model='sphere', texture='circle_outlined', color=color.red))

#배경 생성
sky=Sky()

"""그리드 생성"""
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_x=90, position=(0,15,0))
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_x=90, position=(0,-15,0))
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_z=90, position=(0,0,15))
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_z=90, position=(0,0,-15))
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_y=90, position=(15,0,0))
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_y=90, position=(-15,0,0))

def update():
    global box_count
    if box_count <200:
        box_count += 1
        box = Voxel(position = (random.randint(-15, 15), random.randint(-15, 15), random.randint(-15, 15)))
        boxs.append(box)

    #게임 아웃
    if abs(player1.position.x)>15 or abs(player1.position.y)>15 or  abs(player1.position.z)>15:
        print_on_screen(f'out!!! out!! out!', position=(0, 0.4), origin=(0, 0), scale=2, duration=2)
    if abs(player1.position.x) > 16 or abs(player1.position.y) > 16 or abs(player1.position.z) > 16:
        exit()

    #몬스터가 못나가게 막음
    for monster in monsters:
        if monster.hits>10:
            if monster.x > 15 or monster.x < -15:
                monster.x *= -1
            if monster.y > 15 or monster.y < -15:
                monster.y *= -1
            if monster.z > 15 or monster.z < -15:
                monster.z *= -1



app.run()

