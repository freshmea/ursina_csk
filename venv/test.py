import random

from ursina import *
import numpy as np

def update():
    global e1
    for i in range(num2):
        angle = i* 360 / num2 / 180 * np.pi
        for entity in e1[i]:
            radius=entity.x/np.cos(angle)
            radius -= random.randint(1,5)*.005
            entity.x=radius*np.cos(angle)
            entity.z=radius*np.sin(angle)
            entity.y=-3/abs(entity.x/np.cos(angle))+3
            if radius<.3:
                entity.x=4*np.cos(angle)
                entity.z=4*np.sin(angle)
                entity.y=-3000/(4*np.cos(angle))

app=Ursina()
num=40
num2=50
radius = np.linspace(4, .3, num)
x1=list()
y1=list()
z1=list()

for i in range(num2):
    angle=i*360/num2/180*np.pi
    x1.append(radius*np.cos(angle))
    z1.append(radius*np.sin(angle))
    y1.append(-3000/abs(radius*np.cos(angle))+3)

e1=list()
for i in range(num2):
    e1.append([None]*num)

for i in range(num2):
    colors=random.choice([color.red, color.yellow, color.white, color.cyan, color.green])
    for j in range(num):
        e1[i][j]=Entity(model='sphere', color=colors, scale=.1, x=x1[i][j], y=y1[i][j], z=z1[i][j])



EditorCamera()
Text(text='Funnel Waterfall', position=(0, .4), origin=(0,0), background=True)
app.run()