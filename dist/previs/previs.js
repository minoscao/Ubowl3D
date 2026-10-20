import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { createProps } from './props.js';
import { createScreens } from './screens.js';
import { shots,stateAt } from './timeline.js';

const $=s=>document.querySelector(s),V=a=>new THREE.Vector3(...a);
const clockLabel=t=>`${String(Math.floor(t/60)).padStart(2,'0')}:${(t%60).toFixed(1).padStart(4,'0')}`;
const rangeLabel=s=>`${s.start.toFixed(1)}–${s.end.toFixed(1)} s`;
let time=0,playing=false,speed=1,loaded=false,model,script,renderer,scene,camera,secondCamera,props,screens;
let previousStamp=0,lastShot='',lastScene=0,dirty=true,frameCount=0;
let kioskPlane,posPlane,boardPlane,dashboardPlane,scalePlane,weighBowl,hand,arm,tongs,scanBeam,memberWindow,wokStage;
const metadataURL=new URL('./script.json',import.meta.url);
const viewport=$('#viewport');
function toast(message){$('#toast').textContent=message;$('#toast').style.display='block';setTimeout(()=>$('#toast').style.display='none',3500);}
function error(message){playing=false;loaded=false;$('#play').disabled=true;$('#loader').hidden=false;$('#load-text').textContent=message;const link=document.createElement('a');link.href='./';link.textContent='重新加载 ↻';$('#loader').append(link);}
function play(value){if(!loaded)return;playing=value;if(playing&&time>=60)time=0;$('#play').textContent=playing?'Ⅱ 暂停':'▶ 播放';$('#play').setAttribute('aria-label',playing?'暂停预演':'播放预演');$('#play').setAttribute('aria-pressed',String(playing));dirty=true;}
function seek(t){time=Math.max(0,Math.min(60,t));dirty=true;}
function jump(index){play(false);seek(shots[Math.max(0,Math.min(shots.length-1,index))].start);$('#frame').scrollIntoView({block:'center',behavior:'instant'});}
function paintUI(state){
 const sh=state.shot;
 $('#time').value=`${clockLabel(time)} / 01:00`;
 $('#timeline').value=time;$('#timeline').setAttribute('aria-valuetext',`${time.toFixed(1)} 秒，${sh.title}`);
 $('#frame').dataset.time=time.toFixed(2);$('#frame').dataset.shot=sh.id;$('#frame').dataset.order=state.order;$('#frame').dataset.screen=state.screen;
 if(lastShot!==sh.id){
  lastShot=sh.id;$('#slate').textContent=`${sh.id} / ${sh.title}`;$('#cue').textContent=sh.cue;
  $('#lens').textContent=`${sh.camera.lens} mm · 建议`;
  $('#shot-code').textContent=sh.id;$('#shot-title').textContent=sh.title;$('#shot-time').textContent=`${rangeLabel(sh)} · ${(sh.end-sh.start).toFixed(1)} 秒`;
  $('#direction').textContent=sh.action;$('#camera-info').textContent=`全画幅约 ${sh.camera.lens} mm`;
  $('#split-labels').hidden=!sh.split;$('#end-card').hidden=!sh.endCard;
  $('#split-left').textContent=sh.scene===6?'扫码动作':'顾客端';$('#split-right').textContent=sh.scene===6?'订单状态':'员工端';
  document.querySelectorAll('[data-shot]').forEach(b=>{if(b.tagName==='BUTTON')b.setAttribute('aria-current',String(b.dataset.shot===sh.id));});
 }
 if(lastScene!==sh.scene){
  lastScene=sh.scene;const s=script.scenes[sh.scene-1];
  $('#scene-number').textContent=`SCENE ${s.id} / 08`;$('#scene-title').textContent=s.title;$('#voice').textContent=s.voice;
  $('#notes').textContent=s.notes.replaceAll('⚠️','').trim();$('#voice-duration').textContent=`分配 ${s.end-s.start} 秒`;
  $('#timing').textContent=s.readingSeconds>s.end-s.start?`原稿口播粗估约 ${s.readingSeconds} 秒，超出本场 ${s.end-s.start} 秒。实拍需精简台词或延长剪辑。`:sh.scene===1?'声音提示：现场收录翻拌与沸腾声。':'口播时间仅为粗估，正式拍摄前试读。';
  document.querySelectorAll('[data-scene]').forEach(b=>b.setAttribute('aria-current',String(Number(b.dataset.scene)===sh.scene)));
 }
}
function mesh(geometry,material,p){const m=new THREE.Mesh(geometry,material);if(p)m.position.set(...p);scene.add(m);return m;}
function makeScreen(surface,width,height,p,rotation=[0,0,0]){
 const m=mesh(new THREE.PlaneGeometry(width,height),new THREE.MeshBasicMaterial({map:surface.texture,toneMapped:false,side:THREE.DoubleSide}),p);m.rotation.set(...rotation);return m;
}
function link(m,a,b,r){const direction=V(b).sub(V(a));m.position.copy(V(a)).add(V(b)).multiplyScalar(.5);m.scale.set(r,direction.length(),r);m.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),direction.normalize());}
function poseActor(actor,position,rotation,left,right){actor.visible=true;actor.position.set(...position);actor.rotation.set(0,rotation,0);actor.pose(V(left),V(right));actor.updateMatrixWorld(true);}
function cameraPose(cam,spec,aspect,progress=0){cam.aspect=aspect;cam.fov=THREE.MathUtils.radToDeg(2*Math.atan(36/(2*spec.lens*aspect)));cam.position.set(...spec.pos);cam.lookAt(...spec.target);cam.updateProjectionMatrix();cam.updateMatrixWorld();}
function showHand(position,back=false){hand.visible=true;arm.visible=true;hand.position.set(...position);hand.rotation.set(back?Math.PI:0,0,-.4);link(arm,[position[0]+.12,position[1]-.20,position[2]+(back?-.28:.28)],position,.038);}
function updateObjects(s){
 const {host,staff}=props.actors,sh=s.shot,p=s.progress;
 [host,staff,props.wok,props.foodBowl,props.phone,props.ticket,props.scanner,hand,arm,tongs,scanBeam,memberWindow,wokStage,dashboardPlane].forEach(o=>o.visible=false);
 model.visible=!sh.stage;[kioskPlane,posPlane,boardPlane,scalePlane,weighBowl].forEach(o=>o.visible=model.visible);
 weighBowl.position.set(1.28,1.199,.02);
 if(sh.id==='04B')weighBowl.position.add(V([0,Math.max(0,.38-p)*.5,Math.max(0,.38-p)*.6]));
 scene.background.set(sh.stage?'#29372e':'#e9e5db');
 props.foodBowl.scale.setScalar(1);props.phone.rotation.set(0,0,0);props.ticket.rotation.set(0,0,0);props.scanner.rotation.set(0,0,0);
 if(sh.stage==='wok'){
  props.wok.visible=true;wokStage.visible=true;props.wok.position.set(10,.96,0);
  props.wok.userData.ladle.rotation.y=s.time*1.6;props.wok.userData.ladle.rotation.z=Math.sin(s.time*2)*.15;props.updateSteam(s.time);
 }else if(sh.stage==='dashboard')dashboardPlane.visible=true;
 else if(sh.scene===2||sh.id==='08A'||sh.id==='04A'){
  const opening=sh.scene===2;poseActor(host,opening?[-2.75,0,.94]:[1.77,0,.92],0,[-.29,1.09,.17],[.30,1.16+.04*Math.sin(time*2),.14]);
 }else if(sh.id==='03A'||sh.id==='03B'){
  const picking=sh.id==='03B',reach=.36+.12*Math.sin(p*Math.PI);
  poseActor(host,picking?[3.89,0,-1.40]:[3.86,0,-.44],picking?-Math.PI/2:Math.PI/2,[-.17,1.12,.26],[.17,1.17+.08*Math.sin(p*Math.PI),reach]);
  props.foodBowl.visible=true;props.foodBowl.position.copy(host.localToWorld(V([-.17,1.03,.39])));
  props.foodBowl.children.forEach((o,i)=>{o.visible=i===0||picking;});
  tongs.visible=picking;tongs.position.copy(host.localToWorld(V([.17,1.13,reach+.07])));tongs.rotation.set(0,Math.PI/2,.35);
 }else if(sh.id==='04B'){
  showHand([1.44,1.24+Math.max(0,.38-p)*.5,.12+Math.max(0,.38-p)*.6]);
 }else if(['04C','04D','04E','04F'].includes(sh.id)){
  showHand([.92,1.37,.48+Math.abs(Math.sin(p*Math.PI))*.08]);
 }else if(sh.id==='04G'){
  showHand([.89,1.09,.55]);props.phone.visible=true;props.phone.position.set(.87,1.11,.55);props.phone.rotation.x=-.75;
 }else if(sh.id==='04H'){
  props.ticket.visible=true;props.ticket.position.set(.79,1.05+.07*Math.min(1,p*3),.514);
 }else if(sh.id==='05C'){
  showHand([.88,1.37,-.26],true);
 }else if(sh.id==='06B'||sh.id==='06D'){
  props.ticket.visible=true;props.ticket.position.set(-1.32,1.23,.17);
  props.scanner.visible=true;props.scanner.position.set(-1.16,1.30,-.07);props.scanner.rotation.set(.4,-.40,0);
  showHand([-1.16,1.245,-.07],true);scanBeam.visible=s.scanPulse;
 }else if(sh.id==='06E'){
  props.foodBowl.visible=true;props.foodBowl.children.forEach(o=>o.visible=true);props.foodBowl.position.set(-1.27,1.19+Math.min(p,.5)*.25,.17+p*.85);
  showHand([-1.11,1.19+Math.min(p,.5)*.25,.17+p*.85]);
 }else if(sh.id==='07A'){
  memberWindow.visible=true;props.phone.visible=true;props.phone.position.set(.89,1.14,.54+(.5-Math.min(.5,p))*.15);props.phone.rotation.y=Math.PI;
  showHand([.92,1.12,.61]);
 }
 if(model.visible)memberWindow.visible=true;
 screens.update(s);
}
function render(s){
 const w=viewport.clientWidth,h=viewport.clientHeight;
 if(!w||!h)return;
 renderer.setScissorTest(true);renderer.setViewport(0,0,w,h);renderer.setScissor(0,0,w,h);renderer.clear();
 // Letterbox the same 16:9 composition when fullscreen has another aspect.
 const vw=Math.min(w,h*16/9),vh=vw*9/16,x=(w-vw)/2,y=(h-vh)/2;
 const sh=s.shot;
 if(sh.split){
  const half=vw/2;
  cameraPose(camera,sh.camera,8/9);
  renderer.setViewport(x,y,half,vh);renderer.setScissor(x,y,half,vh);renderer.render(scene,camera);
  cameraPose(secondCamera,sh.split,8/9);
  renderer.setViewport(x+half,y,half,vh);renderer.setScissor(x+half,y,half,vh);renderer.render(scene,secondCamera);
 }else{
  cameraPose(camera,sh.camera,16/9,s.progress);renderer.setViewport(x,y,vw,vh);renderer.setScissor(x,y,vw,vh);renderer.render(scene,camera);
 }
 renderer.setScissorTest(false);frameCount++;$('#frame').dataset.rendered=String(frameCount);
}
async function init(){
 script=await (await fetch(metadataURL)).json();
 script.scenes.forEach((s,i)=>{const b=document.createElement('button');b.dataset.scene=i+1;b.innerHTML=`${s.id} ${['翻拌','开场','夹菜','称重下单','POS','取餐','会员','收尾'][i]}<small>${s.start}–${s.end}s</small>`;b.onclick=()=>jump(shots.findIndex(sh=>sh.scene===i+1));$('#chapters').append(b);});
 shots.forEach((s,i)=>{const b=document.createElement('button');b.dataset.shot=s.id;b.innerHTML=`<b>${s.id}</b><span>${s.title}</span><small>${rangeLabel(s)}</small>`;b.onclick=()=>jump(i);$('#shots').append(b);});
 const reading=script.scenes.reduce((sum,s)=>sum+s.readingSeconds,0);
 $('#timing-overview').textContent=`按每秒 4 个中文字／英文词粗估，全文口播约 ${reading} 秒，未包含停顿与 3 秒无旁白开场。60 秒版本需另行精简台词；此版用于检查镜头顺序与覆盖范围。`;
 scene=new THREE.Scene();scene.background=new THREE.Color('#e9e5db');camera=new THREE.PerspectiveCamera(38,16/9,.015,100);secondCamera=camera.clone();
 renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,1.75));
 renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.95;renderer.autoClear=false;
 renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;viewport.append(renderer.domElement);
 renderer.domElement.setAttribute('aria-label','实时三维分镜画面');
 renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();error('图形显示已暂停，请重新加载预演。');});
 const pm=new THREE.PMREMGenerator(renderer),room=new RoomEnvironment();scene.environment=pm.fromScene(room,.04).texture;scene.environmentIntensity=.65;room.dispose();pm.dispose();
 scene.add(new THREE.HemisphereLight('#fff1d9','#a2937c',1.75));
 const sun=new THREE.DirectionalLight('#fff2dc',2.5);sun.position.set(-4,10,7);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);Object.assign(sun.shadow.camera,{left:-14,right:14,top:8,bottom:-8,near:.5,far:40});sun.shadow.normalBias=.02;scene.add(sun);
 const fill=new THREE.DirectionalLight('#fff8ef',1.3);fill.position.set(8,4,4);scene.add(fill);
 const inside=new THREE.PointLight('#ffeed6',8,5,2);inside.position.set(3.85,2.4,-1.9);scene.add(inside);
 props=createProps(scene);screens=createScreens();
 weighBowl=props.foodBowl.clone();weighBowl.scale.setScalar(1.34);scene.add(weighBowl);
 kioskPlane=makeScreen(screens.kiosk,.248,.438,[.79,1.387,.325],[-THREE.MathUtils.degToRad(24),0,0]);
 posPlane=makeScreen(screens.pos,.39,.26,[.79,1.43,-.185],[0,Math.PI,0]);
 const bezel=mesh(new THREE.BoxGeometry(.42,.29,.035),new THREE.MeshStandardMaterial({color:'#252a28'}),[.79,1.43,-.164]);
 // A previs-only rear screen: exact production hardware must be matched on location.
 bezel.name='DEMO rear display housing';
 boardPlane=makeScreen(screens.board,1.454,.793,[-1.66,2.087,-1.196]);
 scalePlane=makeScreen(screens.scale,.139,.038,[1.28,1.132,.239]);
 dashboardPlane=makeScreen(screens.dashboard,1.26,.72,[10,1.40,0]);
 hand=props.makeHand();scene.add(hand);arm=mesh(new THREE.CylinderGeometry(1,1,1,10),new THREE.MeshStandardMaterial({color:'#d2c8bb',roughness:.8}));
 tongs=new THREE.Group();for(const x of [-.018,.018]){const m=new THREE.Mesh(new THREE.BoxGeometry(.008,.014,.22),new THREE.MeshStandardMaterial({color:'#b6aa86',metalness:.8,roughness:.25}));m.position.x=x;tongs.add(m);}scene.add(tongs);
 scanBeam=mesh(new THREE.CylinderGeometry(1,1,1,8),new THREE.MeshBasicMaterial({color:'#ed6550',transparent:true,opacity:.65}));link(scanBeam,[-1.18,1.29,.02],[-1.32,1.23,.17],.006);
 memberWindow=mesh(new THREE.BoxGeometry(.055,.035,.012),new THREE.MeshStandardMaterial({color:'#152b26',emissive:'#337d52',emissiveIntensity:.6}),[.88,1.15,.431]);
 wokStage=mesh(new THREE.CylinderGeometry(.62,.62,.05,40),new THREE.MeshStandardMaterial({color:'#4b5149',metalness:.7,roughness:.4}),[10,.935,0]);
 const gltf=await new GLTFLoader().loadAsync(new URL('../assets/UBowl_store.glb',import.meta.url).href,p=>{if(p.total)$('#load-text').textContent=`载入店铺 · ${Math.round(p.loaded/p.total*100)}%`;});
 model=gltf.scene;model.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;}});
 // Replace only the right station's bowl and digits with animated props in this viewer.
 // The base GLB remains byte-identical to the approved store model.
 model.getObjectByName('checkout_right_Assembly')?.traverse(o=>{
  if(o.isMesh&&['gold','gold_edge','food_cream','leaf_green','blue_digits'].includes(o.material?.name))o.visible=false;
 });
 scene.add(model);loaded=true;$('#play').disabled=false;$('#loader').hidden=true;
 const resize=()=>{renderer.setSize(viewport.clientWidth,viewport.clientHeight,false);dirty=true;};new ResizeObserver(resize).observe(viewport);resize();
 const initial=Number(new URL(location.href).searchParams.get('t'));if(Number.isFinite(initial))seek(initial);
 function loop(stamp){
  requestAnimationFrame(loop);const dt=previousStamp?Math.min((stamp-previousStamp)/1000,.1):0;previousStamp=stamp;
  if(document.hidden||!loaded)return;
  if(playing){time=Math.min(60,time+dt*speed);dirty=true;if(time>=60)play(false);}
  if(!dirty)return;
  const s=stateAt(time);bezel.visible=!s.shot.stage;paintUI(s);updateObjects(s);render(s);dirty=false;
 }
 requestAnimationFrame(loop);
}
$('#play').onclick=()=>play(!playing);
$('#prev').onclick=()=>jump(shots.indexOf(stateAt(time).shot)-1);$('#next').onclick=()=>jump(shots.indexOf(stateAt(time).shot)+1);
$('#timeline').addEventListener('input',e=>{play(false);seek(Number(e.target.value));});
$('#speed').onchange=e=>speed=Number(e.target.value);
$('#fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await $('#frame').requestFullscreen();}catch{toast('当前浏览器不支持全屏。');}};
document.addEventListener('keydown',e=>{
 if(['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName))return;
 if(e.code==='Space'&&(document.fullscreenElement||!['BUTTON','A','SUMMARY'].includes(e.target.tagName))){e.preventDefault();play(!playing);}
 if(e.key==='ArrowRight'){e.preventDefault();jump(shots.indexOf(stateAt(time).shot)+1);}
 if(e.key==='ArrowLeft'){e.preventDefault();jump(shots.indexOf(stateAt(time).shot)-1);}
});
document.addEventListener('visibilitychange',()=>{previousStamp=0;if(document.hidden)play(false);else dirty=true;});
init().catch(e=>{console.error(e);error('预演未能加载，请检查网络后重新打开。');});
