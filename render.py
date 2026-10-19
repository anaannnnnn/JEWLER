import bpy, bmesh, math, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = dict(a.split("=") for a in argv)
METAL = opt.get("metal", "gold")
GEM = opt.get("gem", "diamond")
OUT = opt.get("out", "/content/jewelry.png")
SAMPLES = int(opt.get("samples", 512))
RES = int(opt.get("res", 1600))

METALS = {"gold": (1.0, 0.77, 0.34), "rose": (0.95, 0.55, 0.45),
          "silver": (0.95, 0.95, 0.96), "platinum": (0.80, 0.80, 0.82)}
GEMS = {"diamond": (1, 1, 1), "ruby": (0.9, 0.02, 0.05),
        "emerald": (0.02, 0.7, 0.2), "sapphire": (0.03, 0.12, 0.9)}

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- materials ----------
def metal_mat():
    m = bpy.data.materials.new("Metal"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*METALS[METAL], 1)
    b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = 0.1
    return m

def gem_mat():
    m = bpy.data.materials.new("Gem"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    glass = nt.nodes.new("ShaderNodeBsdfGlass")
    glass.inputs["IOR"].default_value = 2.417 if GEM == "diamond" else 1.77
    glass.inputs["Roughness"].default_value = 0.0
    glass.inputs["Color"].default_value = (*GEMS[GEM], 1)
    trans = nt.nodes.new("ShaderNodeBsdfTransparent")
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Shadow Ray"], mix.inputs[0])
    nt.links.new(glass.outputs[0], mix.inputs[1])
    nt.links.new(trans.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return m

def floor_mat():
    m = bpy.data.materials.new("Floor"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.03, 0.03, 0.035, 1)
    b.inputs["Roughness"].default_value = 0.12
    return m

# ---------- geometry ----------
def brilliant_cut():
    v = []
    for j in range(16):
        a = j * math.pi / 8
        v.append((math.cos(a), math.sin(a), 0))
    for i in range(8):
        a = i * math.pi / 4
        v.append((0.58 * math.cos(a), 0.58 * math.sin(a), 0.32))
    v.append((0, 0, -0.45))
    f = [list(range(16, 24))]
    for i in range(8):
        n = (i + 1) % 8
        f.append((2 * i, 2 * i + 1, 16 + i))
        f.append((2 * i + 1, (2 * i + 2) % 16, 16 + n))
        f.append((2 * i + 1, 16 + n, 16 + i))
    for j in range(16):
        f.append(((j + 1) % 16, j, 24))
    me = bpy.data.meshes.new("Diamond"); me.from_pydata(v, [], f); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    return me

mm, gm = metal_mat(), gem_mat()

# band
bpy.ops.mesh.primitive_torus_add(major_radius=0.9, minor_radius=0.09,
                                 major_segments=128, minor_segments=48,
                                 location=(0, 0, 0.99), rotation=(math.pi / 2, 0, 0))
band = bpy.context.object; band.data.materials.append(mm)
bpy.ops.object.shade_smooth()

# gem
gem = bpy.data.objects.new("Gem", brilliant_cut())
scene.collection.objects.link(gem)
gem.scale = (0.38, 0.38, 0.38); gem.location = (0, 0, 1.23)
gem.data.materials.append(gm)

# prongs
for k in range(4):
    a = math.pi / 4 + k * math.pi / 2
    x, y = 0.40 * math.cos(a), 0.40 * math.sin(a)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.3, location=(x, y, 1.2))
    p = bpy.context.object; p.data.materials.append(mm); bpy.ops.object.shade_smooth()
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, location=(x * 0.93, y * 0.93, 1.34))
    s = bpy.context.object; s.data.materials.append(mm); bpy.ops.object.shade_smooth()

# floor
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
bpy.context.object.data.materials.append(floor_mat())

# ---------- lights ----------
def area(loc, size, power, shape="RECTANGLE", sy=None):
    d = bpy.data.lights.new("L", "AREA"); d.energy = power; d.shape = shape
    d.size = size
    if sy: d.size_y = sy
    o = bpy.data.objects.new("L", d); scene.collection.objects.link(o)
    o.location = loc
    c = o.constraints.new("TRACK_TO"); c.target = target
    c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"

target = bpy.data.objects.new("T", None); scene.collection.objects.link(target)
target.location = (0, 0, 0.75)
area((0, 0, 6), 4, 1500)
area((-5, -3, 3), 3, 1200)
area((5, 3, 2.5), 1.0, 1500, "RECTANGLE", 5)
area((4, -5, 1.5), 1.0, 900, "RECTANGLE", 4)
area((-4, 5, 3), 2, 1000)

world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.03, 0.03, 0.04, 1); bg.inputs[1].default_value = 1.0

# ---------- camera ----------
cd = bpy.data.cameras.new("Cam"); cd.lens = 70
cam = bpy.data.objects.new("Cam", cd); scene.collection.objects.link(cam)
cam.location = (3.6, -4.6, 2.4)
c = cam.constraints.new("TRACK_TO"); c.target = target
c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
cd.dof.use_dof = True; cd.dof.focus_object = target; cd.dof.aperture_fstop = 11
scene.camera = cam

# ---------- render ----------
scene.render.engine = "CYCLES"
cy = scene.cycles
cy.samples = SAMPLES
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
cy.max_bounces = 32; cy.glossy_bounces = 16
cy.transmission_bounces = 32; cy.transparent_max_bounces = 32
cy.caustics_reflective = False; cy.caustics_refractive = False
cy.sample_clamp_indirect = 10

prefs = bpy.context.preferences.addons["cycles"].preferences
for t in ("OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = t
        prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == t]
        if gpus:
            for d in prefs.devices: d.use = d.type == t
            cy.device = "GPU"; print("Using", t, [d.name for d in gpus]); break
    except Exception as e:
        print(e)

scene.render.resolution_x = RES; scene.render.resolution_y = RES
scene.view_settings.view_transform = "AgX"
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("Saved", OUT)
