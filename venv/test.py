from ursina import *
app = Ursina()
descr = dedent('''
  <scale:1.5><orange>Rainstorm<default><scale:1>
  Summon a <azure>rain storm <default>to deal 5 <azure>water

  damage <default>to <hsb(0,1,.7)>everyone, <default><image:file_icon> <red><image:file_icon> test <default>including <orange>yourself. <default>
  Lasts for 4 rounds.''').strip()

Text.default_resolution = 1080 * Text.size



text = Text('1234\wefw\nwefwef\n wjfoi')
text.create_background(radius=0, padding=0)
app.run()