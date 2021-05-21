from ursina import *
from ursina.mesh_importer import *
import random

#폰트지정
Text.default_font='fonts/malgun.ttf'
color.text_color=color.black

#전역변수 지정
boxs=[]
monsters=[]
box_count = 0
AREA_SIZE = 50
BUTTON_SIZE = (.25, .075)
app = Ursina()

#사운드 로드
background_music = Audio('sound/07 - Town.ogg', pitch=1, loop=True, autoplay=True)
power_up = Audio('sound/power_up_04.ogg', pitch=1, loop=True, autoplay=False)
attention = Audio('sound/attention.wav', pitch=1, loop=True, autoplay=False)

# 텍스쳐 모음
textures =[str(x+1) for x in range(12)]

#전체화면 지정
#window.fullscreen = True

#몬스터 클래스
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

#주인공 클래스
class Snake_camera(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.collider = 'box'
        self.speed = 5
        #self.origin_y = -.5
        self.camera_pivot = Entity(parent=self, y=2)
        self.hits = 0
        self.last_time = time.time()
        self.body = [Entity(parent=scene, model='kirby', collider='sphere',texture='kirby_body.png', position=(-15,-15,-15))]

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

        #자기몸과 충돌 확인
        if len(self.body)>3:
            for i in self.body[6:]:
                hit_info = self.intersects(i)
                if hit_info.hit:
                    application.pause()
                    out = Text(text='자기몸이랑 부딧혀서 죽음', color=color.red, position=(0, 0.4), origin=(0, 0),
                               scale=2, duration=2)
                    main_menu.enable()
                    mouse.locked = False

        self.move_body()

    def input(self, key):
        if key == 'w':
            self.speed += 1
        if key == 'd':
            self.speed -= 1



    def move_body(self):
        if len(self.body)>0:
            self.body[0].position = self.position
        if time.time()-self.last_time>0.2:
            self.last_time=time.time()
            for i in range(len(self.body)-1, 0, -1):
                self.body[i].position = self.body[i-1].position
        for i in self.body:
            i.rotation += Vec3(0,random.randint(5,10),0)

#피자 클래스
class Voxel(Entity):
    def __init__(self, position =(0,0,0)):
        super().__init__(
            parent = scene,
            position = position,
            model = random.choice(['sphere', 'cube']),
            texture = random.choice(['white_cube', 'brick']+textures),
            color = color.color(0,0,random.uniform(0.9,1)),
            collider = 'sphere'
        )
        self.lasttime = time.time()
        self.hits = 0

    def update(self):
        global box_count
        #회전
        self.rotation_y += time.dt*100

        #색상변경
        # if time.time()- self.lasttime > 1:
        #     self.lasttime = time.time()
        #     self.color=color.rgb(random.randint(0,255),random.randint(0,255),random.randint(0,255))

        hit_info = self.intersects(player1)
        if hit_info.hit:
            player1.hits += 1
            out = Text(text=f'피자를 먹은수: {player1.hits}', color=color.red, position=(0, 0.4), origin=(0, 0), scale=2, duration=2)
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

#메뉴 클래스
class MenuMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, ignore_paused=True)
        self.main_menu = Entity(parent=self, enabled=True)
        self.options_menu = Entity(parent=self, enabled=False)
        self.help_menu = Entity(parent=self, enabled=False)
        #self.background = Sprite('shore', color=color.dark_gray, parent=self, x=0, y=0.4, z=-1)

        Text("메뉴", parent=self.main_menu, y=0.4, x=0, origin=(0,0))

        def quit_game():
            application.quit()

        def options_menu_btn():
            self.options_menu.enable()
            self.main_menu.disable()

        def help_menu_btn():
            self.help_menu.enable()
            self.main_menu.disable()

        def restart():
            global player1
            global monsters

            for i in player1.body:
                destroy(i)
            destroy(player1)
            for monster in monsters:
                for i in monster.body:
                    destroy(i)
                del monsters[monsters.index(monster)]
                destroy(monster)
            player1 = Snake_camera(texture='kirby_body.png', model='kirby')
            application.resume()

        ButtonList(button_dict={
            "재시작": Func(restart),
            "옵션": Func(options_menu_btn),
            "도움말": Func(help_menu_btn),
            "게임 종료": Func(quit_game)
        },y=0,parent=self.main_menu, ignore_paused=True)

        # [OPTIONS MENU] WINDOW START
        Text ("OPTIONS MENU", parent=self.options_menu, y=0.4, x=0, origin=(0, 0))

        def options_back_btn_action():
            self.main_menu.enable()
            self.options_menu.disable()

        Button("Back",parent=self.options_menu,y=-0.3,scale=(0.1,0.05),color=rgb(50,50,50),
               on_click=options_back_btn_action)

        # [OPTIONS MENU] WINDOW END

        # [HELP MENU] WINDOW START
        Text ("HELP MENU", parent=self.help_menu, y=0.4, x=0, origin=(0, 0))

        def help_back_btn_action():
            self.main_menu.enable()
            self.help_menu.disable()

        ButtonList (button_dict={
            "Gameplay": Func(print_on_screen,"You clicked on Gameplay help button!", position=(0,.1), origin=(0,0)),
            "Battle": Func(print_on_screen,"You clicked on Battle help button!", position=(0,.1), origin=(0,0)),
            "Control": Func(print_on_screen,"You clicked on Control help button!", position=(0,.1), origin=(0,0)),
            "Back": Func (help_back_btn_action)
        }, y=0, parent=self.help_menu, ignore_paused=True)
        # [HELP MENU] WINDOW END

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def input(self, key):
        if self.options_menu.enabled:
            if key == "escape":
                self.main_menu.enable()
                self.options_menu.disable()

        if self.help_menu.enabled:
            if key == "escape":
                self.main_menu.enable()
                self.help_menu.disable()
        if key=='space':
            application.resume()

    def update(self):
        pass


#메뉴 생성
main_menu = MenuMenu()
main_menu.disable()
#플레이어 생성
#load_model('badboy.blend') #모델 초기 생성
#obj_to_ursinamesh(name='badboy',save_to_file=True)
player1 = Snake_camera(texture='kirby_body.png', model='kirby')


#몬스터 생성
for i in range(1):
    monsters.append(Monster(texture='badboy.png', model='badboy'))

#배경 생성
backgrounds=[str(x) for x in range(21, 34)]
sky=Sky(texture=random.choice(backgrounds))

#배경음악 재생
background_music_playing=Audio(background_music.clip, volume=2, loop=True)
"""그리드 생성"""
grids=[]
grids.append(Entity(model=Grid(AREA_SIZE,AREA_SIZE), scale=AREA_SIZE, color=color.color(0,0,0.5,0), rotation_x=90, position=(0,AREA_SIZE/2,0)))
grids.append(Entity(model=Grid(AREA_SIZE,AREA_SIZE), scale=AREA_SIZE, color=color.color(0,0,0.5,0), rotation_x=90, position=(0,-AREA_SIZE/2,0)))
grids.append(Entity(model=Grid(AREA_SIZE,AREA_SIZE), scale=AREA_SIZE, color=color.color(0,0,0.5,0), rotation_z=90, position=(0,0,AREA_SIZE/2)))
grids.append(Entity(model=Grid(AREA_SIZE,AREA_SIZE), scale=AREA_SIZE, color=color.color(0,0,0.5,0), rotation_z=90, position=(0,0,-AREA_SIZE/2)))
grids.append(Entity(model=Grid(AREA_SIZE,AREA_SIZE), scale=AREA_SIZE, color=color.color(0,0,0.5,0), rotation_y=90, position=(AREA_SIZE/2,0,0)))
grids.append(Entity(model=Grid(AREA_SIZE,AREA_SIZE), scale=AREA_SIZE, color=color.color(0,0,0.5,0), rotation_y=90, position=(-AREA_SIZE/2,0,0)))

#라이트
Light(type='pointlight', color=(1,0.4,0.4,2))
Light(type='directional', color=(0.7, 0.7, 0.7, 3), direction=(3,3,1))

#게임 루프
def update():
    global box_count

    #박스 리젠
    if box_count <AREA_SIZE**3/27000*200:
        box_count += 1
        box = Voxel(position = (random.randint(-AREA_SIZE/2, AREA_SIZE/2), random.randint(-AREA_SIZE/2, AREA_SIZE/2), random.randint(-AREA_SIZE/2, AREA_SIZE/2)))
        boxs.append(box)

    #몬스터 리젠
    if len(monsters)<20:
        monsters.append(Monster(texture='badboy.png', model='badboy'))

    #게임 아웃
    if abs(player1.position.x)>AREA_SIZE/2-2 or abs(player1.position.y)>AREA_SIZE/2-2 or  abs(player1.position.z)>AREA_SIZE/2-2:
        for grid in grids:
            grid.color=(0,0,0.5,1)
        out=Text(text='경고!! 경계를 벗어났습니다.!!', color=color.red, position=(0, 0.4), origin=(0, 0), scale=2, duration=2)
        sound=Audio(attention.clip)
    if abs(player1.position.x) > AREA_SIZE/2+2 or abs(player1.position.y) > AREA_SIZE/2+2 or abs(player1.position.z) > AREA_SIZE/2+2:
        application.pause()
        out=Text(text='경계를 벗어나서 죽음.', color=color.red, position=(0, 0.4), origin=(0, 0), scale=2, duration=2)
        main_menu.enable()
        mouse.locked = False
    if abs(player1.position.x) < AREA_SIZE/2-5 and abs(player1.position.y) < AREA_SIZE/2-5 and abs(player1.position.z) < AREA_SIZE/2-5:
        for grid in grids:
            grid.color = (0, 0, 0.5,0)

    #몬스터와 충돌 확인
    for _monster in monsters:
        for monster in _monster.body:
            hit_info=player1.body[0].intersects(monster)
            if hit_info.hit:
                application.pause()
                out = Text(text='몬스터와 부딧혀서 죽음', color=color.red, position=(0, 0.4), origin=(0, 0), scale=2, duration=2)
                main_menu.enable()
                mouse.locked = False

    #몬스터가 플레이어에 충돌 할 경우
    for monster in monsters:
        for player in player1.body:
            hit_info=monster.intersects(player)
            if hit_info.hit:
                for i in monster.body:
                    destroy(i)
                del monsters[monsters.index(monster)]
                destroy(monster)

    #몬스터가 못나가게 막음
    for monster in monsters:
        if monster.x > AREA_SIZE/2 or monster.x < -AREA_SIZE/2:
            monster.x *= -1
        if monster.y > AREA_SIZE/2 or monster.y < -AREA_SIZE/2:
            monster.y *= -1
        if monster.z > AREA_SIZE/2 or monster.z < -AREA_SIZE/2:
            monster.z *= -1

    #경계선 보이기
    if held_keys['space']:
        for grid in grids:
            grid.color=(0,0,0.5,1)


def input(key):
    #메뉴보이기
    if not mouse.locked:
        main_menu.disable()
        mouse.locked=True
    if main_menu.enabled:
        main_menu.disable()
    if key=='f10':
        application.pause()
        main_menu.enable()
        mouse.locked=False

app.run()

