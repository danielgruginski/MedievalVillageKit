import bpy
CODE=r"C:\Users\danie\AppData\Roaming\Claude\scratch-workspaces\ec03f06b-60f5-4d5d-94a9-dff3a56c5f56\f8ddc2b6-f8a4-41c6-98db-14b97d4348ea\scratch-2026-09-23-d49817\code"
bpy.data.texts["vk_leafgen"].from_string(open(CODE+r"\vk_leafgen.py",encoding="utf8").read())
_L={}
exec(bpy.data.texts["vk_tex"].as_string(),_L); exec(bpy.data.texts["vk_leafgen"].as_string(),_L)
_L["repaint_leaf_cell"]("willow",height=True)
print("willow cell applied; dry",_L["repaint_leaf_cell"]("willow",dry=True))
