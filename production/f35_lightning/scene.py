import bpy, math, os
from mathutils import Vector
from math import sin, cos, pi

# F-35C public-reference educational visualization. Not engineering CAD.
args=sys_args = __import__("sys").argv
out = args[args.index("--")+1] if "--" in args else "/tmp/f35frames"
os.makedirs(out, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def mat(name, color, metallic=0.0, rough=.4):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metallic
    p.inputs["Roughness"].default_value=rough
    return m

skin=mat("FS 36170 carrier aircraft grey",(.19,.22,.25),.48,.34)
edge=mat("Dark graphite composite",(.035,.047,.06),.28,.42)
canopy=mat("Coated smoked canopy",(.018,.075,.105),.72,.16)
metal=mat("Titanium and landing gear",(.38,.42,.46),.82,.24)
rubber=mat("Tyre rubber",(.012,.015,.018),.05,.82)
lightmat=mat("Navigation light blue",(.04,.35,.95),.2,.18)
red=mat("Navigation light red",(.75,.025,.018),.15,.25)
deck=mat("Aircraft carrier nonskid deck",(.075,.09,.10),.18,.78)
yellow=mat("Deck safety yellow",(.95,.55,.035),.12,.4)
white=mat("Deck markings",(.72,.76,.78),.05,.5)

def mesh_obj(name, verts, faces, material, bevel=0):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.materials.append(material); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob)
    if bevel:
        mod=ob.modifiers.new("Soft machined edges","BEVEL"); mod.width=bevel; mod.segments=3
        ob.modifiers.new("Weighted corner normals","WEIGHTED_NORMAL")
    return ob

def cube(name, loc, scale, material, bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o=bpy.context.object; o.name=name; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        b=o.modifiers.new("Rounded edges","BEVEL"); b.width=bevel; b.segments=3
        o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return o

def sphere(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; o.data.materials.append(material)
    bpy.ops.object.shade_smooth(); return o

def cylinder(name, loc, radius, depth, material, rotation=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=radius, depth=depth, location=loc, rotation=rotation)
    o=bpy.context.object; o.name=name; o.data.materials.append(material)
    b=o.modifiers.new("Rounded rim","BEVEL"); b.width=.025; b.segments=3
    o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
    return o

def line(name, points, material, radius=.012):
    c=bpy.data.curves.new(name,"CURVE"); c.dimensions="3D"; c.bevel_depth=radius; c.bevel_resolution=3
    sp=c.splines.new("POLY"); sp.points.add(len(points)-1)
    for p,co in zip(sp.points,points): p.co=(*co,1)
    o=bpy.data.objects.new(name,c); bpy.context.collection.objects.link(o); o.data.materials.append(material)
    return o

parts=[]
# Long blended fuselage loft, nose to engine.
rings=[(-6.8,.025,.04),(-6.2,.16,.16),(-5.3,.34,.29),(-4.0,.55,.45),(-2.2,.72,.59),(0,.83,.68),(2.1,.78,.63),(4.0,.64,.52),(5.4,.50,.43),(6.1,.43,.38)]
N=32; verts=[]
for x,ry,rz in rings:
    for j in range(N):
        a=2*pi*j/N
        verts.append((x,ry*cos(a),.02+rz*sin(a)))
faces=[]
for i in range(len(rings)-1):
    for j in range(N):
        a=i*N+j; b=i*N+(j+1)%N; faces.append((a,b,b+N,a+N))
faces += [tuple(range(N-1,-1,-1)),tuple((len(rings)-1)*N+j for j in range(N))]
fuselage=mesh_obj("Blended F-35C fuselage",verts,faces,skin,.018); parts.append(fuselage)

# Cambered swept wing panels; C variant has larger folding carrier wings.
def wing(side, name, coords, material=skin):
    v=[]
    for zsign in (1,-1):
        for x,y,z in coords:
            v.append((x,side*y,z*zsign))
    n=len(coords); f=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
    for i in range(n):
        j=(i+1)%n; f.append((i,j,n+j,n+i))
    return mesh_obj(name,v,f,material,.035)

wing_plan=[(-2.45,.72,.08),(-.85,2.95,.22),(1.25,5.35,.12),(2.35,5.05,.08),(2.05,1.05,.10)]
for side in (-1,1):
    w=wing(side,"F-35C enlarged carrier wing",wing_plan); parts.append(w)
    # Fold joint and outer folding tip, visibly articulated.
    line("Wing fold seam",[(1.2,side*4.72,.16),(1.8,side*4.82,.16),(2.35,side*4.85,.15)],edge,.022)
    tip=wing(side,"Folding wingtip",[(1.2,4.72,.13),(2.35,4.85,.13),(2.7,5.85,.08),(2.0,5.92,.08)],skin)
    parts.append(tip)
    # Leading/trailing edge control surfaces.
    line("Flap hinge",[(.55,side*1.6,.18),(1.35,side*4.65,.17)],edge,.018)
    line("Aileron edge",[(1.35,side*4.65,.17),(2.25,side*4.95,.13)],edge,.018)
    # Canted twin tails.
    tail=wing(side,"Canted vertical stabilizer",[(3.0,1.0,.25),(5.45,1.12,.22),(4.95,2.15,1.85),(3.55,1.92,1.75)],skin)
    parts.append(tail)
    # Horizontal stabilizers.
    stab=wing(side,"All-moving horizontal stabilizer",[(3.05,.58,.22),(4.65,1.35,.20),(5.25,1.52,.20),(4.35,.55,.22)],skin)
    parts.append(stab)
    # Side intake lips and dark recesses.
    intake=cube("Side intake duct surround",(.05,side*.77,-.02),(1.45,.16,.48),edge,.11); parts.append(intake)
    lip=line("Intake leading lip",[(-.65,side*.82,.15),(.3,side*.88,.18),(.75,side*.83,.08)],metal,.025)

# Cockpit, windscreen frame and seat silhouette.
can=sphere("One-piece tinted canopy",(-3.45,0,.59),(1.58,.58,.48),canopy); parts.append(can)
line("Canopy frame", [(-4.9,0,.59),(-4.35,0,1.0),(-3.4,0,1.08),(-2.15,0,.67)],metal,.025)
parts.append(cube("Pilot seat silhouette",(-3.65,0,.35),(.38,.42,.56),edge,.06))

# Engine nozzle and simplified educational engine cutaway.
nozzle=cylinder("F135 engine exhaust nozzle", (5.95,0,.02),.39,.8,metal,(0,pi/2,0)); parts.append(nozzle)
cylinder("Exhaust dark aperture",(6.38,0,.02),.29,.035,edge,(0,pi/2,0))
cylinder("Engine fan demonstration",(5.25,0,.02),.32,.16,metal,(0,pi/2,0))

# Carrier-capable reinforced landing gear: twin nose wheels, robust main gear.
nose_strut=cube("Reinforced nose gear strut",(-4.55,0,-.78),(.14,.16,.88),metal,.035); parts.append(nose_strut)
for y in (-.19,.19):
    cylinder("Twin nose landing tyre",(-4.52,y,-1.24),.205,.13,rubber,(pi/2,0,0))
    cylinder("Nose wheel hub",(-4.52,y*1.38,-1.24),.105,.025,metal,(pi/2,0,0))
for side in (-1,1):
    strut=cube("Heavy-duty main gear strut",(1.5,side*.92,-.78),(.16,.18,.92),metal,.035); parts.append(strut)
    for offset in (-.17,.17):
        cylinder("Main landing tyre",(1.65,side*.98+offset,-1.28),.27,.16,rubber,(pi/2,0,0))
        cylinder("Main wheel hub",(1.65,side*.98+offset*1.5,-1.28),.13,.025,metal,(pi/2,0,0))
# Tailhook, a visible carrier-specific F-35C feature.
hook=line("Carrier arresting tailhook",[(5.35,0,-.28),(5.75,0,-.55),(6.0,0,-.85),(6.22,0,-.88)],metal,.055)
parts.append(hook)
# Arresting hook tip.
sphere("Tailhook contact shoe",(6.22,0,-.88),(.12,.09,.07),edge)

# Small exterior panel lines and access panels: visual detailing only.
for side in (-1,1):
    line("Upper fuselage panel seam",[(-1.8,side*.56,.45),(-.7,side*.72,.54),(.8,side*.72,.52),(1.8,side*.62,.42)],edge,.008)
    line("Wing service panel",[(-.35,side*2.4,.245),(.25,side*2.9,.24),(.85,side*2.85,.23)],edge,.009)
    sphere("Wingtip navigation light",(1.85,side*5.75,.12),(.09,.08,.065),red if side<0 else lightmat)
    # Subtle access fasteners.
    for x,y in [(-.4,1.55),(.25,2.1),(.8,2.8),(1.3,3.55)]:
        sphere("Flush fastener",(x,side*y,.245),(.025,.025,.009),metal)

# Carrier flight deck environment and runway/catapult guide markings.
cube("Carrier flight deck",(0,0,-1.75),(200,200,.25),deck,.02)
for y in (-3.2,3.2):
    line("Catapult track marking",[(-18,y,-1.61),(18,y,-1.61)],white,.025)
for x in range(-16,17,4):
    line("Deck tie-down marking",[(x,-8,-1.61),(x,-7.7,-1.61)],yellow,.025)
line("Deck safety line",[(-16,-8,-1.60),(-16,8,-1.60)],yellow,.035)
line("Deck center guide",[(-18,0,-1.60),(18,0,-1.60)],white,.012)

# Studio / flight-deck cinematic lighting.
world=bpy.context.scene.world or bpy.data.worlds.new("Hangar atmosphere")
bpy.context.scene.world=world; world.use_nodes=True
world.node_tree.nodes["Background"].inputs[0].default_value=(.11,.14,.18,1)
world.node_tree.nodes["Background"].inputs[1].default_value=.32
for name,loc,power,size,color in [
    ("Large softbox",(-1,-8,12),2600,9,(.72,.82,1)),
    ("Cool rim",(4,8,9),3200,7,(.42,.62,1)),
    ("Warm fill",(-9,-1,5),1500,6,(1,.72,.48)),
    ("Top strip",(2,0,14),1800,8,(1,1,1))]:
    bpy.ops.object.light_add(type="AREA",location=loc); l=bpy.context.object
    l.name=name; l.data.energy=power; l.data.shape="DISK"; l.data.size=size; l.data.color=color
    l.rotation_euler=(Vector((0,0,0))-l.location).to_track_quat("-Z","Y").to_euler()

# Cinematic orbit camera.
bpy.ops.object.camera_add(location=(-11,-17,8))
cam=bpy.context.object; cam.name="Cinematic aircraft camera"; bpy.context.scene.camera=cam
cam.data.lens=55
def camera_key(frame,loc,target=(0,0,0)):
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    cam.keyframe_insert(data_path="location",frame=frame)
    cam.keyframe_insert(data_path="rotation_euler",frame=frame)
for fr,loc in [(1,(-11,-17,8)),(720,(-8,-19,5)),(1440,(0,-18,10)),(2160,(11,-14,7)),(2880,(5,17,8)),(3600,(-11,-17,8))]:
    camera_key(fr,loc)

# Exploded-view sequence; preserve a clean assembled hero shot at the end.
for i,obj in enumerate(parts):
    base=obj.location.copy()
    direction=Vector((0,1 if i%2==0 else -1,.4 if i%3==0 else -.2))
    if "wing" in obj.name.lower(): direction=Vector((0,1 if i%2==0 else -1,0))
    obj.location=base; obj.keyframe_insert(data_path="location",frame=1)
    obj.location=base+direction*1.25; obj.keyframe_insert(data_path="location",frame=900)
    obj.location=base+direction*1.25; obj.keyframe_insert(data_path="location",frame=1320)
    obj.location=base; obj.keyframe_insert(data_path="location",frame=1560)
for obj in bpy.data.objects:
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for key in fc.keyframe_points: key.interpolation="BEZIER"

scene=bpy.context.scene
scene.render.resolution_x=1280; scene.render.resolution_y=720
scene.render.resolution_percentage=100; scene.render.fps=12
scene.frame_start=1; scene.frame_end=3600
# Eevee high-quality PBR look keeps the 3,600-frame cloud render feasible.
try:
    scene.render.engine="BLENDER_EEVEE_NEXT"
except Exception:
    scene.render.engine="BLENDER_EEVEE"
if hasattr(scene,"eevee"):
    profile=os.environ.get("RENDER_PROFILE","high")
    scene.eevee.taa_render_samples={"high":128,"standard":64,"compact":32}.get(profile,128)
scene.render.image_settings.file_format="PNG"
scene.render.image_settings.color_mode="RGB"
scene.render.image_settings.color_depth="8"
scene.render.filepath=os.path.join(out,"frame_")
scene.render.film_transparent=False
scene.view_settings.view_transform="Standard"
scene.view_settings.look="AgX" if "AgX" in [x.name for x in bpy.context.scene.view_settings.bl_rna.properties["look"].enum_items] else "Medium High Contrast"
scene.camera.data.dof.use_dof=True
scene.camera.data.dof.focus_object=fuselage
scene.camera.data.dof.aperture_fstop=8
scene.frame_set(1)
if os.environ.get("F35_SMOKE_TEST")=="1":
    scene.render.resolution_percentage=40
    scene.render.filepath=os.path.join(out,"smoke_")
    bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
