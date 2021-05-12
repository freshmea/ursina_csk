from ursina import *
from ursina.prefabs.sky import Sky
from ursina.mesh_importer import *
import random

#폰트지정
Text.default_font='fonts/malgun.ttf'
color.text_color=color.black

#전역변수 지정
boxs=[]
monsters=[]
box_count = 0

app = Ursina()
#사운드 로드
background_music = Audio('sound/07 - Town.ogg', pitch=1, loop=True, autoplay=True)
power_up = Audio('sound/power_up_04.ogg', pitch=1, loop=True, autoplay=False)
attention = Audio('sound/attention.wav', pitch=1, loop=True, autoplay=False)


#window.fullscreen = True
class Monster(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.collider = 'box'
        self.speed = 4
        self.last_time = time.time()
        self.turn_time = time.time()
        self.body = []
        self.hits = 0
        self.position=Vec3(10,10,10)
        self.rotation=Vec3.zero()
        self.direction = Vec3(0, 0, 0)
        self.turn = True

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        if time.time() - self.turn_time > 3:
            self.turn_time=time.time()
            self.turn= True

        if len(boxs)>100 and self.turn:
            box_temp=boxs[random.randint(0,100)]
            self.direction = Vec3(box_temp.position-self.position).normalized()
            self.look_at(box_temp, axis='left')
            self.turn = False
        self.position += self.direction * self.speed * time.dt * 1

        self.move_body()

    def move_body(self):
        """몸체이동"""
        if len(self.body) > 0:
            self.body[0].position = self.position
            self.body[0].rotation = self.rotation
        if time.time() - self.last_time > 0.2:
            self.last_time = time.time()
            for i in range(len(self.body) - 1, 0, -1):
                self.body[i].position = self.body[i - 1].position
                self.body[i].rotation = self.body[i-1].rotation

class Snake_camera(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.collider = 'box'
        self.speed = 5
        #self.origin_y = -.5
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
                    application.pause()

        self.move_body()

    def move_body(self):
        if len(self.body)>0:
            self.body[0].position = self.position
        if time.time()-self.last_time>0.2:
            self.last_time=time.time()
            for i in range(len(self.body)-1, 0, -1):
                self.body[i].position = self.body[i-1].position
        for i in self.body:
            i.rotation += Vec3(0,random.randint(5,10),0)


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
            print_on_screen(f'피자를 먹은수: {player1.hits}', position=(0,0.4), origin=(0,0), scale=2, duration= 2)
            box_count -= 1
            sound = Audio(power_up.clip, volume=0.1)
            for i in range(4):
                follows = Entity(parent=scene, model='kirby', collider='sphere',texture='kirby_body.png', position=(-15,-15,-15))
                player1.body.append(follows)
            del boxs[boxs.index(self)]
            destroy(self)

        for monster in monsters:
            hit_info = self.intersects(monster)
            if hit_info.hit:
                monster.turn= True
                box_count -= 1
                for i in range(4):
                    follows = Entity(parent=scene, model='badboy', collider='box',texture='badboy.png'
                                    ,position=(-15,-15,-15), rotation=monster.rotation)
                    monster.body.append(follows)
                del boxs[boxs.index(self)]
                destroy(self)


#플레이어 생성
#load_model('badboy.blend') #모델 초기 생성
#obj_to_ursinamesh(name='badboy',save_to_file=True)
player1 = Snake_camera(texture='kirby_body.png', model='kirby', scale=2 )

#몬스터 생성
for i in range(20):
    monsters.append(Monster(texture='badboy.png', model='badboy'))

#배경 생성
sky=Sky()
#배경음악 재생
background_music_playing=Audio(background_music.clip, volume=2)
"""그리드 생성"""
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_x=90, position=(0,15,0))
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_x=90, position=(0,-15,0))
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_z=90, position=(0,0,15))
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_z=90, position=(0,0,-15))
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_y=90, position=(15,0,0))
grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_y=90, position=(-15,0,0))

#라이트
Light(type='pointlight', color=(1,0.4,0.4,2))
Light(type='directional', color=(0.7, 0.7, 0.7, 3), direction=(3,3,1))

def update():
    global box_count
    if box_count <200:
        box_count += 1
        box = Voxel(position = (random.randint(-15, 15), random.randint(-15, 15), random.randint(-15, 15)))
        boxs.append(box)

    #게임 아웃
    if abs(player1.position.x)>15 or abs(player1.position.y)>15 or  abs(player1.position.z)>15:
        out=Text(text='경고!! 경계를 벗어났습니다.!!', color=color.rgb(0,0,0), position=(0, 0.4), origin=(0, 0), scale=2, duration=2)
        sound=Audio(attention.clip)
    if abs(player1.position.x) > 16 or abs(player1.position.y) > 16 or abs(player1.position.z) > 16:
        application.pause()

    #몬스터와 충돌 확인
    for _monster in monsters:
        for monster in _monster.body:
            hit_info=player1.intersects(monster)
            if hit_info.hit:
                print(monster)
                application.pause()

    #몬스터가 플레이어에 충돌 할 경우
    for monster in monsters:
        for player in player1.body:
            hit_info=monster.intersects(player)
            if hit_info.hit:
                for i in monster.body:
                    destroy(i)
                del monsters[monsters.index(monster)]
                destroy(monster)
                #monsters.append(Monster(texture='badboy.png', model='badboy'))

    #몬스터가 못나가게 막음
    for monster in monsters:
        if monster.x > 15 or monster.x < -15:
            monster.x *= -1
        if monster.y > 15 or monster.y < -15:
            monster.y *= -1
        if monster.z > 15 or monster.z < -15:
            monster.z *= -1



app.run()

