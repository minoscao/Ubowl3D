import bpy,json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(r/'UBowl_master.blend'))
for ob in bpy.data.collections['LOW'].objects:
    if ob.name.startswith(('canopy_entry_red_arch','canopy_entry_cream_arch','entry_right','bowl_')):
        pts=[ob.matrix_world@Vector(v) for v in ob.bound_box]
        print(json.dumps({'name':ob.name,'bounds':[[round(min(p[i] for p in pts),4),round(max(p[i] for p in pts),4)] for i in range(3)]}))
o=bpy.data.objects['canopy_entry_cream_arch_liner']
print('LINER',[(tuple(round(x,4) for x in v.co)) for v in o.data.vertices])
