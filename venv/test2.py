from ursina import *


class Snake(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.speed = 5
        self.origin_y = -.5
        self.camera_pivot = Entity(parent=self, y=2)

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

        self.direction = Vec3(
            self.forward * (held_keys['w'] - held_keys['s'])
            + self.right * (held_keys['d'] - held_keys['a'])+ self.down*self.camera_pivot.rotation_x/90*(held_keys['w'] - held_keys['s'])
        ).normalized()

        self.position += self.direction

app=Ursina()
sky=Sky()


person= Snake()
for i in range(30):
    grid = Entity(model=Grid(30, 30), scale=30, color=color.color(0, 0, 0.5), rotation_x=90, position=(0, i-15, 0))


app.run()