import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const refs = [
  {file:'ref-01.jpg', title:'入口与流程立牌', original:'20261011-161334.jpg'},
  {file:'ref-02.jpg', title:'汤底菜单屏', original:'20261011-161342.jpg'},
  {file:'ref-03.jpg', title:'顾客反馈屏', original:'20261011-161347.jpg'},
  {file:'ref-04.jpg', title:'门店正面', original:'20261011-161351.jpg'},
  {file:'ref-05.jpg', title:'招牌与柜台左侧', original:'20261011-161355.jpg'},
  {file:'ref-06.jpg', title:'柜台与收银设备', original:'20261011-161359.jpg'},
  {file:'ref-07.jpg', title:'称重收银近景', original:'20261011-161403.jpg'},
  {file:'ref-08.jpg', title:'食材区入口', original:'20261011-161407.jpg'},
  {file:'video-01.mp4',poster:'video-01.jpg',title:'正面柜台视频',original:'飞书20261011-161415.mp4',video:true},
  {file:'video-02.mp4',poster:'video-02.jpg',title:'自助称重视频',original:'飞书20261011-161419.mp4',video:true},
  {file:'video-03.mp4',poster:'video-03.jpg',title:'付款与出餐视频',original:'飞书20261011-161423.mp4',video:true},
  {file:'video-04.mp4',poster:'video-04.jpg',title:'店内环视视频',original:'飞书20261011-161426.qt',video:true},
];
const views = {
  overview:{position:[7.8,4.8,12],target:[0,1.35,-0.7],title:'整体空间',detail:'棕红砖面、暖色灯棚与店内陈列。',reference:3,index:1},
  front:{position:[-0.1,2.1,13.8],target:[-0.1,1.6,-0.5],title:'门头正面',detail:'品牌招牌、弧形灯棚与连续柜台。',reference:3,index:2},
  counter:{position:[2.4,2.5,4.5],target:[0.3,1.15,0.0],title:'称重收银',detail:'双自助设备、电子秤与黄铜食材碗。',reference:6,index:3},
  ingredients:{position:[3.85,1.65,.6],target:[3.85,1.40,-2.95],title:'自选食材',detail:'两侧冷柜朝向通道，净通行宽度按约 1 米估算。',reference:7,index:4},
  plan:{position:[0,14,0.2],target:[0,0.35,-1.0],title:'俯瞰布局',detail:'顶棚已移开，查看柜台与自选区的关系。',reference:7,index:5},
};
let activeView='overview', model, renderer, camera, controls, scene, transition, roofHidden=false, toastTimer;
let failed=false, lastTime=0, isVisible=true, hasLoaded=false, userMoved=false, modelBounds;
const stage=$('.stage'), viewport=$('#viewport'), loader=$('#loader');
const assetURL=(file)=>new URL('./assets/'+file,import.meta.url).href;
const toast=(text)=>{const el=$('#toast');el.textContent=text;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),2600);};

function setRoof(hidden) {
  roofHidden=hidden;
  if(model) model.traverse(o=>{if(/^(canopy_|roof_)/i.test(o.name))o.visible=!hidden;});
  $('#roof-toggle').setAttribute('aria-pressed',String(hidden));
  $('#roof-toggle').textContent=hidden?'显示顶棚':'隐藏顶棚';
  if(activeView==='plan')$('#view-detail').textContent=hidden?'顶棚已移开，查看柜台与自选区的关系。':'顶棚已显示，可再次隐藏以查看内部布局。';
}
function setAutoRotate(value){if(controls)controls.autoRotate=value;$('#rotate-toggle').setAttribute('aria-pressed',String(value));$('#rotate-toggle').textContent=value?'停止旋转':'自动旋转';}
function viewPose(name){
  const view=views[name],pos=new THREE.Vector3(...view.position),target=new THREE.Vector3(...view.target);
  if(name==='ingredients')return {pos,target};
  const bounds=name==='counter'?new THREE.Box3(new THREE.Vector3(-1.1,.55,-.7),new THREE.Vector3(2.2,2.05,.65)):
    (modelBounds||new THREE.Box3(new THREE.Vector3(-4.66,-.23,-3.30),new THREE.Vector3(4.65,3.43,1.58)));
  const direction=pos.clone().sub(target).normalize(),right=new THREE.Vector3(direction.z,0,-direction.x).normalize(),up=new THREE.Vector3().crossVectors(direction,right);
  const vertical=Math.tan(THREE.MathUtils.degToRad(camera.fov/2)),horizontal=vertical*viewport.clientWidth/Math.max(1,viewport.clientHeight);
  let distance=pos.distanceTo(target);
  for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]){
    const corner=new THREE.Vector3(x,y,z).sub(target);
    distance=Math.max(distance,corner.dot(direction)+Math.max(Math.abs(corner.dot(right))/(horizontal*.88),Math.abs(corner.dot(up))/(vertical*.78)));
  }
  return {pos:direction.multiplyScalar(distance).add(target),target};
}
function setView(name,animate=true){
  const view=views[name];if(!view)return;
  activeView=name;
  $$('[data-view]').forEach(b=>{const active=b.dataset.view===name;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
  $('#view-counter').textContent=String(view.index).padStart(2,'0')+' / 05';
  $('#view-title').textContent=view.title;$('#view-detail').textContent=view.detail;
  $('#reference-image').src=assetURL(refs[view.reference].file);$('#reference-image').alt=refs[view.reference].title;
  setRoof(name==='plan');setAutoRotate(false);
  if(camera&&controls){
    userMoved=false;
    camera.fov=name==='ingredients'?64:38;camera.updateProjectionMatrix();
    const {pos,target}=viewPose(name);
    if(animate&&!reducedMotion){transition={start:performance.now(),duration:1100,fromPosition:camera.position.clone(),fromTarget:controls.target.clone(),position:pos,target};}
    else{transition=null;camera.position.copy(pos);controls.target.copy(target);controls.update();}
  }
  history.replaceState(null,'','#'+name);
}

function showReference(index){
  const ref=refs[index],host=$('.reference-main');
  host.querySelector('video')?.pause();host.querySelector('video')?.remove();
  const image=$('#large-reference');image.hidden=!!ref.video;image.style.display=ref.video?'none':'block';
  if(ref.video){const video=document.createElement('video');video.controls=true;video.playsInline=true;video.preload='metadata';video.src=assetURL(ref.file);video.poster=assetURL(ref.poster);video.setAttribute('aria-label',ref.title);video.style.cssText='width:100%;height:min(53vh,535px);object-fit:contain;background:#241d18';host.prepend(video);}
  else{image.src=assetURL(ref.file);image.alt=ref.title;}
  $('#ref-title').textContent=String(index+1).padStart(2,'0')+' / '+ref.title;$('#ref-filename').textContent=ref.original;
  $$('.ref-item').forEach((b,i)=>{b.classList.toggle('active',i===index);b.setAttribute('aria-pressed',String(i===index));});
  $('#reference-dialog').dataset.index=index;
}
refs.forEach((ref,index)=>{const button=document.createElement('button');button.className='ref-item';button.setAttribute('aria-label',ref.title+(ref.video?'，视频':''));button.innerHTML=`<img src="${assetURL(ref.poster||ref.file)}" alt="" loading="lazy"><span>${ref.video?'▶ ':String(index+1).padStart(2,'0')+' '}${ref.title}</span>`;button.onclick=()=>showReference(index);$('#reference-list').append(button);});
function openReferences(index){showReference(index);$('#reference-dialog').showModal();}
$('#gallery-open').onclick=()=>openReferences(3);
$('#reference-open').onclick=()=>openReferences(views[activeView].reference);
$('#about-open').onclick=()=>$('#about-dialog').showModal();
$('#stage-about').onclick=()=>$('#about-dialog').showModal();
$$('[data-close]').forEach(b=>b.onclick=()=>b.closest('dialog').close());
$$('dialog').forEach(dialog=>{dialog.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});dialog.addEventListener('close',()=>dialog.querySelector('video')?.pause());});
$('#reference-dialog').addEventListener('keydown',e=>{if(e.target.tagName==='VIDEO')return;if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();const i=Number($('#reference-dialog').dataset.index);showReference((i+(e.key==='ArrowRight'?1:-1)+refs.length)%refs.length);}});
$$('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));
$('#roof-toggle').onclick=()=>setRoof(!roofHidden);
$('#rotate-toggle').onclick=()=>{transition=null;setAutoRotate(!controls?.autoRotate);};
$('#reset-view').onclick=()=>{setView(activeView);toast('已回到该区域的初始视角');};
$('#fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await stage.requestFullscreen();}catch{toast('当前浏览器暂不支持全屏');}};
document.addEventListener('fullscreenchange',()=>{$('#fullscreen').textContent=document.fullscreenElement?'退出全屏 ↙':'全屏 ↗';});
viewport.addEventListener('keydown',e=>{
  if(!camera||!controls)return;
  if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','-','=','Home'].includes(e.key))return;e.preventDefault();transition=null;userMoved=true;
  if(e.key==='Home'){setView(activeView);return;}
  const offset=camera.position.clone().sub(controls.target),spherical=new THREE.Spherical().setFromVector3(offset);
  if(e.key==='ArrowLeft')spherical.theta-=.1;if(e.key==='ArrowRight')spherical.theta+=.1;
  if(e.key==='ArrowUp')spherical.phi-=.08;if(e.key==='ArrowDown')spherical.phi+=.08;
  if(e.key==='+'||e.key==='=')spherical.radius*=.9;if(e.key==='-')spherical.radius*=1.1;
  spherical.phi=THREE.MathUtils.clamp(spherical.phi,.035,Math.PI/2-.03);spherical.radius=THREE.MathUtils.clamp(spherical.radius,.8,60);
  camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(spherical));controls.update();
});

function showError(message){failed=true;loader.classList.add('load-error');loader.innerHTML=`<div class="loader-brand">UBowl</div><p>${message}</p><button id="error-reload">重新加载空间</button><button id="error-photos">查看实拍资料</button><a href="${assetURL('UBowl_store.glb')}" download>下载 3D 模型</a>`;$('#error-reload').onclick=()=>location.reload();$('#error-photos').onclick=()=>openReferences(3);$$('.stage-tools button').forEach(b=>b.disabled=true);}
function init(){
  scene=new THREE.Scene();scene.background=new THREE.Color('#e9e5db');
  camera=new THREE.PerspectiveCamera(38,1,.05,120);
  renderer=new THREE.WebGLRenderer({antialias:true,alpha:false,powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=.95;
  renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFShadowMap;
  viewport.appendChild(renderer.domElement);
  renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();showError('图形显示已暂停，请重新加载。');});
  controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;controls.dampingFactor=.075;
  controls.maxPolarAngle=Math.PI/2-.03;controls.minPolarAngle=.035;controls.minDistance=.8;controls.maxDistance=60;
  controls.autoRotateSpeed=.65;controls.zoomSpeed=.7;controls.panSpeed=.7;controls.target.set(0,1.25,-.7);
  controls.addEventListener('start',()=>{transition=null;userMoved=true;setAutoRotate(false);});
  const pmrem=new THREE.PMREMGenerator(renderer),environment=new RoomEnvironment();
  scene.environment=pmrem.fromScene(environment,.04).texture;scene.environmentIntensity=.55;environment.dispose();pmrem.dispose();
  scene.add(new THREE.HemisphereLight('#fff1d9','#9e8c76',1.25));
  const sun=new THREE.DirectionalLight('#fff2d9',2.5);sun.position.set(-4,10,7);sun.castShadow=true;sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-9;sun.shadow.camera.right=9;sun.shadow.camera.top=8;sun.shadow.camera.bottom=-8;sun.shadow.camera.near=.5;sun.shadow.camera.far=35;sun.shadow.normalBias=.025;sun.shadow.bias=-.0002;scene.add(sun);
  const fill=new THREE.DirectionalLight('#fff8ed',.9);fill.position.set(8,4,4);scene.add(fill);
  const ground=new THREE.Mesh(new THREE.PlaneGeometry(200,200),new THREE.ShadowMaterial({color:'#68533e',opacity:.18}));ground.rotation.x=-Math.PI/2;ground.position.y=-.24;ground.receiveShadow=true;scene.add(ground);
  setView(views[location.hash.slice(1)]?location.hash.slice(1):'overview',false);
  new ResizeObserver(()=>{const w=viewport.clientWidth,h=viewport.clientHeight;if(w&&h){camera.aspect=w/h;camera.updateProjectionMatrix();renderer.setSize(w,h);if(!userMoved&&!controls.autoRotate){transition=null;const pose=viewPose(activeView);camera.position.copy(pose.pos);controls.target.copy(pose.target);controls.update();}}}).observe(viewport);
  document.addEventListener('visibilitychange',()=>{isVisible=!document.hidden;});
  const manager=new THREE.LoadingManager();manager.onError=url=>console.warn('Asset failed:',url);
  const gltfLoader=new GLTFLoader(manager);
  gltfLoader.load(assetURL('UBowl_store.glb'),gltf=>{
    model=gltf.scene;let triangles=0,meshes=0;
    model.traverse(object=>{if(object.isMesh){meshes++;triangles+=(object.geometry.index?.count||object.geometry.attributes.position.count)/3;object.castShadow=true;object.receiveShadow=true;const materials=Array.isArray(object.material)?object.material:[object.material];materials.forEach(mat=>{if(mat.map)mat.map.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());});}});
    scene.add(model);modelBounds=new THREE.Box3().setFromObject(model);setRoof(roofHidden);hasLoaded=true;if(!userMoved){const pose=viewPose(activeView);camera.position.copy(pose.pos);controls.target.copy(pose.target);controls.update();}$('#load-progress').style.width='100%';loader.classList.add('hidden');
    window.__ubowl={loaded:true,meshes,triangles:Math.round(triangles),bounds:new THREE.Box3().setFromObject(model).getSize(new THREE.Vector3()).toArray(),version:'1.3.0'};
    $('#model-meta').textContent='实拍还原 / V1.3';
  },progress=>{if(progress.total){const percent=Math.round(progress.loaded/progress.total*100);$('#load-progress').style.width=percent+'%';$('#load-label').textContent='正在打开店铺空间 · '+percent+'%';}},error=>{console.error('Model loading failed',error);showError('空间暂时未能加载，请重试或先查看实拍资料。');});
  function frame(time){requestAnimationFrame(frame);if(!isVisible||failed)return;const delta=Math.min((time-lastTime)/1000,.1);lastTime=time;
    if(transition){const t=Math.min((time-transition.start)/transition.duration,1),ease=t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;camera.position.lerpVectors(transition.fromPosition,transition.position,ease);controls.target.lerpVectors(transition.fromTarget,transition.target,ease);if(t===1)transition=null;}
    controls.update(delta);renderer.render(scene,camera);
  }requestAnimationFrame(frame);
  window.addEventListener('hashchange',()=>{if(views[location.hash.slice(1)])setView(location.hash.slice(1));});
}
try{init();}catch(error){console.error(error);showError('当前浏览器无法显示 3D，可查看实拍资料或下载模型。');}
