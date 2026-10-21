# UBowl 模型源文件

`UBowl_master.blend` 是已交付 V1.5 的可编辑源文件。`UBowl_store.glb` 与网页 `dist/assets/UBowl_store.glb` 完全一致；空间、通道与墙宽仍是照片估算，非测绘尺寸。

- `build/`：原建模、材质生成、导出及局部修正脚本。
- `textures/`：网页模型使用的贴图。
- `ref/`：用户提供的参考照片。
- `review/UBowl_v1.4_before_canopy.blend`：V1.5 弧棚和侧墙修正所依赖的 V1.4 基线。
- `asset-manifest.json`：版本、几何、验证及尺寸假设记录。

继续编辑时从 `UBowl_master.blend` 打开。脚本来自既有制作环境；不要直接运行 `01_build_store.py` 覆盖已交付主文件，它是较早阶段的生成脚本。V1.5 的候选重建入口是 `08_canopy_detail_candidate.py`，会读取保留的 V1.4 基线并生成独立候选文件；完整历史步骤见清单。Python 材质处理需要 Pillow、NumPy 与 OpenCV；部分标牌生成使用 Windows Arial Bold，字体文件不随仓库分发。

参考图像、品牌和视频素材用于本项目门店还原；本仓库未授予第三方对这些素材的额外使用许可。Three.js 许可位于 `dist/vendor/THREE-LICENSE.txt`。
