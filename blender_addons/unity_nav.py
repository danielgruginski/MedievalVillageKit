bl_info = {
    "name": "Unity-Style Viewport Navigation",
    "author": "Claude",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport: hold Right Mouse to fly",
    "description": "Unity Scene-view camera controls: hold RMB + WASD/QE to fly, Alt+LMB orbit, MMB pan, "
                   "Alt+RMB zoom, F frame selected",
    "category": "3D View",
}

import math
import time

import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty
from mathutils import Matrix, Quaternion, Vector

# key -> direction in view space (x right, y up, z backwards: the view looks down -z)
MOVE_KEYS = {
    'W': (0.0, 0.0, -1.0), 'UP_ARROW': (0.0, 0.0, -1.0),
    'S': (0.0, 0.0, 1.0), 'DOWN_ARROW': (0.0, 0.0, 1.0),
    'A': (-1.0, 0.0, 0.0), 'LEFT_ARROW': (-1.0, 0.0, 0.0),
    'D': (1.0, 0.0, 0.0), 'RIGHT_ARROW': (1.0, 0.0, 0.0),
    'Q': (0.0, -1.0, 0.0), 'E': (0.0, 1.0, 0.0),
}
SHIFT_KEYS = {'LEFT_SHIFT', 'RIGHT_SHIFT'}
# Keymaps whose plain right click opens a context menu. The fly operator takes that press over and opens
# the same menu when the button is released without flying (like Unity's right click).
RMB_KEYMAPS = (("Object Mode", 'EMPTY'), ("Mesh", 'EMPTY'), ("Curve", 'EMPTY'), ("Armature", 'EMPTY'),
               ("Pose", 'EMPTY'), ("Lattice", 'EMPTY'), ("Metaball", 'EMPTY'), ("Font", 'EMPTY'),
               ("3D View", 'VIEW_3D'))
KEYMAP_DEFAULTS = {"alt_nav": True, "mmb_pan": True, "f_frame": True}


def _prefs():
    addon = bpy.context.preferences.addons.get(__name__)
    return addon.preferences if addon else None


def fly_look(rot, dx, dy, sens_deg, invert_y=False):
    """Mouse look: yaw about world Z, pitch about the view's right axis. Adds no roll and stops short of the poles."""
    s = math.radians(sens_deg)
    if invert_y:
        dy = -dy
    right = rot @ Vector((1.0, 0.0, 0.0))
    pitched = Quaternion(right, dy * s) @ rot
    if abs((pitched @ Vector((0.0, 0.0, -1.0))).z) > 0.995:
        pitched = rot
    return (Quaternion((0.0, 0.0, 1.0), -dx * s) @ pitched).normalized()


class VIEW3D_OT_unity_fly(bpy.types.Operator):
    """Hold the right mouse button to look around; W/A/S/D/Q/E fly, Shift goes faster, the mouse wheel changes
the speed. A right click without moving opens the usual context menu"""
    bl_idname = "view3d.unity_fly"
    bl_label = "Unity Fly Navigation"
    bl_options = {'BLOCKING'}

    menu: StringProperty(name="Context Menu", default="", options={'SKIP_SAVE'})
    menu_kind: StringProperty(name="Menu Kind", default='MENU', options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        rv3d = context.region_data
        return (context.area is not None and context.area.type == 'VIEW_3D'
                and rv3d is not None and not rv3d.lock_rotation)

    def invoke(self, context, event):
        self.rv3d = context.region_data
        camera = context.scene.camera
        # looking through the scene camera: fly the camera object itself
        self.cam = camera if (self.rv3d.view_perspective == 'CAMERA' and camera is not None) else None
        self.start_mouse = self.last_mouse = (event.mouse_x, event.mouse_y)
        self.t_last = time.perf_counter()
        self.held = set()
        self.shift = event.shift
        self.active = False       # became a look/fly (otherwise the release is a plain click)
        self.looking = False      # pointer hidden and kept inside the region
        self.moved = False
        self.move_time = 0.0
        self.eye = self.rot = self.scale = None
        wm = context.window_manager
        self.timer = wm.event_timer_add(1.0 / 120.0, window=context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    # ---------------------------------------------------------------- pose
    def _begin(self, context):
        """First real input: switch an orthographic view to perspective, read the pose, show the help line."""
        if self.active:
            return
        self.active = True
        if self.cam is not None:
            mw = self.cam.matrix_world
            self.eye, self.rot, self.scale = mw.to_translation(), mw.to_quaternion(), mw.to_scale()
        else:
            rv3d = self.rv3d
            if rv3d.view_perspective == 'ORTHO':
                rv3d.view_perspective = 'PERSP'
            self.rot = rv3d.view_rotation.copy()
            self.eye = rv3d.view_location + self.rot @ Vector((0.0, 0.0, rv3d.view_distance))
        self._header(context)

    def _header(self, context):
        context.area.header_text_set(
            f"Fly {_prefs().fly_speed:.1f} m/s     W/A/S/D move    Q/E down/up    Shift faster    "
            f"Wheel changes speed    release the right button to stop")

    def _apply(self, context):
        if self.cam is not None:
            self.cam.matrix_world = Matrix.LocRotScale(self.eye, self.rot, self.scale)
        else:
            # the view orbits a pivot view_distance in front of the eye: move the pivot with the eye (as Unity does)
            rv3d = self.rv3d
            rv3d.view_rotation = self.rot
            rv3d.view_location = self.eye - self.rot @ Vector((0.0, 0.0, rv3d.view_distance))
        context.area.tag_redraw()

    # ---------------------------------------------------------------- events
    def modal(self, context, event):
        et, ev = event.type, event.value
        if et == 'TIMER':
            self._tick(context)
            return {'PASS_THROUGH'}
        if et == 'RIGHTMOUSE' and ev == 'RELEASE':
            return self._finish(context, click=not self.active)
        if et in {'ESC', 'WINDOW_DEACTIVATE'}:
            return self._finish(context, click=False)
        if et == 'MOUSEMOVE':
            self._look(context, event)
        elif et in MOVE_KEYS:
            if ev == 'PRESS':
                self._begin(context)
                self.held.add(et)
            elif ev == 'RELEASE':
                self.held.discard(et)
        elif et in SHIFT_KEYS:
            if ev in {'PRESS', 'RELEASE'}:
                self.shift = ev == 'PRESS'
        elif et in {'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            self._begin(context)
            p = _prefs()
            p.fly_speed = min(1000.0, max(0.05, p.fly_speed * (1.25 if et == 'WHEELUPMOUSE' else 0.8)))
            self._header(context)
        return {'RUNNING_MODAL'}

    def _look(self, context, event):
        x, y = event.mouse_x, event.mouse_y
        dx, dy = x - self.last_mouse[0], y - self.last_mouse[1]
        self.last_mouse = (x, y)
        if not self.active:
            if abs(x - self.start_mouse[0]) + abs(y - self.start_mouse[1]) < 4:
                return                      # still a click
            self._begin(context)
        if not self.looking:
            self.looking = True
            context.window.cursor_modal_set('NONE')
        p = _prefs()
        self.rot = fly_look(self.rot, dx, dy, p.sensitivity, p.invert_y)
        self._apply(context)
        # keep the hidden pointer inside the region so looking never stops at a screen edge
        r, m = context.region, 50
        if not (r.x + m < x < r.x + r.width - m and r.y + m < y < r.y + r.height - m):
            cx, cy = r.x + r.width // 2, r.y + r.height // 2
            context.window.cursor_warp(cx, cy)
            self.last_mouse = (cx, cy)

    def _tick(self, context):
        now = time.perf_counter()
        dt, self.t_last = min(now - self.t_last, 0.1), now
        move = Vector((0.0, 0.0, 0.0))
        for key in self.held:
            move += Vector(MOVE_KEYS[key])
        if move.length < 1e-6:
            self.move_time = 0.0
            return
        p = _prefs()
        self.move_time += dt
        speed = p.fly_speed * (p.shift_mult if self.shift else 1.0)
        if p.acceleration:
            speed *= 1.0 + 2.0 * min(1.0, self.move_time / 2.0)     # up to 3x after 2 s
        self.eye += (self.rot @ move.normalized()) * speed * dt
        self.moved = True
        self._apply(context)

    def _finish(self, context, click):
        context.window_manager.event_timer_remove(self.timer)
        if self.looking:
            context.window.cursor_modal_restore()
            context.window.cursor_warp(*self.start_mouse)
        if self.active:
            context.area.header_text_set(None)
        if self.cam is not None and self.moved:
            bpy.ops.ed.undo_push(message="Fly Camera")
        if click and self.menu:
            if self.menu_kind == 'PANEL':
                bpy.ops.wm.call_panel(name=self.menu)
            else:
                bpy.ops.wm.call_menu(name=self.menu)
        return {'FINISHED'}


# ---------------------------------------------------------------- keymaps
addon_keymaps = []


def _default_rmb_menu(km_name):
    """(name, kind) of the menu the built-in keymap opens on a plain right click in this keymap, or None."""
    km = bpy.context.window_manager.keyconfigs.default.keymaps.get(km_name)
    for kmi in (km.keymap_items if km else ()):
        if (kmi.type == 'RIGHTMOUSE' and kmi.value == 'PRESS' and kmi.idname in {'wm.call_menu', 'wm.call_panel'}
                and not (kmi.shift or kmi.ctrl or kmi.alt or kmi.oskey)):
            return kmi.properties.name, ('PANEL' if kmi.idname == 'wm.call_panel' else 'MENU')
    return None


def register_keymaps():
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is None:                      # background mode
        return
    p = _prefs()
    opt = {k: (getattr(p, k) if p else v) for k, v in KEYMAP_DEFAULTS.items()}
    active = wm.keyconfigs.active
    select_mouse = getattr(active.preferences, "select_mouse", 'LEFT') if active and active.preferences else 'LEFT'
    if select_mouse != 'RIGHT':         # with right-click select the right button belongs to selection
        for name, space in RMB_KEYMAPS:
            km = kc.keymaps.new(name=name, space_type=space)
            kmi = km.keymap_items.new(VIEW3D_OT_unity_fly.bl_idname, 'RIGHTMOUSE', 'PRESS', head=True)
            menu = _default_rmb_menu(name)
            if menu:
                kmi.properties.menu, kmi.properties.menu_kind = menu
            addon_keymaps.append((km, kmi))
    km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
    items = []
    if opt["alt_nav"]:
        items += [("view3d.rotate", 'LEFTMOUSE', 'CLICK_DRAG', {"alt": True}),   # drag only: Alt+click still selects
                  ("view3d.zoom", 'RIGHTMOUSE', 'PRESS', {"alt": True})]
    if opt["mmb_pan"]:
        items += [("view3d.move", 'MIDDLEMOUSE', 'PRESS', {})]
    if opt["f_frame"]:
        items += [("view3d.view_selected", 'F', 'PRESS', {}),
                  ("view3d.camera_to_view", 'F', 'PRESS', {"ctrl": True, "shift": True})]
    for idname, key, value, mods in items:
        addon_keymaps.append((km, km.keymap_items.new(idname, key, value, head=True, **mods)))


def unregister_keymaps():
    for km, kmi in addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (ReferenceError, RuntimeError):
            pass
    addon_keymaps.clear()


def _update_keymaps(self, context):
    unregister_keymaps()
    register_keymaps()


class UnityNavPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    fly_speed: FloatProperty(name="Fly Speed (m/s)", default=8.0, min=0.05, max=1000.0,
                             description="Base flying speed. The mouse wheel changes it while flying")
    shift_mult: FloatProperty(name="Shift Multiplier", default=3.0, min=1.0, max=20.0,
                              description="Speed multiplier while Shift is held")
    acceleration: BoolProperty(name="Acceleration", default=True,
                               description="Speed ramps up to 3x over 2 seconds while a move key is held")
    sensitivity: FloatProperty(name="Look Sensitivity", default=0.15, min=0.01, max=1.0,
                               description="Degrees of rotation per pixel of mouse movement")
    invert_y: BoolProperty(name="Invert Mouse Y", default=False)
    alt_nav: BoolProperty(name="Alt + Left Drag Orbits, Alt + Right Drag Zooms", default=True,
                          update=_update_keymaps)
    mmb_pan: BoolProperty(name="Middle Drag Pans", default=True, update=_update_keymaps,
                          description="Unity: middle-drag pans. Off: Blender's middle-drag orbit")
    f_frame: BoolProperty(name="F Frames the Selection, Ctrl+Shift+F Aligns the Camera to the View", default=True,
                          update=_update_keymaps)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.label(text="Hold the right mouse button in the 3D Viewport: move the mouse to look, W/A/S/D to move, "
                       "Q/E down/up.")
        col.label(text="Shift goes faster, the mouse wheel changes the speed. A right click without moving still "
                       "opens the context menu.")
        row = layout.row()
        c = row.column()
        c.label(text="Fly")
        c.prop(self, "fly_speed")
        c.prop(self, "shift_mult")
        c.prop(self, "acceleration")
        c = row.column()
        c.label(text="Look")
        c.prop(self, "sensitivity")
        c.prop(self, "invert_y")
        c = layout.column()
        c.label(text="Other Unity shortcuts")
        c.prop(self, "alt_nav")
        c.prop(self, "mmb_pan")
        c.prop(self, "f_frame")


classes = (UnityNavPreferences, VIEW3D_OT_unity_fly)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_keymaps()


def unregister():
    unregister_keymaps()
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
