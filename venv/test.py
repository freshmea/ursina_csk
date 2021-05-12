from ursina import *
from ursina.mesh_importer import *


app=Ursina()
a = Audio('sound/04 - Sanctuary.ogg', pitch=1, loop=True, autoplay=True)
a.volume=0
b=Audio(a.clip)
obj_to_ursinamesh(name='badboy',return_mesh=False, save_to_file=True)
def input(key):
    if key == 'f':
        a.fade_out(duration=4, curve=curve.linear)

app.run()