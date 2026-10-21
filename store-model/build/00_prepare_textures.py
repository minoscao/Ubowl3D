from pathlib import Path
import cv2, numpy as np, random, json, math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]; TEX=ROOT/'textures'; REF=ROOT/'ref'
TEX.mkdir(exist_ok=True); rng=np.random.default_rng(12)
def read(p):return cv2.imdecode(np.fromfile(str(p),np.uint8),cv2.IMREAD_COLOR)
def warp(file,points,out,size):
 im=read(REF/file); dst=np.float32([[0,0],[size[0]-1,0],[size[0]-1,size[1]-1],[0,size[1]-1]])
 a=cv2.warpPerspective(im,cv2.getPerspectiveTransform(np.float32(points),dst),size)
 cv2.imencode('.jpg',a,[cv2.IMWRITE_JPEG_QUALITY,92])[1].tofile(str(TEX/out))
warp('20261011-161342.jpg',[(124,246),(1195,247),(1218,850),(94,847)],'menu.jpg',(1024,576))
warp('20261011-161351.jpg',[(468,388),(621,397),(623,477),(468,473)],'pickup.jpg',(768,432))
warp('20261011-161334.jpg',[(243,264),(661,280),(642,824),(260,813)],'price.jpg',(512,700))
warp('20261011-161334.jpg',[(686,272),(1077,277),(1035,794),(684,804)],'steps.jpg',(512,700))
warp('20261011-161359.jpg',[(493,600),(540,610),(499,687),(466,677)],'terminal.jpg',(360,600))
# Original shared material maps, no external dependencies.
N=512
def noise(n):
 small=rng.random((n,n)).astype(np.float32)
 return cv2.resize(small,(N,N),interpolation=cv2.INTER_CUBIC)
x,y=np.meshgrid(np.linspace(0,8,N),np.linspace(0,8,N))
a=noise(8); b=noise(32); cloud=noise(90)
flow=.55*a+.32*b+.13*cloud
vein=np.clip((.018-np.abs(noise(24)-.50))/.018,0,1)*.32
arr=np.zeros((N,N,3)); colors=[(136,61,17),(215,137,49)]
f=np.clip((flow-.15)*1.45,0,1)
for c in range(3):arr[:,:,c]=colors[0][c]*(1-f)+colors[1][c]*f+vein*(230-colors[1][c])
Image.fromarray(np.uint8(np.clip(arr,0,255))).save(TEX/'amber.jpg',quality=95)
# Subtle glazed handmade ceramic ripples normal map.
h=.60*noise(9)+.2*noise(28)+.2*noise(100)
gx,gy=np.gradient(h); n=np.stack([-gx*2.3,-gy*2.3,np.ones_like(h)],axis=2);n/=np.linalg.norm(n,axis=2,keepdims=True)
Image.fromarray(np.uint8((n*.5+.5)*255)).save(TEX/'ceramic-normal.png')
# Pale terrazzo, true material tile.
im=Image.new('RGB',(768,768),(215,211,201));d=ImageDraw.Draw(im);random.seed(6)
for _ in range(3500):
 px=random.randrange(768);py=random.randrange(768);r=random.uniform(1.2,8);co=random.choice([(65,57,48),(134,117,90),(232,226,217),(174,168,155),(92,85,79)])
 points=[(px+math.cos(k*2*math.pi/5)*r*random.uniform(.5,1.2),py+math.sin(k*2*math.pi/5)*r*random.uniform(.5,1.2)) for k in range(5)]
 d.polygon(points,fill=co)
im.save(TEX/'terrazzo.jpg',quality=92)
# Faithful text reconstruction of LED / small device UI, lettering is not whole-store image projection.
font='C:/Windows/Fonts/arial.ttf'; bold='C:/Windows/Fonts/arialbd.ttf'
im=Image.new('RGB',(3072,100),(184,17,25));d=ImageDraw.Draw(im)
d.text((30,18),'U BOWL MALATANG  BORN IN SICHUAN  MADE FOR THE WORLD  |  U BOWL',font=ImageFont.truetype(font,53),fill=(238,249,253))
for yy in range(1,100,3):d.line((0,yy,3072,yy),fill=(130,20,29),width=1)
im.save(TEX/'led.jpg',quality=95)
im=Image.new('RGB',(320,560),(226,243,246));d=ImageDraw.Draw(im)
d.text((57,35),'U Bowl',font=ImageFont.truetype(bold,46),fill=(184,28,25));d.text((49,112),'PICK • WEIGH',font=ImageFont.truetype(font,25),fill=(42,65,71));d.text((99,150),'ENJOY',font=ImageFont.truetype(bold,30),fill=(42,65,71));d.rounded_rectangle((35,213,285,405),radius=14,fill=(255,255,255));d.ellipse((69,230,251,388),fill=(111,67,32));d.ellipse((79,238,241,377),fill=(177,107,41))
for i in range(30):
 px=random.randint(92,225);py=random.randint(255,355);d.ellipse((px-10,py-8,px+11,py+9),fill=random.choice([(60,112,52),(192,160,100),(215,188,141),(131,58,36)]))
d.rounded_rectangle((36,450,284,511),radius=9,fill=(184,27,27));d.text((104,464),'START',font=ImageFont.truetype(bold,24),fill='white');im.save(TEX/'terminal-clean.jpg',quality=92)
print('Textures prepared:',len(list(TEX.iterdir())))
