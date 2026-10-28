#if TOOLS
using Godot;

namespace MedievalKit.Editor;

/// <summary>The kit's editor menu (Project > Tools), the counterpart of Unity's Tools > Medieval Kit.</summary>
[Tool]
public partial class MedievalKitPlugin : EditorPlugin
{
    const string Check = "Medieval Kit: Check Pieces", Build = "Medieval Kit: Build Layouts",
                 PlayStart = "Medieval Kit: Play From Start Level", WalkThis = "Medieval Kit: Walk This Level";

    public override void _EnterTree()
    {
        EnsureSettings();
        AddToolMenuItem(Check, Callable.From(() => new KitBuilder().CheckPieces(System.Array.Empty<string>())));
        AddToolMenuItem(Build, Callable.From(() => GD.Print(new KitBuilder().BuildAllLayouts())));
        AddToolMenuItem(PlayStart, Callable.From(() => Play("")));
        AddToolMenuItem(WalkThis, Callable.From(() =>
        {
            if (EditorInterface.Singleton.GetEditedSceneRoot() is KitLevel l) Play(l.LevelName);
            else GD.PushWarning("[MedievalKit] Walk This Level: the open scene is not a kit level (res://kit/layouts/)");
        }));
    }

    /// <summary>The project settings the kit's shaders need (FULL_PORT_PLAN phase 6): the see-through's two global
    /// uniforms (kit_see_through.gdshaderinc: a shader naming a global the project lacks does not compile) and the
    /// shroud's four (kit_shroud.gdshaderinc), and room for
    /// instance uniforms -- every kit material has some (the see-through's marks), and Godot gives each instance 16 slots
    /// of the global buffer, 65,536 by default: 4,096 instances, under one outdoor map's pieces. Saved once; Godot reads
    /// the buffer size at start, so the first time it asks for a restart.</summary>
    static void EnsureSettings()
    {
        bool changed = false, restart = false;
        foreach (var g in new[] { "kit_see_through", "kit_see_through_args", "kit_shroud_rect", "kit_shroud_args", "kit_shroud_args2" })
        {
            string key = "shader_globals/" + g;
            if (ProjectSettings.HasSetting(key)) continue;
            ProjectSettings.SetSetting(key, new Godot.Collections.Dictionary { { "type", "vec4" }, { "value", Vector4.Zero } });
            changed = true;
        }
        if (!ProjectSettings.HasSetting("shader_globals/kit_shroud_tex"))      // the shroud's distance field (KitShroud)
        {
            ProjectSettings.SetSetting("shader_globals/kit_shroud_tex", new Godot.Collections.Dictionary { { "type", "sampler2D" }, { "value", "" } });
            changed = true;
        }
        const string buffer = "rendering/limits/global_shader_variables/buffer_size";
        const int want = 1 << 20;
        if ((int)ProjectSettings.GetSetting(buffer, 65536) < want)
        {
            ProjectSettings.SetSetting(buffer, want);
            changed = restart = true;
        }
        if (!changed) return;
        ProjectSettings.Save();
        GD.Print("[MedievalKit] project settings added for the kit's shaders (the see-through's globals, the instance uniform buffer)"
                 + (restart ? ": restart the editor (Project > Reload Current Project) before running" : ""));
    }

    /// <summary>runs Walker/kit_play.tscn on `level` (empty: the world's start) with the test walker</summary>
    static void Play(string level)
    {
        using (var f = FileAccess.Open(KitPlayBoot.LevelFile, FileAccess.ModeFlags.Write)) f.StoreString(level);
        EditorInterface.Singleton.PlayCustomScene(KitPlayBoot.Scene);
    }

    public override void _ExitTree()
    {
        foreach (var m in new[] { Check, Build, PlayStart, WalkThis }) RemoveToolMenuItem(m);
    }
}
#endif
