"""Create a reversible v1.5 candidate; final delivery files stay untouched."""
import bpy,sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(r/'build'))
from canopy_detail_geometry import apply_detail
baseline=r/'review'/'UBowl_v1.4_before_canopy.blend'
bpy.ops.wm.open_mainfile(filepath=str(baseline if baseline.exists() else r/'UBowl_master.blend'))
apply_detail()
bpy.ops.wm.save_as_mainfile(filepath=str(r/'review'/'UBowl_candidate_v1.5.blend'))
print('CANOPY_DETAIL_CANDIDATE_SAVED',flush=True)
