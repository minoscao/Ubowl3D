"""Supplemental entrance relationship camera. Does not modify delivery geometry."""
import bpy
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(r/'UBowl_master.blend'))
s=bpy.context.scene;c=s.camera
c.data.type='PERSP';c.data.sensor_fit='VERTICAL';c.data.sensor_height=36;c.data.lens=40
c.location=(3.88,-3.6,2.2);c.rotation_euler=(Vector((3.7,1.3,1.55))-c.location).to_track_quat('-Z','Y').to_euler()
s.render.resolution_x=1100;s.render.resolution_y=1100;s.render.resolution_percentage=100
s.render.filepath=str(r/'review'/'entry-entrance.png');bpy.ops.render.render(write_still=True)
