# Godot light probes

Small SceneTree scripts that measured how Godot 4.7 lights a floor, behind the light conversions in
`docs/GODOT_EXPORT.md` section 4. Each renders into a SubViewport (needs a window) and prints its readings:

```sh
GODOT=C:/Users/danie/Downloads/Godot_v4.7.2-stable_mono_win64/Godot_v4.7.2-stable_mono_win64_console.exe
cp tools/godot_probes/*.gd <project>/_scratch/      # any res:// folder of a Godot project
"$GODOT" --path <project> --resolution 320x180 --script res://_scratch/spot_cone.gd
```

- `omni_spot_falloff.gd [energy] [omni attenuation] [sun energy]`: a spot and an omni 5 m over a floor. Mind that
  `albedo_color` is sRGB: 0.5 is 0.214 linear.
- `spot_cone.gd`: the spot's pool across, for several `spot_angle_attenuation` values (Godot 4.7: `1 - rim^(1/a)`).
- `area_light.gd`: an AreaLight3D (normalized and not) against an omni of the same energy.
