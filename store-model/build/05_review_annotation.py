"""Neutral technical comparison layout and mesh-derived dimension annotations."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
r=Path(__file__).resolve().parents[1]/'review'
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
for ref,render,out in [('partition-2.8.jpg','partition-corrected.png','partition-comparison.jpg'),('partition-3.8.jpg','entry-matched.png','entry-comparison.jpg')]:
    im=Image.new('RGB',(1400,1210),(237,233,223));d=ImageDraw.Draw(im)
    for idx,(fn,label) in enumerate([(ref,'实拍 · 视频连续帧'),(render,'调整版 · 近似同机位')]):
        a=Image.open(r/fn).convert('RGBA');a.thumbnail((660,1060));x=20+idx*700+(660-a.width)//2;y=70+(1060-a.height)//2
        im.paste(a,(x,y),a);d.text((25+idx*700,20),label,font=font,fill=(48,41,35))
    d.text((26,1140),'检查红墙、入口宽度、侧壁碗柜和向内的冷柜开口关系。',font=small,fill=(48,41,35))
    d.text((26,1175),'镜头为近似匹配；尺寸未实测，不能据此认定测绘精度。',font=small,fill=(100,91,78));im.save(r/out,quality=94)
a=Image.open(r/'entry-top.png').convert('RGBA');im=Image.new('RGB',a.size,(237,233,223));im.paste(a,(0,0),a);d=ImageDraw.Draw(im)
c=json.loads((r/'clearance-validation.json').read_text());blue=(18,92,138)
for n,line in enumerate(c['annotationPixelLines']):
    (x0,y0),(x1,y1)=line['points'];d.line((x0,y0,x1,y1),fill=blue,width=6)
    for x,y in [(x0,y0),(x1,y1)]:d.line((x,y-22,x,y+22),fill=blue,width=5)
    label=('货架外沿净宽 ' if n==0 else '入口保守投影净宽 ')+line['text']
    bb=d.textbbox((0,0),label,font=small);tw=bb[2]-bb[0];tx=(x0+x1-tw)/2;ty=y0-45
    d.rounded_rectangle((tx-10,ty-5,tx+tw+10,ty+35),radius=8,fill=(250,248,241));d.text((tx,ty),label,font=small,fill=blue)
d.rectangle((0,0,1000,80),fill=(237,233,223));d.text((28,18),'调整版 · 入口与取菜区俯视',font=font,fill=(48,41,35))
d.rectangle((0,1080,1000,1200),fill=(237,233,223));d.text((25,1096),'连续直行带：%.3f m；计入层架前沿与凹柜玻璃突出部分。'%c['continuousStraightCorridor_m'],font=small,fill=(48,41,35))
d.text((25,1136),'依据模型实际网格边界核算。约 1 m 为用户估计，非实测尺寸。',font=small,fill=(78,70,59))
im.save(r/'entry-top-annotated.png')
