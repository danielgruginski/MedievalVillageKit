import sys
# usage: python splice.py target start_marker end_marker newfile   (replaces [start, end) with newfile contents)
p, a_m, b_m, nf = sys.argv[1:5]
s = open(p, encoding="utf8").read()
a = s.index(a_m); b = s.index(b_m, a)
new = open(nf, encoding="utf8").read()
if not new.endswith("\n"): new += "\n"
open(p, "w", encoding="utf8").write(s[:a] + new + s[b:])
print("spliced", a, b, len(new))
