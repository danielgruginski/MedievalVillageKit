namespace MedievalKit;

/// <summary>Where the kit's generated files live in a Godot project (src/export/gdx_export.py writes them, nothing
/// there is edited by hand; Unity: the package's Art/, Data/ and Generated/).</summary>
public static class KitPaths
{
    public const string Root = "res://kit/";
    public const string Models = Root + "models/";
    public const string Materials = Root + "materials/";
    public const string Textures = Root + "textures/";
    public const string Data = Root + "data/";
    public const string Pieces = Data + "pieces.json";
    public const string LayoutData = Data + "layouts/";      // <name>.json, from gdx_export_layout
    public const string LayoutScenes = Root + "layouts/";    // <name>.tscn, built from them (KitBuilder)
    public const string Addon = "res://addons/medieval_kit/";
    public const string Shaders = Addon + "Shaders/";
    public const string KitLit = Shaders + "KitLit";         // KitLit.gdshader and KitLitTwoSided.gdshader
}
