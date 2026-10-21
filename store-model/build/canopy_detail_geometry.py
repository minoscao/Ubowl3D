"""Scoped v1.5 canopy/upper-niche construction, retaining circulation fixtures."""
import bpy, bmesh, math
from mathutils import Vector

def apply_detail():
    if bpy.context.scene.get('canopy_detail_v15'): return
    col=bpy.data.collections['LOW']
    def box(name,loc,size,mat):
        x,y,z=[a/2 for a in size]
        vs=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
        fs=[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
        me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(vs,[],fs);me.update()
        o=bpy.data.objects.new(name,me);col.objects.link(o);o.location=loc;me.materials.append(bpy.data.materials[mat])
        uv=me.uv_layers.new(name='UVMap')
        for p in me.polygons:
            axes=[i for i in range(3) if i!=max(range(3),key=lambda j:abs(p.normal[j]))]
            for li in p.loop_indices:
                co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co[axes[0]],co[axes[1]])
        o['owner']='UBowl_reconstruction_v1';return o
    # Keep this as one coherent extruded arch. The apparent red box is its left
    # end/side, not an additional floating object. Match inferred depth and rise.
    def newz(x,z):
        low=2.62 if x<3.28 else 2.70
        if z<=2.86:return low+(z-2.49)*((3.16-low)/.37)
        return 3.16+(z-2.86)*(.26/.56)
    for name in ['canopy_entry_red_arch','canopy_entry_cream_arch_liner']:
        o=bpy.data.objects[name]
        for v in o.data.vertices:
            v.co.y=-.735+(v.co.y+.62)*(.680/1.270)
            v.co.z=newz(v.co.x,v.co.z)
            if 4.649<=v.co.x<=4.931:v.co.x-=.525
        o.data.update()
    arch=bpy.data.objects['canopy_entry_red_arch']
    for v in arch.data.vertices:
        if v.co.y>-.10 and 3.009<=v.co.x<=4.406 and v.co.z<3.18:
            v.co.z += (3.154-v.co.z)*math.sin(.68/1.42*math.pi/2)
    arch.data.update()
    bm=bmesh.new();bm.from_mesh(arch.data)
    inner=[f for f in bm.faces if 3.009<=f.calc_center_median().x<=4.406 and f.calc_center_median().z<3.3 and abs(f.normal.y)<.95]
    bmesh.ops.delete(bm,geom=inner,context='FACES');bm.to_mesh(arch.data);bm.free();arch.data.update()
    arch.data.materials.append(bpy.data.materials['luminous_cream'])
    for p in arch.data.polygons:
        if p.normal.z < -.1: p.material_index=len(arch.data.materials)-1
    # The cream soffit continues behind the red fascia to the tiled return.
    liner=bpy.data.objects['canopy_entry_cream_arch_liner']
    front=sorted([tuple(v.co) for v in liner.data.vertices if v.co.y<-.70],key=lambda p:p[0])
    vs=[];fs=[];steps=24
    for j in range(steps+1):
        t=j/steps
        for x,y,z in front:
            vs.append((x,-.735+1.42*t,z+(3.154-z)*math.sin(t*math.pi/2)))
    n=len(front)
    for j in range(steps):
        for i in range(n-1):
            a=j*n+i;fs.append((a,a+1,a+1+n,a+n))
    me=bpy.data.meshes.new('cream_transition_mesh');me.from_pydata(vs,[],fs);me.update()
    me.materials.append(bpy.data.materials['luminous_cream']);liner.data=me
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co;uv.data[li].uv=(co.x,co.y)
    for p in me.polygons:
        p.use_smooth=True
    ceiling=bpy.data.objects['canopy_entry_ceiling']
    for v in ceiling.data.vertices:
        if v.co.y<0:v.co.y=.685-ceiling.location.y
    # The main vault continues behind the shorter arch end. Its hidden forward
    # part meets the same solid arch, while its lower rear curve remains visible.
    o=bpy.data.objects['canopy_main_luminous_vault']
    for v in o.data.vertices:
        if v.co.x>2.74:v.co.x+=.40
    o=bpy.data.objects['canopy_red_rib_5']
    for v in o.data.vertices:v.co.x+=.40
    for name in ['canopy_inferred_upper_backing','canopy_rear_red_trim']:
        o=bpy.data.objects[name]
        for v in o.data.vertices:
            if v.co.x>0:v.co.x+=.40
    # Replace isolated niche header with a continuous red wall band. Everything
    # below its 1.855 m lower edge, including glass lips and fixtures, is retained.
    bpy.data.objects.remove(bpy.data.objects['bowl_niche_red_header'],do_unlink=True)
    box('bowl_niche_continuous_upper_red',(4.7575,.3725,2.2775),(.705,1.615,.845),'red')
    box('bowl_niche_red_recess_back',(5.09,.3725,1.35),(.08,1.615,2.70),'red')
    box('entry_right_upper_red_return',(4.7575,2.085,2.6925),(.705,1.810,.995),'red')
    for name in ['entry_right_red_pier','entry_right_tile_front','entry_right_tile_return']:
        bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    # Full end return covers the 0.63 m deep bowl station, with a tiled public face.
    # The aisle edge remains x=4.355 so its 1.005 m clear strip is unchanged.
    box('entry_right_solid_end_return',(4.7775,-.34,1.35),(.845,.22,2.70),'red')
    nx=6;nz=18
    for j in range(nz):
        for i in range(nx):
            sx=.845/nx;sz=2.70/nz
            box('entry_right_front_tile_%02d_%02d'%(i,j),(4.355+(i+.5)*sx,-.456,(j+.5)*sz),(sx-.004,.012,sz-.004),'tile_'+str((i+3*j)%7))
    # Brown tiles run along the same right side wall as the red bowl recess.
    # Their curved visible boundary is the actual white soffit above them.
    box('entry_upper_side_backing',(4.530,.3725,2.955),(.25,1.615,.51),'red')
    nx=11;nz=4
    for j in range(nz):
        for i in range(nx):
            sy=1.615/nx;sz=.51/nz
            box('entry_upper_side_tile_%02d_%02d'%(i,j),(4.398,-.435+(i+.5)*sy,2.70+(j+.5)*sz),(.012,sy-.004,sz-.004),'tile_'+str((i+3*j)%7))
    # Continue the outer public tile face over the whole end return.
    for j in range(18):
        for i in range(6):
            sy=.90/6;sz=2.70/18
            box('entry_right_outer_tile_%02d_%02d'%(i,j),(5.206,-.45+(i+.5)*sy,(j+.5)*sz),(.012,sy-.004,sz-.004),'tile_'+str((i+3*j)%7))
    bpy.context.scene['canopy_detail_v15']=True
