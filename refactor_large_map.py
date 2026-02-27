import sys

with open('code/game.py', 'r') as f:
    lines = f.readlines()

out_lines = []
large_map_lines = []
in_large_map = False

for line in lines:
    if "# --- DESSIN GRANDE CARTE INTERACTIVE ---" in line:
        in_large_map = True
        large_map_lines.append(line)
        continue
    
    if in_large_map:
        # Check end of block
        if "    # Infos Textes (THRUST" in line:
            in_large_map = False
            out_lines.append(line)
        else:
            large_map_lines.append(line)
    else:
        out_lines.append(line)

# Now out_lines has everything EXCEPT the large map block.
# Let's insert the large_map_lines into the main loop, before HUD overlay
final_lines = []
for line in out_lines:
    if "def dessiner_dashboard(" in line:
        final_lines.append(line)
        # Add early return
        final_lines.append("    if show_large_map: return\n")
    elif "# 2. HUD Overlay (Haut)" in line:
        final_lines.extend(large_map_lines)
        final_lines.append(line)
    elif "if not args.no_hud:" in line:
        final_lines.append("    if not args.no_hud and not show_large_map:\n")
    else:
        final_lines.append(line)

with open('code/game.py', 'w') as f:
    f.writelines(final_lines)

print("Refactoring done.")
