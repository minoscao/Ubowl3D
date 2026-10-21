"""Finalize GLB draw calls and render review + fresh-import evidence.
Run after 01_build_store.py -- --no-render. Source remains individually editable.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'UBowl_master.blend'))
scene=bpy.context.scene
# One-time repair for first prototype, absent after a clean 01 build.
if not scene.get('construction_v2'):
    for prefix,x in [('checkout_left',-.48),('checkout_right',.79)]:
        for suffix,c in [('_white_casing',(x,-.261,1.38)),('_black_bezel',(x,-.301,1.385)),('_screen',(x,-.310,1.387)),('_receipt_body',(x,-.45,1.044))]:
            ob=bpy.data.objects.get(prefix+suffix)
            if ob:
                trans=Matrix.Translation(c);rot=Matrix.Rotation(math.radians(-48),4,'X')
                ob.data.transform(trans@rot@trans.inverted())
    ob=bpy.data.objects.get('counter_top_glazed_tiles')
    if ob:
        import bmesh
        bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free()
    scene['construction_v2']=True

# Export copies with evaluated geometry; preserve text and semantic parts in mother file.
col=bpy.data.collections.get('EXPORT')
for ob in list(col.objects):bpy.data.objects.remove(ob,do_unlink=True)
def group(name):
    if name=='tong_case' or name.startswith('spare_tong_'):return 'service_Props'
    if name.startswith('canopy_'):return 'canopy_Assembly'
    if name.startswith('ingredient_'):return '_'.join(name.split('_')[:2])+'_Assembly'
    if name.startswith('checkout_'):return '_'.join(name.split('_')[:2])+'_Assembly'
    for prefix,out in [('brand_','brand_Pier'),('counter_','counter_Assembly'),('bowl_','bowl_Station'),('tong_','bowl_Station'),('condiment_','condiment_Station'),('drain_','condiment_Station'),('paper_cup_','condiment_Station'),('drink_','drinks_Station'),('staff_','staff_POS'),('pickup_','service_Props'),('spare_tong_','service_Props'),('tong_case','service_Props'),('menu_counter_','counter_Signs'),('wall_notice','service_Notices'),('service_','service_Window'),('display_','service_Displays'),('backwall_','service_Backwall'),('door_','service_Door'),('entry_','entry_Assembly'),('inferred_','inferred_Shell'),('floor_','floor_Assembly'),('opening_','opening_Flowers'),('flower_','opening_Flowers')]:
        if name.startswith(prefix):return out
    return 'other_Fixtures'
groups={};dep=bpy.context.evaluated_depsgraph_get()
for ob in list(bpy.data.collections['LOW'].objects):
    ev=ob.evaluated_get(dep);me=bpy.data.meshes.new_from_object(ev,depsgraph=dep,preserve_all_data_layers=True)
    cp=bpy.data.objects.new(ob.name+'_export',me);col.objects.link(cp);me.transform(ob.matrix_world)
    cp['owner']='UBowl_export';groups.setdefault(group(ob.name),[]).append(cp)
for name,obs in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs:o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    if len(obs)>1:bpy.ops.object.join()
    ob=obs[0];ob.name=name;ob.data.name=name+'_mesh'
    bm=bmesh.new();bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.0001)
    bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.0000001)
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bm.to_mesh(ob.data);bm.free();ob.data.update()
    # Remove duplicate or unused materials without touching geometry.
    mats=[];mapping={}
    for i,m in enumerate(ob.data.materials):
        if m not in mats:mats.append(m)
        mapping[i]=mats.index(m)
    ids=[mapping[p.material_index] for p in ob.data.polygons]
    ob.data.materials.clear()
    for m in mats:ob.data.materials.append(m)
    for p,i in zip(ob.data.polygons,ids):p.material_index=i
    ob.hide_render=True;ob.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
for ob in col.objects:ob.hide_set(False);ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'UBowl_store.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True)
drawcalls=0;tri=0;verts=0
for ob in col.objects:
    me=ob.data;me.calc_loop_triangles();tri+=len(me.loop_triangles);verts+=len(me.vertices);drawcalls+=len(set(p.material_index for p in me.polygons));ob.hide_render=True;ob.hide_set(True)
manifest=json.loads((ROOT/'asset-manifest.json').read_text(encoding='utf8'))
manifest.update({'meshTriangles':tri,'exportVerticesBeforeUVSplits':verts,'meshObjects':len(col.objects),'drawCallsWithoutShadows':drawcalls,'glbBytes':(ROOT/'UBowl_store.glb').stat().st_size})
manifest['cameraGLTF']['counter']={'position':[4,3.3,7],'target':[0,1.15,0]}
manifest['cameraGLTF']['overview']={'position':[7.8,4.8,12],'target':[0,1.35,-.7]}
manifest['cameraGLTF']['ingredients']={'position':[3.85,1.65,.6],'target':[3.85,1.40,-2.95]}
inference='Luminous canopy upper backing panel is an inferred hidden construction closure; underside shape follows photographed vault.'
if inference not in manifest['inferred']:manifest['inferred'].append(inference)
(ROOT/'asset-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'UBowl_master.blend'))
print('OPTIMIZED_EXPORT',json.dumps({'tri':tri,'mesh':len(col.objects),'drawcalls':drawcalls,'glbMB':round(manifest['glbBytes']/1024/1024,2)}),flush=True)
if '--no-render' in sys.argv:sys.exit(0)
camera=scene.camera
scene.render.resolution_x=1600;scene.render.resolution_y=1100
scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
# High resolution material review.
camera.location=(7.8,-12,4.8);camera.rotation_euler=(Vector((.35,.7,1.35))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=12.0
scene.render.filepath=str(ROOT/'review'/'overview.png');bpy.ops.render.render(write_still=True)
camera.location=(.35,-15,4.30);camera.rotation_euler=(Vector((.35,.5,1.64))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=11.0
scene.render.resolution_y=900;scene.render.filepath=str(ROOT/'review'/'front.png');bpy.ops.render.render(write_still=True)
# Requested geometry correction review: eye-level portrait around the red mass.
camera.data.type='PERSP';camera.data.lens=24;camera.data.sensor_fit='VERTICAL';camera.data.sensor_height=36
camera.location=(3.4,-.7,1.65);camera.rotation_euler=(Vector((2.85,1.45,1.40))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.resolution_x=720;scene.render.resolution_y=1280;scene.render.filepath=str(ROOT/'review'/'partition-corrected.png');bpy.ops.render.render(write_still=True)
# Approximate actual walkthrough at 3.8 seconds: eye at aisle centre, not outside
# the right wall looking diagonally through the bowl cabinet.
camera.location=(3.85,-.6,1.65);camera.rotation_euler=(Vector((3.85,2.95,1.40))-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=str(ROOT/'review'/'entry-matched.png');bpy.ops.render.render(write_still=True)
camera.data.type='ORTHO';camera.data.sensor_fit='AUTO';scene.render.resolution_x=1600
for ob in bpy.data.collections['LOW'].objects:
    if ob.name.startswith('canopy_'):ob.hide_render=True
camera.location=(8,-10,9);camera.rotation_euler=(Vector((0,1.0,1.1))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=11.3
scene.render.resolution_y=1100;scene.render.filepath=str(ROOT/'review'/'cutaway.png');bpy.ops.render.render(write_still=True)
# True mesh-world-space clearances, including shelf lips, trim and niche glass.
def group_bounds(prefixes):
    pts=[]
    for o in bpy.data.collections['LOW'].objects:
        if any(o.name.startswith(p) for p in prefixes):
            ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get())
            pts.extend(ev.matrix_world@Vector(c) for c in ev.bound_box)
    return {'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
lb=group_bounds(['ingredient_left']);rb=group_bounds(['ingredient_right']);nb=group_bounds(['bowl_','tong_hanging_rail']+['tong_'+str(i) for i in range(12)]);pb=group_bounds(['entry_left_red_'])
clear={'unit':'metres','basis':'evaluated world-space mesh bounding boxes including trim and shelf lips','userTarget_m':1.0,'userTargetStatus':'user estimate, not surveyed','leftCase':lb,'rightCase':rb,'rightNiche':nb,'redMass':pb,'ingredientClearWidth_m':rb['min'][0]-lb['max'][0],'entranceClearWidth_m':nb['min'][0]-pb['max'][0],'leftCaseFrontDirection':'+X into aisle','rightCaseFrontDirection':'-X into aisle','nicheFrontDirection':'-X into aisle'}
clear['continuousStraightCorridor_m']=min(rb['min'][0],nb['min'][0])-max(lb['max'][0],pb['max'][0])
clear['entranceMeasurementNote']='Conservative X projection between red mass and niche; these masses do not fully overlap in Y. The continuous straight corridor is the stricter projection intersection over both entrance and ingredient segments.'
endcap=group_bounds(['entry_left_red_pier'])
clear['leftCaseEndReturn']={'wallBounds':endcap,'shelfToWallOuterEdgeMargin_m':endcap['max'][0]-lb['max'][0],'wallToCaseLongitudinalGap_m':lb['min'][1]-endcap['max'][1],'frontElevationCoversCaseEnd':endcap['min'][0]<=lb['min'][0] and endcap['max'][0]>=lb['max'][0] and endcap['min'][2]<=lb['min'][2] and endcap['max'][2]>=lb['max'][2],'wallDepth_m':endcap['max'][1]-endcap['min'][1]}
if bpy.data.objects.get('entry_right_solid_end_return'):
    rightcap=group_bounds(['entry_right_solid_end_return']);warmer=group_bounds(['bowl_warmer_'])
    clear['rightCaseEndReturn']={'wallBounds':rightcap,'userMinimumWidth_m':.60,'actualWidth_m':rightcap['max'][0]-rightcap['min'][0],'wallDepth_m':rightcap['max'][1]-rightcap['min'][1],'frontElevationCoversWarmerSide':rightcap['min'][0]<=warmer['min'][0] and rightcap['max'][0]>=warmer['max'][0] and rightcap['min'][2]<=warmer['min'][2] and rightcap['max'][2]>=warmer['max'][2],'inFrontOfWarmer':rightcap['max'][1]<warmer['min'][1]}
    clear['continuousStraightCorridor_m']=min(rb['min'][0],nb['min'][0],rightcap['min'][0])-max(lb['max'][0],pb['max'][0])
    assert clear['rightCaseEndReturn']['actualWidth_m']>=.60
    assert clear['rightCaseEndReturn']['frontElevationCoversWarmerSide'] and clear['rightCaseEndReturn']['inFrontOfWarmer']
    assert clear['continuousStraightCorridor_m']>=1.0
(ROOT/'review'/'clearance-validation.json').write_text(json.dumps(clear,indent=2),encoding='utf8')
camera.location=(3.65,1.1,12);camera.rotation_euler=(Vector((3.65,1.1,0))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=4.2
scene.render.resolution_x=1000;scene.render.resolution_y=1200;scene.render.filepath=str(ROOT/'review'/'entry-top.png');bpy.ops.render.render(write_still=True)
from bpy_extras.object_utils import world_to_camera_view
def screen(x,y):
    v=world_to_camera_view(scene,camera,Vector((x,y,3.7)));return [v.x*1000,(1-v.y)*1200]
clear['annotationPixelLines']=[{'points':[screen(lb['max'][0],1.8),screen(rb['min'][0],1.8)],'text':'%.3f m'%(clear['ingredientClearWidth_m'])},{'points':[screen(pb['max'][0],.65),screen(nb['min'][0],.65)],'text':'%.3f m'%(clear['entranceClearWidth_m'])}]
(ROOT/'review'/'clearance-validation.json').write_text(json.dumps(clear,indent=2),encoding='utf8')
print('REVIEW_COMPLETE',flush=True)

# Roundtrip: brand new scene, exported GLB alone, no source texture paths needed.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(ROOT/'UBowl_store.glb'))
scene=bpy.context.scene
obs=[o for o in scene.objects if o.type=='MESH']
tri2=sum(len(o.data.polygons) for o in obs)
missing=[];image_checks={}
for m in bpy.data.materials:
    for n in m.node_tree.nodes:
        if n.type=='TEX_IMAGE':
            im=n.image
            try:
                first_pixel=float(im.pixels[0]);valid=im.size[0]>0 and im.size[1]>0 and len(im.pixels)>0
                image_checks[im.name]={'size':list(im.size),'pixelCount':len(im.pixels),'packed':bool(im.packed_file),'firstPixel':first_pixel}
            except Exception:valid=False
            if not valid:missing.append(m.name)
allpts=[o.matrix_world@Vector(c) for o in obs for c in o.bound_box]
mn=[min(v[i] for v in allpts) for i in range(3)];mx=[max(v[i] for v in allpts) for i in range(3)]
report={'status':'pass' if not missing else 'fail','importedMeshes':len(obs),'triangles':tri2,'materials':len(bpy.data.materials),'embeddedImages':len(bpy.data.images),'missingImages':missing,'imagePixelValidation':image_checks,'boundsBlender_m':{'min':mn,'max':mx},'canopyMeshPresent':any(o.name.startswith('canopy_') for o in obs),'screenTexturePresent':any('menu' in im.name.lower() for im in bpy.data.images),'review':'roundtrip.png'}
world=bpy.data.worlds.new('roundtrip_world');scene.world=world
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.31,.30,.27,1);bg.inputs['Strength'].default_value=.65
for name,loc,power,size,color,target in [('key',(-4,-6,8),1700,7,(1,.83,.67),(0,.5,1.4)),('fill',(5,-4,5),1200,6,(.78,.88,1),(0,1,1.2)),('rear',(0,3,6.5),1000,5,(1,.77,.47),(0,.4,1.2))]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('roundtrip_camera');cam=bpy.data.objects.new('roundtrip_camera',d);scene.collection.objects.link(cam);scene.camera=cam
cam.location=(7.8,-12,4.8);cam.rotation_euler=(Vector((0,.7,1.35))-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=11.6
try:scene.render.engine='BLENDER_EEVEE'
except:scene.render.engine='BLENDER_EEVEE_NEXT'
scene.view_settings.view_transform='AgX';scene.render.resolution_x=1200;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.filepath=str(ROOT/'review'/'roundtrip.png');bpy.ops.render.render(write_still=True)
(ROOT/'review'/'roundtrip-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
manifest['validation']['roundtrip']=report
(ROOT/'asset-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print('ROUNDTRIP_COMPLETE',json.dumps(report),flush=True)
