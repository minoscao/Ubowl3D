"""Baseline/candidate camera match to ref/20261011-161351.jpg. No export."""
import bpy, math, sys, json
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[1]
candidate='--candidate' in sys.argv
source=r/'review'/'UBowl_candidate_v1.5.blend' if candidate else r/'UBowl_master.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
s=bpy.context.scene;c=s.camera
c.data.type='PERSP';c.data.sensor_fit='HORIZONTAL';c.data.sensor_width=36;c.data.lens=25
c.location=(-2.614,-5.175,1.65)
c.rotation_euler=(Vector((math.sin(math.radians(24.5)),math.cos(math.radians(24.5)),0))).to_track_quat('-Z','Y').to_euler()
c.data.shift_y=-.0035
s.render.resolution_x=1440;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.filepath=str(r/'review'/('canopy-candidate-full.png' if candidate else 'canopy-v1.4-full.png'))
bpy.ops.render.render(write_still=True)
s.render.use_border=True;s.render.use_crop_to_border=True
s.render.border_min_x=787/1440;s.render.border_max_x=1431/1440
s.render.border_min_y=1-788/1080;s.render.border_max_y=1-206/1080
s.render.filepath=str(r/'review'/('canopy-candidate-crop.png' if candidate else 'canopy-v1.4-crop.png'))
bpy.ops.render.render(write_still=True)
s.render.use_border=False;s.render.use_crop_to_border=False
if candidate:
    c.data.sensor_fit='VERTICAL';c.data.sensor_height=36;c.data.lens=40;c.data.shift_y=0
    c.location=(3.88,-3.6,2.2);c.rotation_euler=(Vector((3.7,1.3,1.55))-c.location).to_track_quat('-Z','Y').to_euler()
    s.render.resolution_x=1100;s.render.resolution_y=1100
    s.render.filepath=str(r/'review'/'canopy-candidate-entrance.png');bpy.ops.render.render(write_still=True)
    c.data.type='ORTHO';c.data.ortho_scale=3.6
    c.location=(3.65,-8,1.65);c.rotation_euler=(Vector((3.65,1.3,1.65))-c.location).to_track_quat('-Z','Y').to_euler()
    s.render.filepath=str(r/'review'/'canopy-candidate-front.png');bpy.ops.render.render(write_still=True)
print('CANOPY_DETAIL_RENDER_COMPLETE',flush=True)
