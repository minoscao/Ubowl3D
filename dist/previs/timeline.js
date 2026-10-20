// Metres, Y up, +Z towards customers. All screen states are derived from time.
const K=[.79,1.387,.32], P=[.79,1.41,-.18], B=[-1.66,2.087,-1.19];
const kiosk={pos:[.80,1.64,1.56],target:K,lens:65};
const pos={pos:[1.02,1.65,-1.05],target:P,lens:55};
const board={pos:[-1.66,2.06,1.40],target:B,lens:48};
const shot=(id,scene,start,end,title,action,camera,cue,extra={})=>({id,scene,start,end,title,action,camera,cue,...extra});
export const shots=[
 shot('01A',1,0,3,'大锅翻拌','锅铲绕锅翻拌；蒸汽上升。现场补拍慢动作，保留锅铲与咕嘟原声。',{pos:[10.6,1.72,.64],target:[10,1.10,0],lens:50},'45° 俯拍 · 翻拌与蒸汽',{stage:'wok'}),
 shot('02A',2,3,10,'Diana 开场','替身标示 Diana 在店内明亮位置口播；柜台、取餐屏入背景。',{pos:[-2.75,1.5,4.7],target:[-2.75,1.35,.35],lens:65},'固定中景 · 主持人开场'),
 shot('03A',3,10,11.5,'取碗','从入口右侧取碗；动作连接进入自选区。',{pos:[3.65,1.57,1.05],target:[4.30,1.12,-.62],lens:38},'取碗 · 手部与入口同框'),
 shot('03B',3,11.5,13,'自选夹菜','Diana 站在通道中，左手持碗，右手夹菜；避免拍到其他客人。',{pos:[3.80,1.58,.10],target:[3.86,1.26,-1.58],lens:35},'夹菜 · 约 1 米通道'),
 shot('03C',3,13,14.5,'丸子与豆制品','从层架空隙拍食材，备拍毛肚、丸子和豆制品；模型食材为示意。',{pos:[3.70,1.69,-2.14],target:[3.70,1.52,-2.655],lens:60},'食材快切 · 1.5 秒'),
 shot('03D',3,14.5,16,'蔬菜特写','切到另一侧食材；现场选择刚补货的整齐菜盘。',{pos:[3.87,1.67,-1.70],target:[4.62,1.52,-1.70],lens:65},'食材快切 · 蔬菜'),
 shot('04A',4,16,18,'引导至设备','Diana 在顾客侧介绍双面设备，手势引向电子秤。',{pos:[1.90,1.56,3.20],target:[1.24,1.25,.20],lens:43},'中景转设备 · 称重流程'),
 shot('04B',4,18,20,'称重与去皮','碗放到电子秤。演示数值：总重 0.85 kg − 皮重 0.20 kg = 净重 0.65 kg。',{pos:[1.10,1.71,1.70],target:[1.01,1.35,.14],lens:55},'重量联动 · 去皮数据清晰'),
 shot('04C',4,20,22,'选择汤底','顾客点击汤底，选中麻辣汤。屏幕均为预演界面。',kiosk,'屏幕特写 · 汤底'),
 shot('04D',4,22,23.2,'选择口味','点击微辣；按实际产品界面核对选项。',kiosk,'屏幕特写 · 口味'),
 shot('04E',4,23.2,24.4,'过敏信息','展示过敏信息选择与备注，预演选中花生。',kiosk,'屏幕特写 · 过敏备注'),
 shot('04F',4,24.4,25.6,'堂食或外带','点击 Dine in，选项需要清楚入画。',kiosk,'屏幕特写 · Dine in'),
 shot('04G',4,25.6,27.3,'刷卡支付','手部靠近读卡区；金额与卡号以遮罩示意，不出现真实数据。',{pos:[1.05,1.50,1.60],target:[.83,1.27,.32],lens:45},'手部特写 · 支付信息遮挡'),
 shot('04H',4,27.3,30,'双面同步出票','顾客端成功、员工端接单并出票。二分屏表示同一订单的同步画面。',kiosk,'二分屏 · 订单 A318 同步出票',{split:pos}),
 shot('05A',5,30,32,'POS 监控小窗','特写员工端的小窗，显示顾客停留在口味选择步骤。',pos,'员工端特写 · 顾客操作小窗'),
 shot('05B',5,32,34.2,'顾客与前台对照','二分屏：顾客端选口味，前台小窗显示相同步骤。',kiosk,'二分屏 · 同步查看顾客进度',{split:pos}),
 shot('05C',5,34.2,36,'人工 POS 兜底','员工在背屏操作，示意人工点单作为另一种服务方式。',{pos:[1.36,1.68,-.95],target:[.84,1.32,-.12],lens:45},'员工操作 · 人工点单'),
 shot('06A',6,36,38,'Preparing','下单后，取餐屏 A318 出现在 Preparing 栏。',board,'订单 A318 · Preparing'),
 shot('06B',6,38,39.4,'第一次扫码','员工扫描票据；镜头末订单转为 Ready to Pick Up。',{pos:[-1.14,1.49,1.18],target:[-1.25,1.24,.08],lens:55},'扫码 ① · 完成备餐',{split:board}),
 shot('06C',6,39.4,41.5,'Ready + 双语叫号','A318 从 Preparing 移至 Ready；正式拍摄录下中英文叫号。',board,'A318 请取餐 / A318, ready for pickup'),
 shot('06D',6,41.5,42.8,'第二次扫码','客人取餐时再次扫描；镜头末 A318 从取餐屏消失。',{pos:[-1.14,1.49,1.18],target:[-1.25,1.24,.08],lens:55},'扫码 ② · 确认取餐',{split:board}),
 shot('06E',6,42.8,45,'客人取餐','顾客端取走餐碗，大屏中不再显示 A318。',{pos:[-1.6,1.57,2.70],target:[-1.28,1.25,.04],lens:42},'取餐完成 · 订单移出大屏'),
 shot('07A',7,45,47.5,'会员码扫描','手机靠近设备右下扫码窗；窗口位置为拍摄示意，现场确认。',{pos:[1.17,1.42,1.15],target:[.87,1.19,.43],lens:50},'右下扫码窗 · 会员码'),
 shot('07B',7,47.5,49.5,'登录会员','顾客端显示会员登录成功，所有身份、积分均为虚拟数据。',kiosk,'会员登录 · DEMO 数据'),
 shot('07C',7,49.5,53,'多门店后台','虚拟后台展示 01–10 家门店及标准流程。独立插入镜头，不代表已上线后台。',{pos:[10,1.40,1.80],target:[10,1.40,0],lens:50},'后台插入 · 虚拟多店 DEMO',{stage:'dashboard'}),
 shot('08A',8,53,57.5,'Diana 收尾','Diana 站在设备旁收尾，设备与店内环境自然入画。',{pos:[1.65,1.55,3.60],target:[1.32,1.22,.35],lens:45},'主持人中景 · 收尾口播'),
 shot('08B',8,57.5,60,'品牌与 Slogan','保留安全区；正式制作替换 PiSell 官方 Logo 和品牌色。',{pos:[.4,2.6,9],target:[.4,1.45,-.3],lens:40},'片尾定格 · 品牌字样占位',{endCard:true}),
];
export function stateAt(time){
 const t=Math.max(0,Math.min(60,Number(time)||0));
 const shot=shots.find(s=>t>=s.start&&t<s.end)||shots.at(-1);
 const progress=Math.min(1,(t-shot.start)/(shot.end-shot.start));
 let screen='welcome';
 if(t>=18&&t<20)screen='weight';
 else if(t>=20&&t<22)screen='soup';
 else if(t>=22&&t<23.2)screen='spice';
 else if(t>=23.2&&t<24.4)screen='allergy';
 else if(t>=24.4&&t<25.6)screen='dine';
 else if(t>=25.6&&t<27.3)screen='pay';
 else if(t>=27.3&&t<30)screen='receipt';
 else if(t>=30&&t<34.2)screen='spice';
 else if(t>=34.2&&t<36)screen='manual';
 else if(t>=45&&t<47.5)screen='scan';
 else if(t>=47.5&&t<53)screen='member';
 const order=t<36?'idle':t<39.1?'preparing':t<42.5?'ready':'complete';
 return {time:t,shot,progress,screen,order,selection:progress>.38,scanPulse:(t>=38.7&&t<39.1)||(t>=42.1&&t<42.5)};
}
