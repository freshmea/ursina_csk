from ursina import *
from ursina.mesh_importer import *
from ursina.prefabs.health_bar import *
import random

#폰트지정
Text.default_font='fonts/malgun.ttf'
color.text_color=color.black

#전역변수 지정
boxs=[]
monsters=[]
box_count = 0
AREA_SIZE = 30
BUTTON_SIZE = (.25, .075)
app = Ursina()
MAX_COUNT = 30
monster_hits = 0
grid_clear = True

#사운드 로드
background_music = Audio('sound/07 - Town.ogg', pitch=1, loop=True, autoplay=True, loops=-1)
power_up = Audio('sound/power_up_04.ogg', pitch=1, loop=True, autoplay=False)
attention = Audio('sound/attention.wav', pitch=1, loop=True, autoplay=False)

# 텍스쳐 모음

#전체화면 지정
window.fullscreen = True

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
class Player_kirby(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.collider = 'box'
        self.speed = 5
        #self.origin_y = -.5
        self.camera_pivot = Entity(parent=self, y=2)
        self.hits = 0
        self.last_time = time.time()
        self.body = [Entity(parent=scene, model='sphere', collider='sphere', position=(-15,-15,-15), color=color.rgb(255, 91, 173), scale=0.7)]

        camera.parent = self.camera_pivot
        camera.position = (0, 0, -8)
        camera.rotation = (0, 0, 0)
        camera.fov = 90
        mouse.locked = True
        self.mouse_sensitivity = Vec2(40, 40)
        DirectionalLight(parent=self, color=(1, 1, 1, 100), rotation_x=45)
        SpotLight(parent=self, color=(1, 1, 1, 1), rotation_x=0)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        self.rotation_y += mouse.velocity[0] * self.mouse_sensitivity[1]
        self.rotation_y += 5*(held_keys['d'] - held_keys['a'])
        self.camera_pivot.rotation_x += 5*(held_keys['s'] - held_keys['w'])

        self.camera_pivot.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity[0]
        self.camera_pivot.rotation_x = clamp(self.camera_pivot.rotation_x, -90, 90)

        self.direction = Vec3(self.forward + self.up *self.camera_pivot.rotation_x/-80).normalized()
        origin = self.world_position
        self.position += self.direction * self.speed * time.dt*0.5

        #자기몸과 충돌 확인
        if len(self.body)>3:
            for i in self.body[6:]:
                hit_info = self.intersects(i)
                if hit_info.hit:
                    application.pause()
                    out = Text(text='자기몸이랑 부딪혀서 죽음', color=color.red, position=(0, 0.4), origin=(0, 0),
                               scale=2)
                    destroy(out, delay=2)
                    main_menu.enable()
                    mouse.locked = False

        self.move_body()

    def input(self, key):
        pass



    def move_body(self):
        if len(self.body)>0:
            self.body[0].position = self.position
        if time.time()-self.last_time>0.2:
            self.last_time=time.time()
            for i in range(len(self.body)-1, 0, -1):
                self.body[i].position = self.body[i-1].position

#피자 클래스
class Voxel(Entity):
    def __init__(self, position =(0,0,0)):
        super().__init__(
            parent = scene,
            position = position,
            model = random.choice(['pizza']), scale=0.01,
            texture = 'pizza',
            color = color.color(0,0,random.uniform(0.9,1)),
            collider = 'box'
        )
        self.lasttime = time.time()
        self.hits = 0

    def update(self):
        global box_count
        global monster_hits
        #회전
        self.rotation_y += time.dt*100

        hit_info = self.intersects(player1)
        if hit_info.hit:
            player1.hits += 1
            ui.health_bar_1.value = player1.hits
            ui.health_bar_1_kirby.x += 0.018
            box_count -= 1
            sound = Audio(power_up.clip, volume=0.1)
            for i in range(4):
                follows = Entity(parent=scene, model='sphere', collider='sphere', position=(-15,-15,-15), color=color.rgb(255, 91, 173), scale=0.7)
                follows.set_render_mode_wireframe(True)
                player1.body.append(follows)
            del boxs[boxs.index(self)]
            destroy(self)

        for monster in monsters:
            hit_info = self.intersects(monster)
            if hit_info.hit:
                monster.turn= True
                monster_hits += 1
                ui.health_bar_2.value = monster_hits
                ui.health_bar_2_bad.x -= 0.0018
                box_count -= 1
                for i in range(4):
                    #follows = Entity(parent=scene, model='badboy', collider='box',texture='badboy.png'
                    #                ,position=(-15,-15,-15), rotation=monster.rotation)
                    follows = Entity(parent=scene, model='sphere', collider='sphere',color=color.light_gray.tint(-0.5),
                                     position=(-15, -15, -15), scale=0.8)
                    follows.set_render_mode_wireframe(True)
                    monster.body.append(follows)
                del boxs[boxs.index(self)]
                destroy(self)

#메뉴 클래스
class MenuMenu(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=camera.ui, ignore_paused=True)
        self.main_menu = Entity(parent=self, enabled=True)
        self.options_menu = Entity(parent=self, enabled=False)
        #self.background = Sprite('shore', color=color.dark_gray, parent=self, x=0, y=0.4, z=-1)

        Text("메뉴", parent=self.main_menu, y=0.4, x=0, origin=(0,0), color=color.red)

        def quit_game():
            application.quit()

        def options_menu_btn():
            self.options_menu.enable()
            self.main_menu.disable()

        def grid_btn():
            global grid_clear
            grid_clear = not grid_clear

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
            player1 = Player_kirby(texture='kirby_body.png', model='kirby')
            application.resume()

        ButtonList(button_dict={
            "재시작": Func(restart),
            "옵션": Func(options_menu_btn),
            "경계 보기": Func(grid_btn),
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

        for key, value in kwargs.items ():
            setattr (self, key, value)

    def input(self, key):
        if self.options_menu.enabled:
            if key == "escape":
                self.main_menu.enable()
                self.options_menu.disable()

        if key=='space':
            application.resume()

    def update(self):
        pass

#유저 인터페이스 클래스
class UI(Entity):
    def __init__(self):
        super().__init__(parent=camera.ui, ignore_paused=True)
        self.score = 0
        self.frame = Entity(parent=self, ignore_pauded=True, )

        frame1=Entity(model='quad', parent = self, color=color.color(0, 0, 0, 1), scale=(2,0.01), position=(0,0.49))
        frame2=Entity(model='quad', parent = self, color=color.color(0, 0, 0, 1), scale=(2,0.01), position=(0,-0.49))
        frame3=Entity(model='quad', parent = self, color=color.color(0, 0, 0, 1), scale=(0.01,1), position=(0.88,0))
        frame4=Entity(model='quad', parent = self, color=color.color(0, 0, 0, 1), scale=(0.01,1), position=(-0.88,0))
        self.health_bar_1_text=Text(text=f'피자 먹은수 {player1.hits}/30', position=(-0.85, 0.47), color=color.blue)
        self.health_bar_1_kirby = Entity(parent=self, model='kirby', texture='kirby_body.png',
                                         position=((-.44 * window.aspect_ratio, .45)), scale=0.05, rotation_y=180)
        self.health_bar_1 = HealthBar(parent = self, bar_color=color.pink.tint(-.25), roundness=.5, max_value=MAX_COUNT)
        self.health_bar_1.value=0
        self.health_bar_2_bad = Entity(parent=self, model='badboy', texture='badboy.png',
                                         position=((.1 * window.aspect_ratio, .445)), scale=0.05)
        self.health_bar_2 = HealthBar(parent = self, bar_color=color.lime.tint(-.25), roundness=.5, max_value=300, position = (.1 * window.aspect_ratio, .425), rotation_z=180)
        self.health_bar_2.value=0

    def update(self):
        global monster_hits
        destroy(self.health_bar_1_text)
        self.health_bar_1_text=Text(text=f'피자 먹은수 {player1.hits}/30            몬스터의 갯수{len(monsters)}       몬스터가 먹은 피자수{monster_hits}/300', position=(-0.85, 0.47), color=color.blue)
        self.health_bar_2_bad.rotation_y += 5
        self.health_bar_1_kirby.rotation_y += 5


#메뉴 생성
main_menu = MenuMenu()
main_menu.disable()



#플레이어 생성
#load_model('pizza.blend') #모델 초기 생성
#obj_to_ursinamesh(name='badboy',save_to_file=True)
player1 = Player_kirby(texture='kirby_body.png', model='kirby')

#UI 생성
ui = UI()

#몬스터 생성
for i in range(20):
    monsters.append(Monster(texture='badboy.png', model='badboy', scale=1.5))

#배경 생성
backgrounds=[str(x) for x in range(21, 33)]
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



#게임 루프
def update():
    global box_count
    global grid_clear
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
        out=Text(text='경고!! 경계를 벗어났습니다.!!', color=color.red, position=(0, 0.4), origin=(0, 0), scale=2)
        destroy(out, delay=2)
        sound=Audio(attention.clip)
    if abs(player1.position.x) > AREA_SIZE/2+2 or abs(player1.position.y) > AREA_SIZE/2+2 or abs(player1.position.z) > AREA_SIZE/2+2:
        application.pause()
        out=Text(text='경계를 벗어나서 죽음.', color=color.red, position=(0, 0.4), origin=(0, 0), scale=2)
        destroy(out, delay=2)
        main_menu.enable()
        mouse.locked = False

    #그리드 지우기
    if abs(player1.position.x) < AREA_SIZE/2-5 and abs(player1.position.y) < AREA_SIZE/2-5 and abs(player1.position.z) < AREA_SIZE/2-5 and grid_clear:
        for grid in grids:
            grid.color = (0, 0, 0.5,0)

    #몬스터와 충돌 확인
    for _monster in monsters:
        for monster in _monster.body:
            hit_info=player1.body[0].intersects(monster)
            if hit_info.hit:
                application.pause()
                out=Text(text='몬스터와 부딪혀서 죽음', color=color.red, position=(0, 0.4), origin=(0, 0), scale=2)
                destroy(out, delay=2)
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

    #피자를 30개 먹으면 게임 종료
    if player1.hits > MAX_COUNT-1:
        application.pause()
        out = Text(text='성공!! 게임을 클리어 했어요!', color=color.red, position=(0, 0.2), origin=(0, 0), scale=5)
        destroy(out, delay=6)
        main_menu.enable()
        mouse.locked = False

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
        mouse.locked=True
    if main_menu.enabled:
        main_menu.disable()
    if key=='f1':
        application.pause()
        main_menu.enable()
        mouse.locked=False

app.run()

