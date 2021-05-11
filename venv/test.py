from ursina import *
app=Ursina()
a = Audio('sound/04 - Sanctuary.ogg', pitch=1, loop=True, autoplay=True)
a.volume=0
b=Audio(a.clip)

def input(key):
    if key == 'f':
        a.fade_out(duration=4, curve=curve.linear)

app.run()