"""
Print Layout for Transition Quadrants
Arranges transition quadrants for efficient printing on a 250mm x 220mm x 220mm bed
Imports the quadrant design from manifold_design.py

STEP-BY-STEP APPROACH:
Step 1: Orient one quadrant on its interior bolted edge (X=0 or Y=0 edge)
Step 2: Position with top-most portion near one print bed edge
Step 3: Keep bottom edge parallel to opposite print bed edge
Step 4: Position bottom corner as close to adjacent side as possible
"""

import cadquery as cq
import sys
import io

# Import the transition quadrant creation function BEFORE fixing stdout
# (manifold_design.py already does the stdout fix)
from manifold_design import create_transition_section_quadrant, TRANSITION_LENGTH

def create_print_layout():
    """
    Step 1: Create and orient a single quadrant on its bolted edge

    Quadrant geometry:
    - Tapers from 180mm x 180mm at bottom to ~24mm x 24mm at top
    - Height: 150mm
    - Interior edges at X=0, Y=0 (bolt to neighbors)
    - Outer edges at X=180mm, Y=180mm

    Target orientation:
    - Lay quadrant on its Y=0 edge (one of the interior bolted edges)
    - Top of quadrant (narrow, small end) near one build plate edge
    - Bottom edge (wide) parallel to opposite build plate edge
    - Bottom corner as close to adjacent side as possible
    """

    print("="*60)
    print("TRANSITION QUADRANT PRINT LAYOUT - STEP 1")
    print("="*60)
    print()
    print(f"Build volume: 250mm (H) x 220mm (W) x 220mm (D)")
    print(f"Quadrant dimensions (as modeled): ~180mm x 180mm x {TRANSITION_LENGTH}mm")
    print()

    # Create the quadrant
    print("Step 1: Generating quadrant...")
    quadrant = create_transition_section_quadrant()

    # The quadrant is modeled with:
    # - Bottom (wide) at Z=0, top (narrow) at Z=150
    # - Interior edges along X=0 and Y=0
    # - Outer edges at X=180, Y=180

    # STEP 1: Rotate to lay on the Y=0 edge (interior bolted edge)
    # Rotate 90° around Y axis so the Y=0 edge becomes the bottom
    print("Step 2: Rotating quadrant to lay on interior edge (Y=0 edge)...")
    quadrant = quadrant.rotate((0, 0, 0), (0, 1, 0), -90)

    # After this rotation:
    # - What was +Z (top) is now +X
    # - What was +X (outer edge) is now +Z
    # - The Y=0 edge is now flat on the build plate
    # - Original bottom (Z=0) is now at X=0
    # - Original top (Z=150) is now at X=150

    print("Step 3: Positioning quadrant on build plate...")
    # After rotation, we need to position according to requirements:
    # - Top-most portion (narrow end, was Z=150, now at X=150) near one edge (Y=0)
    # - Bottom edge (wide end, was Z=0, now at X=0) parallel to opposite edge (Y=220)
    # - Bottom corner as close to adjacent side as possible (X near 0)

    # The Y=0 interior edge is now the bottom surface (resting on build plate)
    # After rotation the part needs translation to position correctly

    # Since we rotated around Y axis at origin:
    # - The Y=0 plane is now flat (good - this is our bolted edge)
    # - We need to translate so the narrow top is near Y=0
    # - And the wide bottom extends toward Y=220
    # - And position it close to X=0

    # Actually, after rotating -90° around Y:
    # - Original (X, Y, Z) becomes (Z, Y, -X)
    # - So original top at Z=150 becomes X=-150
    # - We want the top (narrow, now at negative X) near the Y=0 edge of build plate
    # - Translate X by +150 to bring narrow end near X=0

    quadrant = quadrant.translate((150, 0, 0))

    # Now the narrow top should be near X=0
    # The wide bottom should be near X=150
    # The interior Y=0 edge should be at Z=0 (build plate)
    # But we need to ensure it sits on the build plate properly

    # Translate up in Z to ensure the Y=0 edge sits on Z=0
    # The Y=0 edge after rotation should be centered, we need to lift it
    # Since the quadrant interior edge was at Y=0 originally, and it's a flat edge,
    # we may need to translate in Z to get it to sit properly on the build plate

    # For a quadrant with interior edges at X=0, Y=0 and going to X=180, Y=180:
    # The Y=0 edge is a plane - after rotating it becomes the bottom
    # We need to position close to build plate edges

    # Move to have narrow end (now at X≈0) close to Y=0 build plate edge
    # The quadrant spans in Y from 0 to 180, so it's already positioned
    # Just need to ensure it's sitting on Z=0 and near X=0, Y=0 corner

    quadrant = quadrant.translate((0, 0, 0))  # May need adjustment after checking geometry

    print(f"  Positioned quadrant:")
    print(f"    - Narrow end (top) near build plate edges")
    print(f"    - Wide end (bottom) extends into build volume")
    print(f"    - Resting on Y=0 interior edge")
    print()

    print("="*60)
    print("Step 4: Creating L-shaped platform...")
    print("="*60)
    print()

    # Platform specifications:
    # - 3mm high, 3mm wide
    # - Starts at X=-3mm (3mm in negative X direction)
    # - At the corner of sloping surface resting on print plate
    # - Runs along Y axis for 110mm
    # - Then turns 90° to run in positive X direction for 75mm

    platform_width = 3  # mm
    platform_height = 5  # mm

    # Create 3 parallel platforms running along Y axis
    # Each is 110mm long, spaced 20mm apart in Y direction

    # Platform 1 - runs along Y axis (x-most platform) - now 10mm tall
    # Starting at X=-3, Y=0, running to Y=110, then moved -160mm+80mm+10mm+10mm+10mm=-50mm in X
    platform1 = (
        cq.Workplane("XY")
        .workplane(offset=0)
        .center(-3-160+80+10+10+10, 55)  # Center at X=-53, Y midpoint (110/2 = 55)
        .rect(platform_width, 110)  # 3mm wide, 110mm long in Y
        .extrude(10)  # 10mm tall
    )

    # Platform 1b - duplicate of platform 1, 20mm in positive X direction from platform 1
    platform1b = (
        cq.Workplane("XY")
        .workplane(offset=0)
        .center(-3-160+80+10+10+10+20, 55)  # X=-33, Y=55
        .rect(platform_width, 110)  # 3mm wide, 110mm long in Y
        .extrude(10)  # 10mm tall
    )

    # Platform 2 - 20mm in negative Y from platform 1, then moved +20mm Y, -20mm X, then +10mm X, then +5mm X
    platform2 = (
        cq.Workplane("XY")
        .workplane(offset=0)
        .center(-3-20+10+5, 35+20)  # X=-8, Y=55 (35+20)
        .rect(platform_width, 110)  # 3mm wide, 110mm long in Y
        .extrude(platform_height)  # 5mm tall
    )

    # Platform 3 - 20mm in negative Y from platform 2, then moved +40mm Y, -40mm X from original, then +10mm X, then +5mm X
    platform3 = (
        cq.Workplane("XY")
        .workplane(offset=0)
        .center(-3-40+10+5, 15+40)  # X=-28, Y=55 (15+40)
        .rect(platform_width, 110)  # 3mm wide, 110mm long in Y
        .extrude(platform_height)  # 5mm tall
    )

    # Combine platforms
    l_platform = platform1.union(platform1b).union(platform2).union(platform3)

    # Rotate platform 180 degrees on the print plate (around Z axis)
    l_platform = l_platform.rotate((0, 0, 0), (0, 0, 1), 180)

    # Move platform: 150mm in X direction, 180mm in positive Y direction
    l_platform = l_platform.translate((150, 180, 0))

    print(f"  Created 4 platforms:")
    print(f"    - Width: {platform_width}mm")
    print(f"    - Platform 1 & 1b: 10mm tall (x-most platforms)")
    print(f"    - Platform 1b: +20mm X from Platform 1")
    print(f"    - Platforms 2 & 3: 5mm tall")
    print(f"    - Each platform: 110mm long along Y axis")
    print(f"    - Platform 1: Base position")
    print(f"    - Platform 2: +20mm Y, -20mm X from parallel spacing")
    print(f"    - Platform 3: +40mm Y, -40mm X from parallel spacing")
    print(f"    - Rotated 180° around Z axis")
    print(f"    - Translated +150mm in X direction, +180mm in Y direction")
    print()

    print("="*60)
    print("Step 5: Creating second quadrant...")
    print("="*60)
    print()

    # Create second quadrant with same orientation as first
    print("  Generating second quadrant...")
    quadrant2 = create_transition_section_quadrant()

    # Apply same rotation as first quadrant (lay on interior edge)
    quadrant2 = quadrant2.rotate((0, 0, 0), (0, 1, 0), -90)

    # Apply same initial positioning as first quadrant
    quadrant2 = quadrant2.translate((150, 0, 0))

    # Now offset from first quadrant: +40mm-10mm = +30mm X, +10mm Y, +5mm Z
    quadrant2 = quadrant2.translate((30, 10, 5))

    print(f"  Second quadrant positioned:")
    print(f"    - Same orientation as first quadrant")
    print(f"    - Offset: +30mm X, +10mm Y, +5mm Z from first")
    print()

    print("="*60)
    print("Step 6: Creating third quadrant...")
    print("="*60)
    print()

    # Create third quadrant with same orientation
    print("  Generating third quadrant...")
    quadrant3 = create_transition_section_quadrant()

    # Apply same rotation as first quadrant (lay on interior edge)
    quadrant3 = quadrant3.rotate((0, 0, 0), (0, 1, 0), -90)

    # Apply same initial positioning as first quadrant
    quadrant3 = quadrant3.translate((150, 0, 0))

    # Position relative to quadrant 2: +35mm X, +10mm Y, +5mm Z from quadrant 2
    # Quadrant 2 is at: +30mm X, +10mm Y, +5mm Z from quadrant 1
    # So quadrant 3 is at: +30+35=65mm X, +10+10=20mm Y, +5+5=10mm Z from quadrant 1
    # Then moved -20mm X, then +10mm X = +55mm X total
    quadrant3 = quadrant3.translate((55, 20, 10))

    print(f"  Third quadrant positioned:")
    print(f"    - Same orientation as first quadrant")
    print(f"    - Offset: +35mm X, +10mm Y, +5mm Z from quadrant 2")
    print(f"    - Total offset from quadrant 1: +55mm X, +20mm Y, +10mm Z")
    print()

    # Create assembly with all three quadrants and platforms
    assembly = quadrant.union(quadrant2).union(quadrant3).union(l_platform)

    # Export the layout
    filename = "transition_quadrant_print_layout.stl"
    cq.exporters.export(assembly, filename)
    print(f"Exported: {filename}")
    print()

    print("="*60)
    print("NESTED LAYOUT COMPLETE - 3 QUADRANTS")
    print("="*60)
    print()
    print("Layout summary:")
    print("  - 3 quadrants nested together!")
    print("  - All oriented on interior bolted edge")
    print("  - Quadrant 2: +30mm X, +10mm Y, +5mm Z from quadrant 1")
    print("  - Quadrant 3: +35mm X, +10mm Y, +5mm Z from quadrant 2")
    print("  - Total: Quadrant 3 at +55mm X, +20mm Y, +10mm Z from quadrant 1")
    print("  - 4 support platforms (3mm wide, varying heights)")
    print(f"  - Estimated footprint: ~220mm (W) x ~200mm (D) x ~195mm (H)")
    print()
    print("Platform details:")
    print(f"  - Platforms 1 & 1b: 10mm tall")
    print(f"  - Platforms 2 & 3: 5mm tall")
    print(f"  - Can be easily removed after printing")
    print()
    print("Print this layout once, then print 1 more quadrant separately = 4 total!")
    print()

    return assembly

if __name__ == "__main__":
    create_print_layout()
