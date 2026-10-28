using System.Collections.Generic;
using System.Linq;

namespace MedievalKit;

/// <summary>
/// Unity's Mono and .NET sort alike, with one exception that matters to a seed (measured 2026-10-28): ToList / ToArray
/// straight after an OrderBy or ThenBy of a single element skips its key in .NET, while Mono computes it, so a key that
/// draws a random number (<c>OrderBy(_ => rnd.Next())</c>) shifts every draw after it. Enumerating computes every key in
/// both, so the generators list a random order with <see cref="ToListKeyed{T}"/>.
/// </summary>
internal static class MonoLinq
{
    internal static List<T> ToListKeyed<T>(this IOrderedEnumerable<T> source)
    {
        var list = new List<T>();
        foreach (var x in source) list.Add(x);
        return list;
    }
}
