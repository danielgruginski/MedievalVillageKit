using Godot;

namespace MedievalKit;

/// <summary>
/// The see-through's hidden check: does anything the hole would open stand over the walker's upper body? A camera owns
/// one (<see cref="KitCamera"/>) and calls <see cref="Look"/> each frame after it has set the see-through's globals; it
/// reads <see cref="Cover"/> and opens or shuts the hole by it. Unity: KitSeeThroughProbe.
/// How (Godot): a 32 x 40 SubViewport sharing the level's world, its camera at the game camera framing the walker from
/// its waist to over its head, with <see cref="KitSeeThrough.ProbeCameraBit"/> in its cull mask: the kit's shader sees it
/// (CAMERA_VISIBLE_LAYERS) and draws only what the hole would open, flat magenta, a building's tag in green. Its own
/// environment (black, no ambient, linear tone map) keeps everything else dark or lit as usual, never magenta with a low
/// green. The view is read back the frame after it renders (an image read, 5 KB), at most <see cref="Rate"/> times a
/// second: the magenta share of an ellipse over the body is <see cref="Cover"/>, each tag's count decides the buildings
/// (<see cref="KitSeeThrough.Probed"/>).
/// </summary>
public partial class KitSeeThroughProbe : SubViewport
{
    public const int W = 32, H = 40;
    /// <summary>the frame's width at the walker (m); its height follows the image's shape</summary>
    public const float FrameWidth = 0.8f;

    /// <summary>the share of the walker's upper body behind what the hole would open, at the last read (0..1)</summary>
    public float Cover { get; private set; }
    /// <summary>reads so far (0: no answer yet)</summary>
    public int Reads { get; private set; }
    /// <summary>renders a second at most</summary>
    public float Rate = 15f;

    Camera3D view, cam;
    bool pending;
    int gen, asked;
    double last = -1;
    readonly int[] tags = new int[KitSeeThrough.MaxTag + 1];

    /// <summary>a hidden check for the camera `view` (added under it)</summary>
    public static KitSeeThroughProbe For(Camera3D view)
    {
        var p = new KitSeeThroughProbe { Name = "KitSeeThroughProbe", view = view };
        view.AddChild(p);
        return p;
    }

    public override void _Ready()
    {
        Size = new Vector2I(W, H);
        RenderTargetUpdateMode = UpdateMode.Disabled;
        RenderTargetClearMode = ClearMode.Always;
        Msaa3D = Msaa.Disabled;
        ScreenSpaceAA = ScreenSpaceAAEnum.Disabled;
        UseTaa = false;
        PositionalShadowAtlasSize = 0;
        cam = new Camera3D
        {
            Name = "ProbeCamera", Near = 0.3f, KeepAspect = Camera3D.KeepAspectEnum.Height,
            Environment = new Environment
            {
                BackgroundMode = Environment.BGMode.Color, BackgroundColor = Colors.Black,
                AmbientLightSource = Environment.AmbientSource.Color, AmbientLightColor = Colors.Black,
                ReflectedLightSource = Environment.ReflectionSource.Disabled, TonemapMode = Environment.ToneMapper.Linear,
            },
            Attributes = new CameraAttributesPractical(),
        };
        AddChild(cam);
        cam.MakeCurrent();
    }

    /// <summary>render the walker's view (feet: its feet, world; chest: its chest's height over them) unless a read is
    /// due; the see-through's globals must be set for this frame</summary>
    public void Look(Vector3 feet, float chest)
    {
        if (cam == null || view == null) return;
        if (pending) { pending = false; Read(); return; }                // rendered at the end of the last frame
        double now = Time.GetTicksMsec() / 1000.0;
        if (last >= 0 && now - last < 1.0 / Mathf.Max(1f, Rate)) return;
        last = now;
        var from = view.GlobalPosition;
        var at = feet + Vector3.Up * (1.4f * chest);                    // between its waist and its head
        var dv = at - from;
        float dist = dv.Length();
        if (dist < 1f) return;
        float frameH = FrameWidth * H / W;
        cam.GlobalTransform = new Transform3D(Basis.LookingAt(dv / dist, Vector3.Up), from);
        cam.Fov = Mathf.RadToDeg(2f * Mathf.Atan(0.5f * frameH / dist));
        cam.Far = dist + 3f;
        cam.CullMask = view.CullMask | KitSeeThrough.ProbeCameraBit;
        RenderTargetUpdateMode = UpdateMode.Once;
        pending = true;
        asked = gen;
    }

    /// <summary>drop the answer (and a read still on its way): the walker was moved (a level's door, a teleport)</summary>
    public void Forget()
    {
        gen++;
        pending = false;
        Cover = 0f;
        Reads = 0;
        last = -1;
        KitSeeThrough.Probed(null, 0);
    }

    void Read()
    {
        if (asked != gen) return;
        var img = GetTexture()?.GetImage();
        if (img == null || img.GetWidth() != W || img.GetHeight() != H) return;
        int hit = 0, all = 0;
        System.Array.Clear(tags, 0, tags.Length);
        for (int y = 0; y < H; y++)
        {
            float v = (y + 0.5f) / H * 2f - 1f;
            for (int x = 0; x < W; x++)
            {
                float u = (x + 0.5f) / W * 2f - 1f;
                if (u * u / 0.5f + v * v > 1f) continue;               // the body: an ellipse 0.57 m wide, the frame's height
                all++;
                var c = img.GetPixel(x, y);
                if (c.R < 0.94f || c.B < 0.94f || c.G > 0.72f) continue;   // the kit's view: magenta, a tag's green under 0.66
                hit++;
                int tg = Mathf.RoundToInt(c.SrgbToLinear().G * 255f);      // a building's tag (0: not a building's)
                if (tg > 0 && tg < tags.Length) tags[tg]++;
            }
        }
        Cover = all > 0 ? (float)hit / all : 0f;
        Reads++;
        KitSeeThrough.Probed(tags, all);
    }
}
