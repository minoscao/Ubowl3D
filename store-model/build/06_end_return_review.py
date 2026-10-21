"""Review candidate end return before replacing the deliverable model."""
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(r/'review'/'UBowl_candidate.blend'))
s=bpy.context.scene;c=s.camera
s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100
c.data.type='PERSP';c.data.sensor_fit='VERTICAL';c.data.sensor_height=36;c.data.lens=40
c.location=(3.88,-3.6,2.2);c.rotation_euler=(Vector((3.7,1.3,1.55))-c.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(r/'review'/'end-return-entrance.png');bpy.ops.render.render(write_still=True)
c.data.type='ORTHO';c.data.ortho_scale=3.6
c.location=(3.65,-8,1.65);c.rotation_euler=(Vector((3.65,1.3,1.65))-c.location).to_track_quat('-Z','Y').to_euler()
s.render.filepath=str(r/'review'/'end-return-front.png');bpy.ops.render.render(write_still=True)
print('END_RETURN_PREVIEW_COMPLETE',flush=True)
