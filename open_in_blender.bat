@echo off
rem Opens the kit's .blend in Blender 4.4. The Blender MCP add-on (addon.py) starts its server on port 9876 by itself.
start "" "D:\Program Files\Blender Foundation\Blender 4.4\blender-launcher.exe" "%~dp0blender\medievalDiorama.blend"
