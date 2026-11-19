import bpy, math, os, sys
from mathutils import Vector
from math import sin, cos, pi
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
out=args[0] if args else "/tmp/f35frames"; os.makedirs(out,exist_ok=True)
bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete(use_global=False)
def material(n,c,m=.4,r=.4):
 x=bpy.data.materials.new(n); x.diffuse_color=(*c,1); x.use_nodes=True
 p=x.node_tree.nodes.get("Principled BSDF"); p.inputs["Base Color"].default_value=(*c,1); p.inputs["Metallic"].default_value=m; p.inputs["Roughness"].default_value=r
 return x
gray=material("Titanium grey",(.23,.28,.34),.75,.3); dark=material("Graphite",(.045,.065,.09),.5,.4); glass=material("Smoked canopy",(.015,.08,.13),.8,.16); steel=material("Engine alloy",(.48,.52,.58),.85,.25); blue=material("Blue lights",(.02,.32,.9),.3,.2); floor=material("Hangar",(.018,.026,.04),.2,.7)
def mesh(n,v,f,ma,bevel=.03):
 me=bpy.data.meshes.new(n); me.from_pydata(v,[],f); me.materials.append(ma); me.update(); o=bpy.data.objects.new(n,me); bpy.context.collection.objects.link(o)
 if bevel: b=o.modifiers.new("Machined edge","BEVEL"); b.width=bevel; b.segments=2; o.modifiers.new("Weighted normals","WEIGHTED_NORMAL")
 return o
def cube(n,loc,scale,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=n; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma)
 b=o.modifiers.new("Edge radius","BEVEL"); b.width=.04; b.segments=3; o.modifiers.new("Weighted normals","WEIGHTED_NORMAL"); return o
def sphere(n,loc,scale,ma):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc); o=bpy.context.object; o.name=n; o.scale=scale; o.data.materials.append(ma); bpy.ops.object.shade_smooth(); return o
rings=[(-6.3,.08,.1),(-5.4,.3,.28),(-4.1,.56,.46),(-2,.78,.62),(0,.88,.68),(2,.8,.62),(4.2,.62,.48),(5.5,.48,.4),(6,.42,.35)]
v=[]; N=16
for x,ry,rz in rings:
 for j in range(N):
  a=2*pi*j/N; v.append((x,ry*cos(a),rz*sin(a)))
f=[]
for i in range(len(rings)-1):
 for j in range(N): a=i*N+j; b=i*N+(j+1)%N; f.append((a,b,b+N,a+N))
f.extend([tuple(range(N-1,-1,-1)),tuple((len(rings)-1)*N+j for j in range(N))])
body=mesh("Fuselage",v,f,gray); parts=[body]
for side in (-1,1):
 p=[(-2,side*.68),(0.2,side*5.25),(2.35,side*4.95),(2.15,side*.78)]
 w=mesh("Swept wing",[(x,y,z) for z in (-.12,.12) for x,y in p],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],gray,.055); parts.append(w)
 p3=[(3.25,side*1,.2),(5.4,side*1.1,.2),(4.8,side*2.15,2),(3.55,side*2,1.85)]
 tail=mesh("Canted vertical tail",p3+[(x,y+side*.13,z) for x,y,z in p3],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],gray); parts.append(tail)
 p4=[(3,side*.6,.25),(4.9,side*1.8,.25),(5.25,side*1.65,.25),(4.25,side*.55,.25)]
 stab=mesh("Horizontal stabilizer",p4+[(x,y,z+.12) for x,y,z in p4],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],gray); parts.append(stab)
 intake=cube("Side intake exterior",(.35,side*.78,-.05),(1.9,.22,.42),dark); parts.append(intake)
 gear=cube("Main landing gear", (1.6,side*.9,-.82),(.13,.13,1),steel); parts.append(gear)
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.29,depth=.18,location=(1.72,side*.9,-1.3),rotation=(pi/2,0,0)); wheel=bpy.context.object; wheel.name="Main landing gear wheel"; wheel.data.materials.append(dark); parts.append(wheel)
nose_gear=cube("Nose gear",(-4.45,0,-.78),(.12,.12,.8),steel); parts.append(nose_gear)
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.22,depth=.15,location=(-4.35,0,-1.17),rotation=(pi/2,0,0)); nose_wheel=bpy.context.object; nose_wheel.name="Nose landing gear wheel"; nose_wheel.data.materials.append(dark); parts.append(nose_wheel)
can=sphere("Cockpit canopy",(-3.15,0,.58),(1.55,.62,.48),glass); parts.append(can)
parts.append(cube("Pilot seat silhouette",(-3.45,0,.42),(.34,.4,.58),dark))
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.43,depth=.85,location=(5.9,0,0),rotation=(0,pi/2,0)); nozzle=bpy.context.object; nozzle.name="Single engine nozzle"; nozzle.data.materials.append(steel); parts.append(nozzle)
bpy.ops.mesh.primitive_torus_add(major_radius=.37,minor_radius=.05,location=(6.34,0,0),rotation=(0,pi/2,0)); bpy.context.object.data.materials.append(dark)
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.33,depth=.12,location=(5.65,0,0),rotation=(0,pi/2,0)); fan=bpy.context.object; fan.name="Simplified engine fan demonstration"; fan.data.materials.append(steel); parts.append(fan)
for s in (-1,1): sphere("Navigation light",(.15,s*5.2,.12),(.1,.08,.07),blue)
cube("Hangar floor",(0,0,-1.7),(200,200,.2),floor)
for name,loc,power,size,color in [("Key",(0,-7,10),1800,8,(.7,.82,1)),("Rim",(3,7,7),2200,7,(.3,.55,1)),("Fill",(-8,-2,4),950,6,(1,.72,.46))]:
 bpy.ops.object.light_add(type="AREA",location=loc); l=bpy.context.object; l.data.energy=power; l.data.shape="DISK"; l.data.size=size; l.data.color=color; l.rotation_euler=(Vector((0,0,0))-l.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add(location=(-10,-15,7)); cam=bpy.context.object; bpy.context.scene.camera=cam; cam.data.lens=52
def camera_key(fr,loc):
 cam.location=loc; cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat("-Z","Y").to_euler(); cam.keyframe_insert(data_path="location",frame=fr); cam.keyframe_insert(data_path="rotation_euler",frame=fr)
for fr,loc in [(1,(-10,-15,7)),(720,(-8,-17,5)),(1440,(0,-17,9)),(2160,(10,-14,6)),(2880,(5,16,8)),(3600,(-10,-15,7))]: camera_key(fr,loc)
for i,o in enumerate(parts):
 base=o.location.copy(); d=Vector((0,1 if i%2==0 else -1,.35 if i%3==0 else -.2))
 if "wing" in o.name.lower(): d=Vector((0,1 if i%2==0 else -1,0))
 o.location=base; o.keyframe_insert(data_path="location",frame=1)
 o.location=base+d*1.7; o.keyframe_insert(data_path="location",frame=900)
 o.location=base+d*1.7; o.keyframe_insert(data_path="location",frame=1320)
 o.location=base; o.keyframe_insert(data_path="location",frame=1560)
for o in bpy.data.objects:
 if o.animation_data and o.animation_data.action:
  for fc in o.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation="BEZIER"
s=bpy.context.scene; s.render.engine="BLENDER_WORKBENCH"; s.render.resolution_x=1280; s.render.resolution_y=720; s.render.resolution_percentage=100; s.render.fps=12; s.frame_start=1; s.frame_end=3600
s.display.shading.light="STUDIO"; s.display.shading.studio_light="paint.sl"; s.display.shading.color_type="MATERIAL"; s.display.shading.show_shadows=True; s.display.shading.show_cavity=True; s.display.shading.cavity_type="BOTH"; s.display.shading.background_type="WORLD"
s.render.image_settings.file_format="PNG"; s.render.image_settings.color_mode="RGB"; s.render.filepath=os.path.join(out,"frame_"); s.render.image_settings.color_depth="8"; s.view_settings.view_transform="Standard"
s.frame_set(1); bpy.ops.render.render(animation=True)
