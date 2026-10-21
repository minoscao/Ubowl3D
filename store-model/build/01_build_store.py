"""UBowl observed-store reconstruction. Re-runnable owner-tagged bpy build.
Metres, Z up, -Y storefront. All dimensions are inferred from 0.15 m tile proxy.
Run: blender -b --python store-model/build/01_build_store.py
"""
import bpy, bmesh, math, random, json, sys, os
from pathlib import Path
from mathutils import Vector, Matrix
from math import sin, cos, pi
ROOT=Path(__file__).resolve().parents[1]
TEX=ROOT/'textures'; random.seed(31)
OWNER='UBowl_reconstruction_v1'
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
scene['construction_v2']=True
COL={}
for name in ['REF','HIGH','LOW','RIG_CTRL','RIG_DEF','COLLISION','SOCKETS','EXPORT','LIGHTS']:
    col=bpy.data.collections.new(name);scene.collection.children.link(col);COL[name]=col
bpy.context.preferences.filepaths.save_version=0
M={}
def mat(name,color,rough=.45,metal=0,emit=0,alpha=1,texture=None,normal=False):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,alpha)
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,alpha)
    p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
    p.inputs['Alpha'].default_value=alpha
    if emit:
        p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
    if texture:
        t=m.node_tree.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(str(TEX/texture),check_existing=True)
        m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color'])
        if emit: m.node_tree.links.new(t.outputs['Color'],p.inputs['Emission Color'])
    if normal:
        t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(TEX/'ceramic-normal.png'),check_existing=True);t.image.colorspace_settings.name='Non-Color'
        n=m.node_tree.nodes.new('ShaderNodeNormalMap');n.inputs['Strength'].default_value=.5
        m.node_tree.links.new(t.outputs['Color'],n.inputs['Color']);m.node_tree.links.new(n.outputs['Normal'],p.inputs['Normal'])
    if alpha<1:
        m.surface_render_method='DITHERED';p.inputs['IOR'].default_value=1.45
    M[name]=m;return m
mat('grout',(0.22,.19,.155),.82)
mat('tile_base',(.061,.016,.007),.2)
for i in range(7):
    f=.82+i*.057;mat('tile_'+str(i),(.062*f,.021*f,.011*f),.16+i*.018,normal=True)
mat('red',(.23,.026,.013),.3);mat('red_dark',(.14,.012,.008),.27)
mat('inferred_wall',(.15,.135,.115),.83)
mat('ivory',(.9,.88,.8),.42);mat('luminous_cream',(1,.74,.38),.38,emit=.6)
mat('amber',(1,1,1),.25,texture='amber.jpg');mat('terrazzo',(1,1,1),.7,texture='terrazzo.jpg')
mat('stone',(.19,.18,.155),.85);mat('slab_edge',(.115,.104,.085),.85)
mat('charcoal',(.014,.019,.021),.38);mat('rubber',(.008,.01,.011),.75)
mat('steel',(.50,.54,.56),.28,.83);mat('steel_dark',(.20,.23,.25),.36,.75)
mat('gold',(.73,.48,.12),.25,.86);mat('gold_edge',(.89,.64,.24),.20,.88)
mat('glass',(.45,.67,.70),.13,.25,alpha=.19)
mat('kitchen_glass',(.19,.27,.28),.23,.4,alpha=.54)
mat('white',(1,.96,.83),.33);mat('white_sign',(1,.94,.78),.30,emit=.65)
mat('screen_menu',(1,1,1),.55,emit=.65,texture='menu.jpg')
mat('screen_pickup',(1,1,1),.55,emit=.65,texture='pickup.jpg')
mat('screen_terminal',(1,1,1),.46,emit=.5,texture='terminal-clean.jpg')
mat('led',(1,1,1),.4,emit=1.2,texture='led.jpg')
mat('price_sign',(1,1,1),.6,texture='price.jpg');mat('steps_sign',(1,1,1),.6,texture='steps.jpg')
mat('blue_digits',(.13,.64,1),.3,emit=2);mat('paper',(.94,.9,.8),.72)
mat('leaf_green',(.10,.26,.04),.7);mat('leaf_light',(.27,.46,.08),.65)
mat('food_cream',(.76,.64,.37),.65);mat('food_salmon',(.69,.25,.13),.53);mat('food_brown',(.29,.09,.028),.6)
mat('flower_red',(.61,.012,.018),.65);mat('flower_yellow',(.92,.40,.016),.6);mat('flower_pink',(.69,.21,.34),.63)
def mesh(name,verts,faces,material='ivory',collection='LOW',uv=True,uvscale=1,ids=None):
    me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);COL[collection].objects.link(ob);ob['owner']=OWNER
    mats=material if isinstance(material,list) else [material]
    for mn in mats:me.materials.append(M[mn])
    if ids:
        for p,i in zip(me.polygons,ids):p.material_index=i
    if uv:
        lay=me.uv_layers.new(name='UVMap')
        for poly in me.polygons:
            n=poly.normal;ax=max(range(3),key=lambda k:abs(n[k]));coords=[i for i in range(3) if i!=ax]
            for li in poly.loop_indices:
                co=me.vertices[me.loops[li].vertex_index].co;lay.data[li].uv=(co[coords[0]]*uvscale,co[coords[1]]*uvscale)
    return ob
def box(name,loc,size,material='ivory',bevel=0,rot=None):
    x,y,z=[v/2 for v in size]
    verts=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    ob=mesh(name,verts,faces,material);ob.location=loc
    if rot:ob.rotation_euler=rot
    if bevel:
        mod=ob.modifiers.new('manufactured_edge','BEVEL');mod.width=bevel;mod.segments=1
        mod=ob.modifiers.new('weighted_normals','WEIGHTED_NORMAL')
    return ob
def plane(name,loc,width,height,material,rot=(pi/2,0,0)):
    ob=mesh(name,[(-width/2,-height/2,0),(width/2,-height/2,0),(width/2,height/2,0),(-width/2,height/2,0)],[(0,1,2,3)],material,uv=False)
    uv=ob.data.uv_layers.new(name='UVMap')
    for li,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[li].uv=co
    ob.location=loc;ob.rotation_euler=rot;return ob
def lathe(name,profile,loc,material='steel',n=24):
    vs=[];fs=[]
    for r,z in profile:
        for k in range(n):vs.append((r*cos(2*pi*k/n),r*sin(2*pi*k/n),z))
    for j in range(len(profile)-1):
        for k in range(n):a=j*n+k;b=j*n+(k+1)%n;fs.append((a,b,b+n,a+n))
    ob=mesh(name,vs,fs,material);ob.location=loc
    for p in ob.data.polygons:p.use_smooth=True
    return ob
def cyl(name,loc,r,depth,material='steel',n=20):
    return lathe(name,[(0,-depth/2),(r,-depth/2),(r,depth/2),(0,depth/2)],loc,material,n)
def tube(name,points,r,material='steel',sides=8):
    vs=[];fs=[]
    for i,co in enumerate(points):
        tangent=Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])
        tangent.normalize();up=Vector((0,0,1)) if abs(tangent.z)<.95 else Vector((0,1,0));a=tangent.cross(up).normalized();b=tangent.cross(a).normalized()
        for k in range(sides):vs.append(Vector(co)+r*(cos(2*pi*k/sides)*a+sin(2*pi*k/sides)*b))
    for i in range(len(points)-1):
        for k in range(sides):q=i*sides+k;v=i*sides+(k+1)%sides;fs.append((q,v,v+sides,q+sides))
    fs.extend([tuple(reversed(range(sides))),tuple(range((len(points)-1)*sides,len(points)*sides))])
    ob=mesh(name,vs,fs,material)
    for p in ob.data.polygons:p.use_smooth=True
    return ob
FONT=bpy.data.fonts.load('C:/Windows/Fonts/arialbd.ttf')
def text(name,body,loc,size,material='white_sign',width=None,rotation=(pi/2,0,0),extrude=.012):
    data=bpy.data.curves.new(name,'FONT');data.body=body;data.font=FONT;data.size=size;data.extrude=extrude;data.bevel_depth=.001;data.bevel_resolution=0;data.resolution_u=5;data.align_x='CENTER';data.align_y='CENTER'
    ob=bpy.data.objects.new(name,data);COL['LOW'].objects.link(ob);ob.location=loc;ob.rotation_euler=rotation;ob.data.materials.append(M[material]);ob['owner']=OWNER
    bpy.context.view_layer.update()
    if width and ob.dimensions.x>width:ob.scale.x*=width/ob.dimensions.x
    return ob
def tiled(name,origin,w,h,axis='front',pitch=.15):
    # Glazed individual tile faces with chamfered relief; common 150 mm inferred module.
    verts=[];faces=[];ids=[];uvs=[]
    nx=round(w/pitch);nz=round(h/pitch);tw=w/nx;th=h/nz
    for row in range(nz):
        for col in range(nx):
            a=col*tw+.002;b=row*th+.002; ww=tw-.004;hh=th-.004
            rings=[[(a,b),(a+ww,b),(a+ww,b+hh),(a,b+hh)],[(a+.004,b+.004),(a+ww-.004,b+.004),(a+ww-.004,b+hh-.004),(a+.004,b+hh-.004)]]
            st=len(verts)
            for ri,ring in enumerate(rings):
                for u,v in ring:
                    dep=-.004-ri*.004
                    if axis=='front':p=(origin[0]+u,origin[1]+dep,origin[2]+v)
                    elif axis=='side':p=(origin[0]-dep,origin[1]+u,origin[2]+v)
                    elif axis=='top':p=(origin[0]+u,origin[1]+v,origin[2]-dep)
                    verts.append(p)
            tilefaces=[(st,st+1,st+5,st+4),(st+1,st+2,st+6,st+5),(st+2,st+3,st+7,st+6),(st+3,st,st+4,st+7),(st+4,st+5,st+6,st+7)]
            faces.extend(tilefaces);ids.extend([random.randrange(7)]*5)
    ob=mesh(name,verts,faces,['tile_'+str(i) for i in range(7)],ids=ids)
    # Normal map texture repeats at one tile, rather than across the entire facade.
    for p in ob.data.polygons:
        for li in p.loop_indices:
            c=ob.data.vertices[ob.data.loops[li].vertex_index].co
            if axis=='front':co=(c.x/pitch,c.z/pitch)
            elif axis=='side':co=(c.y/pitch,c.z/pitch)
            else:co=(c.x/pitch,c.y/pitch)
            ob.data.uv_layers.active.data[li].uv=co
    return ob
def add_light(name,loc,power,size,color,target):
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=color
    ob=bpy.data.objects.new(name,d);COL['LIGHTS'].objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();return ob

# 02 primary architectural forms. Width 9.0 m, height 3.35 m and depth 3.8 m inferred.
box('floor_foundation',(.35,1.0,-.12),(10.0,4.6,.22),'slab_edge',.045)
box('floor_shop_terrazzo',(.35,1.3,.008),(9.7,3.4,.025),'terrazzo')
for i in range(16):
    for j in range(2):box(f'floor_forecourt_{i}_{j}',(-4.35+i*.62,-.68-j*.60,.016),(.613,.592,.03),'stone',.003)
box('inferred_back_wall',(-.875,3.05,1.60),(7.25,.15,3.2),'inferred_wall',.015)
box('entry_back_red_wall',(3.975,3.05,1.60),(2.45,.15,3.2),'red',.015)
box('inferred_left_shell',(-4.49,1.56,1.64),(.12,3.05,3.28),'red',.01)
box('inferred_right_shell',(5.17,1.68,1.64),(.12,2.81,3.28),'red',.01)
# Long cashier/condiment counter across storefront; nine-ish tile courses, 1.05 m height.
box('counter_grout_core',(-.9,.0,.53),(7.2,.80,1.06),'grout',.004)
tiled('counter_front_glazed_tiles',(-4.5,-.402,.006),7.2,1.05)
tiled('counter_right_glazed_tiles',(2.706,-.40,.006),.80,1.05,'side')
tiled('counter_top_glazed_tiles',(-4.5,-.40,1.061),7.2,.80,'top')
box('counter_kick_shadow',(-.9,-.413,.035),(7.2,.014,.058),'red_dark')
box('counter_top_edge',(-.9,-.416,1.066),(7.21,.015,.021),'tile_base',.004)
# Left brand pier. The forward return is observed; exact extrusion depth is inferred.
box('brand_pier_grout',(-3.83,.77,1.685),(1.35,.91,3.37),'grout')
tiled('brand_pier_front_tiles',(-4.50,.31,0),1.35,3.35)
tiled('brand_pier_return_tiles',(-3.149,.31,0),.99,2.45,'side')
text('brand_primary_letters','U Bowl',(-3.825,.285,2.70),.42,width=1.16,extrude=.023)
text('brand_secondary_letters','Mālatāng',(-3.825,.284,2.38),.185,width=1.1,extrude=.014)
# Back tiled wall, with true open serving window and kitchen door.
box('backwall_lower',(-.5475,1.37,.65),(5.195,.12,1.30),'grout')
tiled('backwall_lower_tiles',(-3.145,1.304,.0),5.195,1.30)
box('backwall_right',(1.35,1.37,1.86),(1.40,.12,1.12),'grout')
tiled('backwall_right_tiles',(.65,1.304,1.30),1.40,1.12)
# Preserve downstream fixture/food/flower random choices from the original
# build; exactly 71 fewer tile material draws occur after this width correction.
for _ in range(71):random.randrange(7)
box('backwall_header',(-1.255,1.37,2.36),(3.81,.12,.14),'red_dark')
box('door_jamb',(-2.55,1.30,1.56),(.12,.14,1.90),'red',.01)
box('door_open_leaf',(-2.91,1.59,1.22),(.72,.047,2.38),'red',.008,rot=(0,0,-.50))
for z in [.48,1.9]:cyl('door_hinge_'+str(z),(-2.55,1.28,z),.012,.085,'steel',12)
# Serving opening frame: [ -2.43, .65 ] / z1.3..2.33, menu upper row.
for x in [-2.43,.65]:box('service_vertical_'+str(x),(x,1.294,1.78),(.038,.083,1.03),'red_dark',.004)
for z in [1.30,1.85,2.35]:box('service_horizontal_'+str(z),(-.89,1.286,z),(3.11,.09,.036),'red_dark',.003)
box('service_stainless_sill',(-.9,1.24,1.306),(3.14,.23,.032),'steel',.009)
plane('service_glass_left',(-1.66,1.31,1.58),1.51,.48,'kitchen_glass')
plane('service_glass_right',(-.12,1.31,1.58),1.51,.48,'kitchen_glass')
box('service_center_mullion',(-.89,1.278,1.59),(.018,.024,.55),'steel')
box('inferred_kitchen_passbench',(-.85,1.79,1.14),(3.2,.55,.08),'steel')
box('inferred_kitchen_stainless_back',(-.85,2.05,1.7),(3.1,.06,1.1),'steel_dark')
for i in range(4):box(f'inferred_kitchen_tray_{i}',(-2+i*.65,1.83,1.22),(.45,.3,.05),'steel',.018)
for x,tex,n in [(-1.66,'screen_pickup','pickup'),(-.12,'screen_menu','menu')]:
    box('display_'+n+'_housing',(x,1.253,2.087),(1.51,.081,.847),'charcoal',.008)
    plane('display_'+n+'_content',(x,1.209,2.087),1.454,.793,tex)
    cyl('display_'+n+'_led',(x+.68,1.201,1.684),.003,.005,'blue_digits',8)

# 03 illuminated canopy: shallow quarter vault, red structural ribs, sculpted side returns.
def canopy_surface(name,x0,x1):
    vs=[];fs=[];steps=24
    for x in [x0,x1]:
        for i in range(steps+1):
            t=(pi/2)*i/steps;vs.append((x,-.62+1.94*sin(t),3.205-.78*(1-cos(t))))
    for i in range(steps):fs.append((i,i+1,i+steps+2,i+steps+1))
    ob=mesh(name,vs,fs,'luminous_cream')
    mod=ob.modifiers.new('panel_thickness','SOLIDIFY');mod.thickness=.048
    for p in ob.data.polygons:p.use_smooth=True
    return ob
canopy_surface('canopy_main_luminous_vault',-3.15,2.75)
box('canopy_inferred_upper_backing',(-.20,.35,3.235),(5.90,1.94,.034),'ivory',.006)
for k in range(6):
    x=-3.15+k*1.18;pts=[(x,-.635+1.94*sin(pi/2*i/24),3.20-.78*(1-cos(pi/2*i/24))) for i in range(25)]
    tube(f'canopy_red_rib_{k}',pts,.012,'red_dark',8)
box('canopy_front_fascia',(-.20,-.65,3.285),(5.96,.13,.28),'ivory',.014)
box('canopy_LED_frame',(-.20,-.724,3.31),(5.88,.035,.197),'charcoal',.005)
plane('canopy_LED_typography',(-.20,-.745,3.31),5.82,.169,'led')
box('canopy_rear_red_trim',(-.20,1.31,2.425),(5.96,.035,.035),'red_dark',.006)
for i in range(5):
    x=-2.75+i*1.13
    o=cyl(f'canopy_spot_bezel_{i}',(x,-.61,3.13),.038,.015,'steel',16)
    cyl(f'canopy_spot_light_{i}',(x,-.61,3.119),.028,.008,'white_sign',16)

# Right red entry arch and bowl/tong niche, as seen in entrance photo and walkthrough.
# Corrected from QT 2.3 / 2.8 / 3.3 s: wide red face is flush with service
# back wall, NOT a thin blade projecting to the cashier line. All metre values
# remain inferred. v1.4: the solid end return covers the entire left case end,
# including shelf lips at x=3.343. Case starts behind this 0.24 m deep mass.
box('entry_left_red_pier',(2.70,1.32,1.68),(1.30,.24,3.36),'red',.012)
box('entry_left_red_mass_core',(2.405,2.18,1.68),(.71,1.62,3.36),'red',.008)
# Recess accommodates the observed left ingredient case, without moving it.
box('entry_left_red_recess_header',(2.905,2.18,2.785),(.29,1.62,1.15),'red',.006)
box('entry_left_red_recess_plinth',(2.905,2.18,.32),(.29,1.62,.64),'red',.006)
box('entry_left_red_recess_rear',(2.905,2.755,1.425),(.29,.47,1.57),'red',.006)
box('entry_right_red_pier',(5.07,.015,1.66),(.26,.89,3.32),'grout')
tiled('entry_right_tile_return',(5.20,-.435,0),.90,3.30,'side')
tiled('entry_right_tile_front',(4.94,-.438,0),.26,3.3)
# Extruded arch shape in XZ with lower opening curved corners and red top fascia.
vs=[];fs=[];outline=[(2.75,3.42),(5.2,3.42),(5.2,2.49),(4.93,2.49)]
for i in range(9):
    t=(pi/2)*i/8;outline.append((4.93-.28*(1-cos(t)),2.49+.37*sin(t)))
outline.append((3.27,2.86))
for i in range(9):
    t=(pi/2)*i/8;outline.append((3.27-.26*sin(t),2.86-.37*(1-cos(t))))
outline.append((2.75,2.49))
for yy in [-.62,.65]:vs.extend([(x,yy,z) for x,z in outline])
n=len(outline);fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]
for i in range(n):j=(i+1)%n;fs.append((i,j,n+j,n+i))
mesh('canopy_entry_red_arch',vs,fs,'red')
archpath=[(3.27-.26*cos(pi/2*i/12),2.49+.37*sin(pi/2*i/12)) for i in range(13)]
archpath += [(4.65,2.86)]
archpath += [(4.65+.28*sin(pi/2*i/12),2.86-.37*(1-cos(pi/2*i/12))) for i in range(1,13)]
archvs=[(x,yy,z-.006) for yy in [-.62,.65] for x,z in archpath];an=len(archpath)
archfs=[(i,i+an,i+an+1,i+1) for i in range(an-1)]
mesh('canopy_entry_cream_arch_liner',archvs,archfs,'luminous_cream')
box('canopy_entry_ceiling',(3.96,1.27,3.19),(2.28,3.06,.08),'ivory',.012)
for yy in [.30,1.55,2.6]:
    cyl('canopy_entry_round_light_'+str(yy),(3.96,yy,3.135),.057,.022,'white_sign',24)
for yy in [.75,2.13]:
    cyl('canopy_entry_vent_'+str(yy),(3.96,yy,3.115),.18,.046,'ivory',40)
    cyl('canopy_entry_vent_shadow_'+str(yy),(3.96,yy,3.092),.152,.012,'steel_dark',32)
text('entry_back_brand','U Bowl',(3.85,2.957,2.65),.37,width=1.17,extrude=.015)
text('entry_back_subbrand','Mālatāng',(3.85,2.947,2.405),.14,width=.90,extrude=.010)

# Niche sits to the entry's right, faces front; independent bronze bowl stack and hanging tongs.
box('bowl_niche_red_back',(4.04,.455,1.36),(.69,.11,2.10),'red')
box('bowl_niche_red_header',(4.04,.18,2.11),(.69,.62,.51),'red',.014)
box('bowl_warmer_steel_body',(4.02,.145,.40),(.66,.61,.78),'steel',.025)
box('bowl_warmer_top_shadow',(4.02,.12,.797),(.61,.52,.025),'charcoal',.012)
box('bowl_niche_glass_shelf',(4.02,.10,1.155),(.63,.56,.013),'glass',.008)
tube('tong_hanging_rail',[(3.76,.105,1.77),(4.28,.105,1.77)],.010,'steel')
for i in range(12):
    x=3.78+i*.043
    tube('tong_'+str(i),[(x,.10,1.79),(x,.057,1.80),(x,-.004,1.73),(x,-.15,1.41),(x+.017,-.15,1.38),(x+.027,-.115,1.40),(x+.025,.04,1.73)],.0045,'gold',6)
def bowl(name,loc,r=.18,h=.115,material='gold',n=28):
    profile=[(0,0),(.67*r,0),(.76*r,.018),(r,h*.88),(r,h),(.96*r,h+.004),(.91*r,h*.88),(.69*r,.025),(0,.025)]
    ob=lathe(name,profile,loc,material,n)
    return ob
for col,x in enumerate([3.86,4.15]):
    for i in range(5):bowl(f'bowl_stack_{col}_{i}',(x,.10,.802+i*.030),.126,.093,n=22)
    for i in range(3):bowl(f'bowl_upper_stack_{col}_{i}',(x,.20,1.164+i*.025),.113,.085,n=22)
text('bowl_warmer_label','BOWL WARMER',(4.02,-.17,.44),.049,'red_dark',width=.5,extrude=.0003)
# Photographic correction: this is a niche ALONG the right side wall, opening
# into the aisle (-X), not a cabinet spanning the entrance and facing -Y.
oldpivot=Vector((4.02,.145,0));newpivot=Vector((4.68,.65,0))
niche_transform=Matrix.Translation(newpivot)@Matrix.Rotation(-pi/2,4,'Z')@Matrix.Translation(-oldpivot)
for ob in list(COL['LOW'].objects):
    if ob.name.startswith('bowl_') or ob.name.startswith('tong_'):ob.matrix_world=niche_transform@ob.matrix_world

# U-shaped cold ingredient display. Layout from walkthrough, exact plan depth inferred.
def tray(name,loc,sx=.25,sy=.28):
    x,y,z=loc
    box(name+'_well',(x,y,z),(sx,sy,.043),'steel_dark',.010)
    box(name+'_base',(x,y,z+.021),(sx-.025,sy-.025,.012),'steel',.008)
    for dx in [-sx/2,sx/2]:box(name+'_rimx_'+str(dx),(x+dx,y,z+.034),(.011,sy+.008,.011),'steel',.004)
    for dy in [-sy/2,sy/2]:box(name+'_rimy_'+str(dy),(x,y+dy,z+.034),(sx,.011,.011),'steel',.004)
    # Identifiable but intentionally simplified food families, not invented precise stock.
    family=random.choice(['leaf_green','leaf_light','food_cream','food_salmon','food_brown'])
    for k in range(7):
        px=x+random.uniform(-sx*.31,sx*.31);py=y+random.uniform(-sy*.31,sy*.31)
        ob=box(name+'_food_'+str(k),(px,py,z+.042+random.uniform(0,.028)),(.044,.042,.026),family,.008,rot=(random.random()*.4,random.random()*.3,random.random()*pi))
def fridge_run(prefix,x0,y0,length,rot=0):
    # Author local along X then rotate into side returns.
    before=set(bpy.data.objects)
    box(prefix+'_lower_cabinet',(0,0,.35),(length,.50,.68),'red',.02)
    box(prefix+'_plinth',(0,0,.05),(length-.035,.47,.085),'charcoal')
    box(prefix+'_cold_back',(0,.205,1.36),(length,.045,1.29),'steel',.009)
    box(prefix+'_lit_header',(0,.03,2.015),(length,.5,.28),'luminous_cream',.018)
    box(prefix+'_header_trim',(0,-.232,1.89),(length,.035,.035),'steel')
    for zz in [.75,1.10,1.45,1.78]:
        box(prefix+'_shelf_'+str(zz),(0,-.025,zz),(length,.50,.025),'steel',.006)
        box(prefix+'_front_edge_'+str(zz),(0,-.281,zz+.020),(length,.024,.063),'steel',.004)
        count=max(2,round(length/.28));step=length/count
        for k in range(count):tray(prefix+f'_tray_{zz}_{k}',(-length/2+step*(k+.5),-.025,zz+.025),step-.025,.34)
    for xx in [-length/2+.025,length/2-.025]:box(prefix+'_post_'+str(xx),(xx,-.251,1.315),(.025,.025,1.25),'steel')
    for z in [.20,.25,.30,.35,.40,.45]:box(prefix+'_vent_'+str(z),(0,-.258,z),(length*.63,.013,.012),'red_dark')
    plane(prefix+'_thermostat',(length*.34,-.266,.55),.10,.052,'charcoal')
    text(prefix+'_temperature','4°',(length*.34,-.271,.55),.035,'blue_digits',extrude=.0001)
    R=Matrix.Rotation(rot,4,'Z')
    for ob in set(bpy.data.objects)-before:
        ob.location=R@ob.location+Vector((x0,y0,0));ob.rotation_euler.rotate_axis('Z',rot)
fridge_run('ingredient_back',3.85,2.68,2.10)
# Inward-facing cold cases: local front=-Y -> left +X / right -X.
# Actual shelf lips extend 0.293 m from centre; 1.60-2*0.293=1.014 m clear.
fridge_run('ingredient_left',3.05,1.96,1.00,pi/2)
fridge_run('ingredient_right',4.65,1.85,1.22,-pi/2)

# Condiments in amber stone with recessed metal pots, cups, faucet and drip tray.
box('condiment_amber_top',(-3.00,.005,1.091),(2.86,.78,.047),'amber',.010)
box('condiment_amber_upstand',(-3.1,.30,1.258),(2.65,.095,.33),'amber',.009)
for i in range(7):
    x=-4.05+i*.28;y=-.12 if i%2==0 else .035
    cyl('condiment_pot_rim_'+str(i),(x,y,1.120),.084,.012,'steel',26)
    cyl('condiment_pot_inset_'+str(i),(x,y,1.122),.073,.013,'food_brown' if i%3 else 'leaf_green',24)
    tube('condiment_spoon_'+str(i),[(x+.016,y,1.127),(x+.055,y+.08,1.25)],.005,'steel',6)
box('condiment_drain',(-1.84,-.055,1.119),(.35,.32,.009),'steel',.006)
for i in range(11):box('drain_slot_'+str(i),(-1.975+i*.027,-.055,1.125),(.010,.27,.002),'charcoal')
tube('condiment_faucet',[(-1.86,.15,1.12),(-1.86,.15,1.38),(-1.86,.10,1.43),(-1.86,-.035,1.43),(-1.86,-.075,1.39)],.014,'steel',12)
for j,x in enumerate([-3.86,-3.55,-3.28]):
    for i in range(8-j):lathe(f'paper_cup_stack_{j}_{i}',[(.032,0),(.042,.085),(.038,.087),(.029,.005)],(x,.225,1.426+i*.011),'paper',18)
for i in range(5):box('condiment_sachet_'+str(i),(-4.15+i*.095,.23,1.48),(.074,.045,.18),'red',.004,rot=(0,-.1,.10))

# Two self-weigh checkout terminals with tilted screens, receipt body and adjacent scales.
def terminal(prefix,x):
    box(prefix+'_base',(x,-.095,1.115),(.29,.34,.071),'ivory',.021)
    # Screen upper edge leans backwards: tilt 24 degrees from upright.
    theta=math.radians(-24);rot=(theta,0,0)
    body=box(prefix+'_white_casing',(x,-.261,1.38),(.303,.07,.58),'ivory',.025,rot)
    bezel=box(prefix+'_black_bezel',(x,-.301,1.385),(.271,.014,.475),'charcoal',.015,rot)
    screen=plane(prefix+'_screen',(x,-.310,1.387),.248,.438,'screen_terminal',rot=(pi/2+theta,0,0))
    # Correct face tilt by shared local translation offset, screen sits in front of casing.
    box(prefix+'_receipt_body',(x,-.45,1.044),(.268,.10,.19),'ivory',.014,rot=(theta,0,0))
    box(prefix+'_receipt_slot',(x,-.507,1.032),(.11,.008,.012),'charcoal',.002)
    box(prefix+'_card_reader',(x+.075,-.51,1.02),(.050,.014,.069),'charcoal',.004)
    box(prefix+'_rear_support',(x,.0,1.30),(.24,.13,.27),'ivory',.025,rot=(0,0,0))
    text(prefix+'_card_only','Card Only',(x,-.198,1.738),.047,'red',width=.29,extrude=.0003)
    box(prefix+'_card_sign',(x,-.177,1.735),(.318,.015,.108),'paper',.003)
    # readable lettering placed slightly in front of little paper sign
    for ob in [bpy.data.objects.get(prefix+'_card_only')]:ob.location.y=-.192
    sx=x+.49
    box(prefix+'_scale_base',(sx,-.038,1.132),(.43,.37,.089),'charcoal',.014)
    box(prefix+'_scale_tray',(sx,-.038,1.184),(.439,.374,.021),'steel',.012)
    plane(prefix+'_scale_display',(sx,-.230,1.132),.139,.038,'charcoal')
    text(prefix+'_scale_digits','0.000',(sx,-.236,1.132),.031,'blue_digits',extrude=.0001)
    bowl(prefix+'_weighing_bowl',(sx,-.02,1.199),.177,.103)
    for sign in [-1,1]:
        pts=[(sx+sign*.165,-.05,1.269),(sx+sign*.214,-.05,1.295),(sx+sign*.220,.01,1.295),(sx+sign*.165,.01,1.269)]
        tube(prefix+'_bowl_handle_'+str(sign),pts,.006,'gold_edge',8)
    for i in range(5):box(prefix+'_bowl_contents_'+str(i),(sx+random.uniform(-.10,.10),-.02+random.uniform(-.08,.08),1.277),(.08,.055,.015),'leaf_green' if i%2 else 'food_cream',.01,rot=(.3,.1,random.random()*pi))
terminal('checkout_left',-.48)
terminal('checkout_right',.79)
# Staff POS and service tray.
box('staff_POS_base',(-1.25,.03,1.109),(.25,.22,.035),'charcoal',.008)
tube('staff_POS_arm',[(-1.25,.03,1.12),(-1.25,.10,1.37)],.026,'charcoal',10)
box('staff_POS_monitor',(-1.25,.075,1.49),(.38,.048,.26),'charcoal',.010,rot=(math.radians(-14),0,0))
box('pickup_tray',(-1.27,-.17,1.123),(.46,.31,.024),'amber',.020)
lathe('pickup_plate',[(0,0),(.11,0),(.147,.014),(.15,.025),(.14,.030),(.11,.009),(0,.009)],(-1.27,-.17,1.137),'paper',32)
box('tong_case',(0.30,.14,1.182),(.45,.20,.15),'glass',.005)
for i in range(8):tube('spare_tong_'+str(i),[(.1+i*.045,.07,1.19),(.1+i*.045,.23,1.24),(.112+i*.045,.23,1.245)],.004,'gold',6)
# Thermoses and cups on service end.
box('drink_service_tray',(2.055,-.025,1.104),(.73,.42,.035),'amber',.017)
for i in range(3):
    x=1.83+i*.225
    lathe('drink_thermos_'+str(i),[(.058,0),(.074,.04),(.064,.235),(.04,.285),(.038,.30)],(x,.10,1.123),'steel',26)
    lathe('drink_thermos_lid_'+str(i),[(.046,0),(.044,.056),(.021,.061)],(x,.10,1.408),'charcoal',22)
    tube('drink_thermos_spout_'+str(i),[(x,.07,1.447),(x,-.004,1.438)],.012,'charcoal',8)
for i in range(4):lathe('drink_paper_cup_'+str(i),[(.025,0),(.035,.07),(.032,.073),(.022,.006)],(1.82+i*.14,-.18,1.125),'paper',18)
for i,(x,tex) in enumerate([(2.21,'price_sign'),(2.51,'steps_sign')]):
    box('menu_counter_holder_'+str(i),(x,-.02,1.319),(.279,.025,.38),'glass',.003)
    plane('menu_counter_paper_'+str(i),(x,-.039,1.319),.262,.359,tex)
# Six paperwork notices on red wall, observed placement but illegible body simplified.
for row in range(2):
    for col in range(3):
        x=2.235+col*.235;z=2.095-row*.33
        box(f'wall_notice_{row}_{col}',(x,1.188,z),(.205,.016,.285),'paper',.002)
        for k in range(4):box(f'wall_notice_rule_{row}_{col}_{k}',(x,1.178,z+.055-k*.035),(.155,.002,.006),'red_dark')

# Temporary opening flowers visible in the supplied images. No people reconstructed.
def leaf(name,a,b,w,material):
    a=Vector(a);b=Vector(b);axis=b-a;side=axis.cross(Vector((0,0,1))).normalized()*w
    if side.length<.001:side=Vector((w,0,0))
    mid=(a+b)*.5
    return mesh(name,[a,mid+side,b,mid-side,mid+Vector((0,0,.02))],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],material)
def bouquet(prefix,loc,scale=1):
    x,y,z=loc
    lathe(prefix+'_red_vase',[(.09*scale,0),(.11*scale,.20*scale),(.065*scale,.30*scale)],loc,'red',24)
    for i in range(23):
        ang=random.random()*2*pi;r=random.uniform(.04,.24)*scale;h=random.uniform(.31,.60)*scale
        end=(x+cos(ang)*r,y+sin(ang)*r,z+h)
        tube(prefix+'_stem_'+str(i),[(x,y,z+.18*scale),end],.002*scale,'gold',5)
        leaf(prefix+'_leaf_'+str(i),(x,y,z+.23*scale),end,.04*scale,'leaf_green' if i%3 else 'flower_red')
        if i%2:
            for k in range(5):
                a=2*pi*k/5
                leaf(prefix+f'_petal_{i}_{k}',end,(end[0]+cos(a)*.045*scale,end[1]+sin(a)*.045*scale,end[2]+.025*scale),.026*scale,'flower_red' if i%3 else 'flower_yellow')
    for i in range(7):
        a=i*2*pi/7
        leaf(prefix+'_wrap_'+str(i),(x,y,z+.15*scale),(x+cos(a)*.21*scale,y+sin(a)*.21*scale,z+.34*scale),.08*scale,'flower_red')
bouquet('opening_counter_flowers',(-1.87,.25,1.125),.9)
bouquet('opening_left_flowers',(-4.26,-.70,.40),1.65)
for x in [-4.45,-4.08]:tube('flower_stand_'+str(x),[(x,-.68,.025),(-4.26,-.7,.58)],.016,'red_dark',8)

# 04 Master retains bevel modifiers and editable text. Evaluated copies, identity
# transforms and semantic consolidation are created by 02_export_review.py.
print('GEOMETRY_COMPLETE',len(COL['LOW'].objects),flush=True)

# 05 material and proportion review setup; environment is deliberately neutral.
world=bpy.data.worlds.new('review_world');scene.world=world
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.31,.30,.27,1);bg.inputs['Strength'].default_value=.55
add_light('review_key',(-4,-6,8),1700,7,(1,.83,.67),(0,.5,1.4))
add_light('review_fill',(5,-4,5),1200,6,(.78,.88,1),(0,1,1.2))
add_light('review_back',(0,3.0,6.5),1000,5,(1,.77,.47),(0,.4,1.2))
add_light('canopy_softlight',(-.3,.25,2.90),160,5.5,(1,.68,.34),(-.3,.0,.7))
add_light('ingredient_softlight',(3.5,1.7,2.85),70,1.4,(1,.87,.57),(3.5,1.8,.8))
d=bpy.data.cameras.new('review_camera');camera=bpy.data.objects.new('review_camera',d);COL['REF'].objects.link(camera);scene.camera=camera
camera.location=(10,-13,8);camera.rotation_euler=(Vector((0,.8,1.45))-camera.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=12.0;d.lens=45
try:scene.render.engine='BLENDER_EEVEE'
except:scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1800;scene.render.resolution_y=1250;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.film_transparent=True
scene.render.image_settings.color_mode='RGBA';scene.view_settings.view_transform='AgX'
scene.render.filepath=str(ROOT/'review'/'overview.png')
scene.render.fps=30
for img in bpy.data.images:
    if img.filepath:img.pack()
if '--candidate' in sys.argv:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'review'/'UBowl_candidate.blend'))
    print('CANDIDATE_SAVED_NO_EXPORT',flush=True)
    sys.exit(0)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'UBowl_master.blend'))

# 09 GLB contains selected architectural meshes and editable text converted by exporter.
bpy.ops.object.select_all(action='DESELECT')
for ob in COL['LOW'].objects:ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(ROOT/'UBowl_store.glb'),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials='EXPORT',export_cameras=False,export_lights=False,export_extras=True)
tris=0;verts=0
for ob in COL['LOW'].objects:
    dep=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=dep.to_mesh();me.calc_loop_triangles();tris+=len(me.loop_triangles);verts+=len(me.vertices);dep.to_mesh_clear()
info={'asset':'AR_UBowl_ObservedStore','version':'1.0','units':'meters','authoringAxes':'Z up, -Y forward','exportAxes':'Y up, +Z forward','boundsApprox_m':{'width':9.3,'depth':4.6,'height':3.54},'shopDimensionsInferred_m':{'width':9.0,'depth':3.8,'height':3.35},'meshTriangles':tris,'sourceVertices':verts,'meshObjects':len(COL['LOW'].objects),'materials':len(M),'glbBytes':(ROOT/'UBowl_store.glb').stat().st_size,'files':['UBowl_store.glb','UBowl_master.blend'],'sourcePhotos':[p.name for p in (ROOT/'ref').glob('*.jpg')],'sourceVideos':['飞书20261011-161415.mp4','飞书20261011-161419.mp4','飞书20261011-161423.mp4','飞书20261011-161426.qt'],'inferred':['All absolute dimensions use an unconfirmed 150 mm tile module; no survey dimensions supplied.','Overall store depth and U-shaped ingredient aisle plan are approximate from moving perspective video.','Opaque kitchen shell and simplified stainless equipment behind serving hatch are placeholders, not measured fixtures.','Unseen side and rear enclosure thicknesses are inferred.','Food contents are representative simplified geometry; exact stock assortment is not asserted.','Temporary opening bouquets are simplified from supplied photos.','LED ticker and tiny POS UI lettering are reconstructed from observed wording.','No customers, staff, seating or unobserved dining areas modelled.'],'observedFeatures':['Brown glazed square tile counter, backing wall and left brand pillar','Raised ivory UBowl and Malatang letterforms','Cream curved luminous canopy with red ribs and LED header','Two digital menu/order displays above glazed serving hatch','Two white tilted self-weigh checkout terminals with black scales and brass bowls','Amber condiment stone and recessed condiment pots','Red entrance arch, three-sided refrigerated ingredients display, brass tong and bowl niche'],'textureContract':{'baseColor':'sRGB','normal':'OpenGL +Y, Non-Color','roughness':'scalar','metallic':'scalar','screenTextures':'Locally rectified supplied photos; screen glare present in source','proceduralMaterials':'Original material maps generated locally; glTF compatible image textures','externalDependencies':[]},'hideCanopyPrefix':'canopy_','cameraGLTF':{'overview':{'position':[10,8,13],'target':[0,1.45,-.8]},'front':{'position':[0,2.4,14],'target':[0,1.5,-.7]},'ingredients':{'position':[7.5,4.4,6.5],'target':[3.6,1.35,-1.6]}},'validation':{'roundtrip':'pending','perspectiveReferences':'No calibrated orthographic references supplied; numeric silhouette IoU cannot establish survey accuracy.'}}
(ROOT/'asset-manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf8')
print('BUILD_COMPLETE',json.dumps({'triangles':tris,'vertices':verts,'glbMB':round(info['glbBytes']/1024/1024,2)}))
if '--no-render' not in sys.argv:
    bpy.ops.render.render(write_still=True)
    camera.location=(.0,-15,5.1);camera.rotation_euler=(Vector((0,.5,1.7))-camera.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=10.3
    scene.render.resolution_x=1800;scene.render.resolution_y=1000;scene.render.filepath=str(ROOT/'review'/'front.png');bpy.ops.render.render(write_still=True)
    for ob in COL['LOW'].objects:
        if ob.name.startswith('canopy_'):ob.hide_render=True
    camera.location=(8,-10,9);camera.rotation_euler=(Vector((0,1.0,1.1))-camera.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=11.3
    scene.render.resolution_y=1200;scene.render.filepath=str(ROOT/'review'/'cutaway.png');bpy.ops.render.render(write_still=True)
    print('REVIEW_RENDERS_COMPLETE')
