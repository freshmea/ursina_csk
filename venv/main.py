from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.sky import Sky


app = Ursina()

class AirpersonController(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.speed = 5
        self.origin_y = -.5
        self.camera_pivot = Entity(parent=self, y=2)
        self.cursor = Entity(parent=camera.ui, model='quad', color=color.pink, scale=.008, rotation_z=45)

        camera.parent = self.camera_pivot
        camera.position = (0, 0, 0)
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

        self.direction = Vec3(self.forward * (held_keys['w'] - held_keys['s']) + self.right * (held_keys['d'] - held_keys['a'])
                              +self.up *self.camera_pivot.rotation_x/-80* (held_keys['w'] - held_keys['s'])).normalized()
        origin = self.world_position # + (self.up * .5)

        hit_info = raycast(origin, self.direction, ignore=(self,), distance=.5, debug=False)
        if not hit_info.hit:
            self.position += self.direction * self.speed * time.dt






player1 = AirpersonController()
sky=Sky()
r = 30
for i in range(r):
    grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_x=90, position=(0,i-15,0))
    grid = Entity(model=Grid(30,30), scale=30, color=color.color(0,0,0.5), rotation_z=90, position=(0,0,i-15))


def update():
    pass


app.run()

