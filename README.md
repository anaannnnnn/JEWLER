# Jewelry 3D Generator

Photorealistic 3D jewelry renders (ring with diamond-cut gem) using Blender Cycles on a GPU. Built for Google Colab.

## Run in Colab (3 commands)

Set Runtime > Change runtime type > T4 GPU, then:

```
!git clone https://github.com/anaannnnnn/JEWLER.git
%cd JEWLER
!pip -q install -r requirements.txt && python render.py -- metal=gold gem=diamond out=/content/ring.png
```

Show the result:

```python
from IPython.display import Image
Image("/content/ring.png")
```

## Options

| Option | Values | Default |
|---|---|---|
| metal | gold, rose, silver, platinum | gold |
| gem | diamond, ruby, emerald, sapphire | diamond |
| samples | e.g. 128 (fast) to 1024 (best) | 512 |
| res | image size in pixels | 1600 |
| out | output path | /content/jewelry.png |

Example:

```
!python render.py -- metal=rose gem=sapphire samples=768 res=2000 out=/content/ring2.png
```

## Notes

- Uses the `bpy` Python package (Blender as a module). Needs Python 3.11 on some versions; if `pip install bpy` fails, see `colab_blender_fallback.md`.
- Renders with OptiX/CUDA when a GPU is available, otherwise falls back to CPU (slow).
