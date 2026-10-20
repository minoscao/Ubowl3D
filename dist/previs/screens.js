import * as THREE from 'three';
const font='"Segoe UI","Microsoft YaHei",sans-serif';
function surface(w,h){
 const canvas=document.createElement('canvas');canvas.width=w;canvas.height=h;
 const ctx=canvas.getContext('2d');
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=4;
 return {canvas,ctx,texture};
}
function text(c,t,x,y,size=26,color='#233d34',weight=500){c.font=`${weight} ${size}px ${font}`;c.fillStyle=color;c.fillText(t,x,y);}
function rect(c,x,y,w,h,color){c.fillStyle=color;c.fillRect(x,y,w,h);}
function base(s,title){const c=s.ctx,w=s.canvas.width,h=s.canvas.height;rect(c,0,0,w,h,'#f3f0e6');rect(c,0,0,w,75,'#254b3e');text(c,'PiSell',26,49,31,'#fff',700);text(c,'DEMO',w-112,47,22,'#e9c8a9',600);text(c,title,26,128,30,'#294235',650);rect(c,25,h-47,w-50,1,'#c2cabe');text(c,'拍摄示意 · 虚拟数据',26,h-18,18,'#748573');return c;}
function option(c,label,y,selected,w=428){rect(c,25,y,w,76,selected?'#d9e8ce':'#fffdf6');rect(c,25,y,5,76,selected?'#567b42':'#d5dbcd');text(c,label,48,y+47,27);if(selected)text(c,'✓',w-15,y+46,29,'#45662f',700);}
export function createScreens(){
 const kiosk=surface(480,848),pos=surface(900,600),board=surface(1500,820),dashboard=surface(1400,800),scale=surface(560,150);
 let last='';
 function update(state){
  const key=`${state.screen}:${state.selection}:${state.order}`;
  if(key===last)return;last=key;
  const selected=state.selection,c=base(kiosk,({
   welcome:'欢迎来到 U Bowl',weight:'称重 · 自动去皮',soup:'01 选择汤底',spice:'02 选择口味',allergy:'03 过敏信息',dine:'04 用餐方式',pay:'05 支付',receipt:'下单成功',manual:'前台人工点单',scan:'扫描会员码',member:'会员已登录'
  })[state.screen]);
  switch(state.screen){
   case 'weight':
    text(c,'总重',30,225,26);text(c,selected?'0.85 kg':'0.20 kg',230,225,35);
    text(c,'皮重',30,313,26);text(c,'− 0.20 kg',210,313,35);
    rect(c,25,365,430,180,'#dbe7d1');text(c,'净重 / NET WEIGHT',47,415,24);
    text(c,selected?'0.65 kg':'0.00 kg',47,500,67,'#284732',700);text(c,'计价按净重 · 示例数值',30,600,24);break;
   case 'soup':['麻辣汤','番茄汤','菌菇汤'].forEach((v,i)=>option(c,v,190+i*100,selected&&i===0));break;
   case 'spice':['不辣','微辣','中辣'].forEach((v,i)=>option(c,v,190+i*100,selected&&i===1));break;
   case 'allergy':['无已知过敏','花生 / Peanut','其他备注'].forEach((v,i)=>option(c,v,190+i*100,selected&&i===1));text(c,'过敏信息请与店员确认',30,575,23);break;
   case 'dine':option(c,'Dine in · 堂食',220,selected);option(c,'Takeaway · 外带',330,false);break;
   case 'pay':text(c,'应付金额：••••',35,250,32);text(c,'银行卡号：•••• ••••',35,330,27);option(c,selected?'支付完成 ✓':'请靠近读卡区',450,selected);break;
   case 'receipt':text(c,'A318',36,300,98,'#30573c',700);text(c,'订单已发送至后厨',36,390,27);option(c,'票据已打印 ✓',490,true);break;
   case 'member':text(c,'DEMO MEMBER',30,250,38);text(c,'你好，体验会员',30,320,30);option(c,'会员登录成功 ✓',410,true);text(c,'示例积分  120',30,560,29);break;
   case 'scan':text(c,'将手机会员码',35,250,35);text(c,'靠近右下扫码窗',35,310,35);option(c,'等待扫描…',450,false);break;
   default:text(c,'自选 → 称重 → 点单',30,270,30);option(c,'开始点单',410,true);
  }
  if(['soup','spice','allergy','dine'].includes(state.screen)){rect(c,25,680,430,74,'#315443');text(c,'下一步  →',155,728,28,'#fff');}
  kiosk.texture.needsUpdate=true;
  rect(scale.ctx,0,0,560,150,'#142322');text(scale.ctx,state.screen==='weight'&&!selected?'0.000':'0.650',75,110,100,'#c9e2d8',650);scale.texture.needsUpdate=true;
  const p=base(pos,state.screen==='manual'?'人工点单 / POS':'员工端 / POS');
  rect(p,26,165,440,340,'#fffdf7');text(p,state.screen==='receipt'?'新订单 A318':'本单商品',48,214,28);
  text(p,'麻辣烫 · 净重 0.65 kg',48,282,25);text(p,'微辣 · 堂食',48,330,25);text(p,'金额 ••••',48,386,25);
  text(p,state.screen==='manual'?'人工添加商品  +':'订单操作',48,468,26,'#497048');
  rect(p,492,164,380,340,'#dce5d4');text(p,'顾客操作小窗',510,199,24);
  p.drawImage(kiosk.canvas,550,211,135,238);
  text(p,({spice:'口味选择',receipt:'支付完成',manual:'人工模式'})[state.screen]||'操作同步',700,305,22);
  text(p,'同一台双面设备 · DEMO',492,533,21,'#6c7e67');pos.texture.needsUpdate=true;
  const b=base(board,'U Bowl · 取餐进度');
  rect(b,26,164,713,550,'#e3e8e6');rect(b,761,164,713,550,'#e2ebd6');
  text(b,'Preparing',55,226,45,'#607f8c',650);text(b,'Ready to Pick Up',792,226,45,'#497244',650);
  text(b,'制作中',55,274,28);text(b,'请取餐',792,274,28);
  text(b,'A316',55,405,80,'#82928c',650);
  if(state.order==='preparing')text(b,'A318',55,541,95,'#36575a',700);
  if(state.order==='ready'){text(b,'A318',792,435,109,'#375b32',700);text(b,'A318 请取餐',792,535,35);text(b,'A318, ready for pickup',792,592,33);}
  if(state.order==='complete')text(b,'当前无待取餐订单',792,440,37,'#687f59');
  board.texture.needsUpdate=true;
 }
 const d=base(dashboard,'连锁管理 / DEMO 管理后台');
 text(d,'一套标准流程，多家门店复用',30,190,37);
 for(let i=0;i<10;i++){const x=30+(i%5)*271,y=237+Math.floor(i/5)*183;rect(d,x,y,249,155,'#e0e7d5');text(d,`门店 ${String(i+1).padStart(2,'0')}`,x+18,y+47,30);text(d,'点单 · 称重 · 取餐',x+18,y+90,21);text(d,'示例配置',x+18,y+127,19,'#6b8060');}
 text(d,'虚拟门店与数据 · 非 U Bowl 实际后台',30,680,26,'#708064');dashboard.texture.needsUpdate=true;
 return {kiosk,pos,board,dashboard,scale,update};
}
