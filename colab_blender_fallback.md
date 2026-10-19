# If `pip install bpy` fails

Download Blender directly and run the script with it:

```
!wget -q https://download.blender.org/release/Blender4.2/blender-4.2.3-linux-x64.tar.xz
!tar -xf blender-4.2.3-linux-x64.tar.xz
!./blender-4.2.3-linux-x64/blender -b -P render.py -- metal=gold gem=diamond out=/content/ring.png
```

(Check https://download.blender.org/release/ for the current 4.2 LTS filename if the link changes.)
