from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.sky import Sky
import random

box_count = 0
body = []

app = Ursina()

class AirpersonController(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.collider = 'sphere'
        self.speed = 5
        self.origin_y = -.5
        self.camera_pivot = Entity(parent=self, y=2)
        self.hits = 0
        self.last_time = time.time()

        camera.parent = self.camera_pivot
        camera.position = (0, 0, -8)
        camera.rotation = (0, 0, 0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        global box_count
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(self.forward * (1 - held_keys['s']) + self.right * (held_keys['d'] - held_keys['a'])
                              +self.up *self.camera_pivot.rotation_x/-80* (1 - held_keys['s'])).normalized()
        origin = self.world_position

        hit_info = self.intersects()

        if hit_info.hit:
            self.hits += 1
            print_on_screen(f'hits count {self.hits}', position=(0,0.4), origin=(0,0), scale=2, duration= 2)
            destroy(hit_info.entity)
            box_count -= 1

            for i in range(4):
                follows = Entity(parent=scene, model='sphere', color=color.rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255)))
                body.append(follows)

        self.move_body()

        self.position += self.direction * self.speed * time.dt*0.5

    def move_body(self):

        if len(body)>0:
            print(self.position)
            body[0].position = self.position

        if time.time()-self.last_time>0.2:
            self.last_time=time.time()
            for i in range(len(body)-1, 0, -1):
                body[i].position = body[i-1].position




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

    def update(self):
        global box_count
        self.rotation_y += time.dt*100
        if time.time()- self.lasttime > 1:
            self.lasttime = time.time()
            self.color=color.rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))


player1 = AirpersonController(model='sphere')

sky=Sky()

"""그리드 생성"""
# r = 30
# for i in range(r):
#     grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_x=90, position=(0,i-15,0))
#     grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_z=90, position=(0,0,i-15))

def update():
    global box_count
    if box_count <200:
        box_count += 1
        box = Voxel(position = (random.randint(-15, 15), random.randint(-15, 15), random.randint(-15, 15)))


app.run()

