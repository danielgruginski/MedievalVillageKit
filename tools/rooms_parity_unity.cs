// The Unity side of tools/rooms_parity.py: the room generators' levels (the runs of the Godot addon's
// KitRoomTools.Runs, seeds 1..3) built by the Unity package's KitRoom in a preview scene, one JSON object each, written
// to OUT. Paste into an editor run-command tool (the Unity MCP's Unity_RunCommand) or an editor script; it reaches the
// kit by reflection, as a sandboxed runner that does not reference the package must (LEVEL_BUILDING 2.1). Godot side:
// kit_cli -- rooms dump all 3 1 <out.jsonl>; then: py tools/rooms_parity.py <unity.jsonl> <godot.jsonl>
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;

internal class CommandScript : IRunCommand
{
    const string OUT = "Logs/MedievalKit/rooms_dump_unity.jsonl";
    const int SEEDS = 3;

    static Type T(string n) => AppDomain.CurrentDomain.GetAssemblies().Select(a => a.GetType(n)).First(t => t != null);
    static object G(object o, string f) => o.GetType().GetField(f).GetValue(o);
    static void S(object o, string f, object v) => o.GetType().GetField(f).SetValue(o, v);
    static string Q(string s) => s == null ? "null" : "\"" + s.Replace("\\", "\\\\").Replace("\"", "\\\"").Replace("\n", "\\n").Replace("\r", "\\r").Replace("\t", "\\t") + "\"";
    static string N(double v) => v.ToString("R", CultureInfo.InvariantCulture);

    public void Execute(ExecutionResult result)
    {
        var tRoom = T("MedievalKit.KitRoom"); var tRules = T("MedievalKit.KitInteriorRules");
        var tSpawn = T("MedievalKit.KitSpawn"); var tLink = T("MedievalKit.KitLink"); var tEnc = T("MedievalKit.KitEncounter");
        var rules = AssetDatabase.LoadAssetAtPath("Packages/com.danielgruginski.medievalkit/Generated/KitInteriorRules.asset", tRules);
        if (rules == null) { result.LogError("no rules"); return; }
        var runs = new List<(string, Action<object, int>)>();
        Action<object, string, string, object> set = (room, opt, f, v) => S(G(room, opt), f, v);
        Action<object, string> call = (room, m) => tRoom.GetMethod(m).Invoke(room, null);
        runs.Add(("cave maze", (r, sd) => { set(r, "cave", "seed", sd); call(r, "RandomCave"); }));
        runs.Add(("cave open", (r, sd) => { set(r, "cave", "seed", sd); set(r, "cave", "layout", "Open"); call(r, "RandomCave"); }));
        foreach (var th in new[] { "Dungeon", "Crypt", "Warren", "Hideout" })
            runs.Add(("dungeon " + th, (r, sd) => { set(r, "dungeon", "seed", sd); set(r, "dungeon", "theme", th); call(r, "RandomDungeon"); }));
        runs.Add(("sewer", (r, sd) => { set(r, "sewer", "seed", sd); call(r, "RandomSewer"); }));
        runs.Add(("sewer large", (r, sd) => { set(r, "sewer", "seed", sd); set(r, "sewer", "nc", 40); set(r, "sewer", "nr", 28); set(r, "sewer", "deep", "@deep"); call(r, "RandomSewer"); }));
        foreach (var ft in new[] { new[] { "S", "N" }, new[] { "W", "E" }, new[] { "S", "E" }, new[] { "N", "W" } })
            runs.Add(("connector " + ft[0] + "-" + ft[1], (r, sd) => { set(r, "connector", "seed", sd); set(r, "connector", "from", ft[0]); set(r, "connector", "to", ft[1]); call(r, "RandomConnector"); }));
        foreach (var kind in new[] { "Cottage", "Townhouse", "Tavern", "Workshop" })
            runs.Add(("interior " + kind, (r, sd) => { set(r, "interior", "seed", sd); set(r, "interior", "kind", kind); call(r, "RandomInterior"); }));

        var scene = EditorSceneManager.NewPreviewScene();
        var sb = new StringBuilder();
        int n = 0;
        try
        {
            foreach (var (label, make) in runs)
                for (int sd = 1; sd <= SEEDS; sd++)
                {
                    var go = new GameObject("Dump");
                    UnityEngine.SceneManagement.SceneManager.MoveGameObjectToScene(go, scene);
                    try
                    {
                        var room = go.AddComponent(tRoom);
                        S(room, "rules", rules); S(room, "buildLights", false);
                        make(room, sd);
                        var parts = new List<string>();
                        foreach (var p in (IEnumerable)G(room, "placed"))
                            parts.Add("[" + Q((string)G(p, "piece")) + "," + Q((string)G(p, "what")) + "," + N(Math.Round((float)G(p, "x"), 3)) + "," + N(Math.Round((float)G(p, "y"), 3)) + "," + N(Math.Round((float)G(p, "z"), 3)) + "," + N(Math.Round((float)G(p, "rot"), 2)) + "]");
                        var sp = go.GetComponentsInChildren(tSpawn).Select(s => "[" + Q((string)G(s, "spawnId")) + "," + N(Math.Round(-s.transform.localPosition.x, 3)) + "," + N(Math.Round(-s.transform.localPosition.z, 3)) + "," + N(Math.Round((float)G(s, "facingDeg"), 2)) + "]");
                        var lk = go.GetComponentsInChildren(tLink).Select(l => (string)G(l, "linkId") + ":" + (string)G(l, "kind") + "->" + (string)G(l, "target")).OrderBy(s => s, StringComparer.Ordinal).Select(Q);
                        var en = go.GetComponentsInChildren(tEnc).Select(e => "[" + Q((string)G(e, "encounterId")) + "," + Q((string)G(e, "creature")) + "," + (int)G(e, "budget") + "," + e.transform.childCount + "]");
                        var notes = ((IEnumerable<string>)G(room, "notes")).Select(Q);
                        string rec = (string)G(room, "record");
                        sb.Append("{\"label\":" + Q(label) + ",\"seed\":" + sd + ",\"plan\":" + Q((string)G(room, "plan")) + ",\"record\":" + (string.IsNullOrWhiteSpace(rec) ? "{}" : rec) +
                                  ",\"placed\":[" + string.Join(",", parts) + "],\"spawns\":[" + string.Join(",", sp) + "],\"links\":[" + string.Join(",", lk) +
                                  "],\"encounters\":[" + string.Join(",", en) + "],\"notes\":[" + string.Join(",", notes) + "]}").Append('\n');
                        n++;
                    }
                    catch (Exception e) { sb.Append("{\"label\":" + Q(label) + ",\"seed\":" + sd + ",\"error\":" + Q(e.ToString()) + "}\n"); }
                    finally { UnityEngine.Object.DestroyImmediate(go); }
                }
        }
        finally { EditorSceneManager.ClosePreviewScene(scene); }
        System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(OUT));
        System.IO.File.WriteAllText(OUT, sb.ToString());
        result.Log("dumped {0} levels to {1}", n, OUT);
    }
}
