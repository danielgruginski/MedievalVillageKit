using Godot;

namespace MedievalKit;

/// <summary>
/// The see-through's caps, baked (<see cref="KitSeeThroughCaps"/>): each cap mesh made ahead -- `kit_cli -- bakecaps`
/// (Editor/KitSeeThroughCapsBake.cs) -- for every piece, cut and set of solid materials the built levels use, kept in
/// <see cref="Path"/>. A level then registers its caps without cutting a mesh in play (Godot can read a mesh in a game,
/// but each read waits on the GPU: a level of a few hundred pieces stalls). An entry whose source mesh changed since the
/// bake (re-exported: another vertex count or bounds) is ignored and its cap made again in play. Unity:
/// KitSeeThroughCapBank (Resources "KitSeeThroughCaps").
/// </summary>
[GlobalClass]
public partial class KitSeeThroughCapBank : Resource
{
    public const string Path = KitPaths.Root + "see_through_caps.res";

    [Export] public Godot.Collections.Array<KitSeeThroughCapEntry> Entries = new();
    [Export(PropertyHint.MultilineText)] public string Report = "";
}
