"""
PCB Snap-Fit Holder for 1"x1"x1mm Sensor PCB
Standalone test fixture for validating PCB fit before chamber integration

Design Features:
- Vertical drop-in insertion from top
- Spring clips in corners for retention
- Solid bottom platform for PCB to rest on
- Open airflow edges (minimal obstruction)
- Connector edge with 4mm x 2mm access cutout
- Low profile design
"""

import cadquery as cq

# PCB Dimensions
PCB_WIDTH = 25.4  # mm (1 inch)
PCB_DEPTH = 25.4  # mm (1 inch)
PCB_THICKNESS = 1.0  # mm
PCB_HOLE_DIA = 3.0  # mm (mounting holes in corners - corrected measurement)
PCB_HOLE_OFFSET = 0.75  # mm from edge to hole center (closer to edge)

# Holder dimensions
WALL_THICKNESS = 1.2  # mm (thinner walls for low profile)
BASE_THICKNESS = 1.125  # mm (75% of 1.5mm - reduced for weight/material)
HOLDER_HEIGHT = 8.0  # mm total height (above base)
PCB_PLATFORM_HEIGHT = 1.125  # mm height of platform PCB sits on (75% of 1.5mm)
PCB_WALL_CLEARANCE = 1.5  # mm extra clearance between PCB edge and walls (increased from 0.5mm)

# Spring clip dimensions
CLIP_LENGTH = 2.0  # mm thickness (thin for flexibility)
CLIP_THICKNESS = 0.6  # mm thickness (thin for flexibility)
CLIP_OVERHANG = 1.6  # mm how far clip extends over PCB edge

# Connector cutout
CONNECTOR_WIDTH = 4.0  # mm
CONNECTOR_HEIGHT = 2.0  # mm (extends above PCB top)

# Corner support dimensions
CORNER_SIZE = 6.35  # mm (1/4 inch - the clean area in corners)

def create_pcb_holder():
    """
    Create a snap-fit holder for the sensor PCB
    PCB drops into recessed platform, spring clips press down on top surface corners
    """

    # Calculate overall dimensions
    # Base needs to extend to support the walls at their new position
    outer_width = PCB_WIDTH + 2 * PCB_WALL_CLEARANCE + 2 * WALL_THICKNESS
    outer_depth = PCB_DEPTH + 2 * PCB_WALL_CLEARANCE + 2 * WALL_THICKNESS

    # Wall rim height (the highest point)
    rim_height = PCB_PLATFORM_HEIGHT + PCB_THICKNESS + 2.0  # 2mm above PCB top (increased from 1mm)

    # Create base
    base = (
        cq.Workplane("XY")
        .rect(outer_width, outer_depth)
        .extrude(BASE_THICKNESS)
    )

    # Create corner walls only (1/4 of each side length)
    # This keeps the center open for airflow
    corner_wall_length = PCB_WIDTH / 4  # 1/4 of side

    holder = base

    # Define the four corners and their wall segments
    corners = [
        # (sign_x, sign_y)
        (-1, -1),  # Front-left
        (1, -1),   # Front-right
        (-1, 1),   # Back-left
        (1, 1),    # Back-right
    ]

    for sign_x, sign_y in corners:
        # Each corner gets an L-shaped wall
        # Calculate the outer corner position (with extra clearance for PCB)
        outer_x = sign_x * (PCB_WIDTH/2 + PCB_WALL_CLEARANCE + WALL_THICKNESS/2)
        outer_y = sign_y * (PCB_DEPTH/2 + PCB_WALL_CLEARANCE + WALL_THICKNESS/2)

        # X-direction wall segment (horizontal from corner)
        wall_x = (
            cq.Workplane("XY")
            .workplane(offset=BASE_THICKNESS)
            .center(outer_x - sign_x * corner_wall_length/2, outer_y)
            .rect(corner_wall_length, WALL_THICKNESS)
            .extrude(rim_height)
        )
        holder = holder.union(wall_x)

        # Y-direction wall segment (vertical from corner)
        wall_y = (
            cq.Workplane("XY")
            .workplane(offset=BASE_THICKNESS)
            .center(outer_x, outer_y - sign_y * corner_wall_length/2)
            .rect(WALL_THICKNESS, corner_wall_length)
            .extrude(rim_height)
        )
        holder = holder.union(wall_y)

    # Create recessed PCB platform (inside the walls, lower than rim)
    # Platform is at BASE_THICKNESS, rim top is at BASE_THICKNESS + rim_height
    platform_inset = 0.5  # mm inset from inner wall for clearance
    platform = (
        cq.Workplane("XY")
        .workplane(offset=BASE_THICKNESS)
        .rect(PCB_WIDTH - 2*platform_inset, PCB_DEPTH - 2*platform_inset)
        .extrude(PCB_PLATFORM_HEIGHT)
    )

    holder = holder.union(platform)

    # Calculate Z positions
    platform_top_z = BASE_THICKNESS + PCB_PLATFORM_HEIGHT  # PCB sits here
    pcb_top_z = platform_top_z + PCB_THICKNESS
    rim_top_z = BASE_THICKNESS + rim_height  # Wall rim top

    # Add integrated clips that are part of the corner walls
    # Clips extend inward from walls at full wall height for better strength
    # They cantilever over the PCB edge to hold it down

    clip_overhang = CLIP_OVERHANG  # mm - how far clip extends inward over PCB edge (doubled from 0.4mm)
    clip_length = CLIP_LENGTH    # mm - length along the wall
    clip_thickness = CLIP_THICKNESS  # mm - thin enough to flex

    for sign_x, sign_y in corners:
        # Create clips as horizontal tabs on walls
        # They extend inward over the PCB edge to hold it down
        # Positioned one clip thickness below the top of the wall

        # Clip on horizontal wall arm (sits on top of Y-direction wall)
        # Position is on inner edge of wall, centered along wall segment
        wall_y_inner = sign_y * (PCB_DEPTH/2 + PCB_WALL_CLEARANCE)  # Inner edge of wall
        wall_x_center = sign_x * (PCB_WIDTH/2 - corner_wall_length/2)  # Center of wall segment

        clip_x = (
            cq.Workplane("XY")
            .workplane(offset=rim_top_z - clip_thickness)  # Start one clip thickness below top
            .center(wall_x_center, wall_y_inner - sign_y * clip_overhang/2)
            .rect(clip_length, clip_overhang)
            .extrude(clip_thickness)  # Thin for flexibility
        )
        holder = holder.union(clip_x)

        # Clip on vertical wall arm (sits on top of X-direction wall)
        wall_x_inner = sign_x * (PCB_WIDTH/2 + PCB_WALL_CLEARANCE)  # Inner edge of wall
        wall_y_center = sign_y * (PCB_DEPTH/2 - corner_wall_length/2)  # Center of wall segment

        clip_y = (
            cq.Workplane("XY")
            .workplane(offset=rim_top_z - clip_thickness)  # Start one clip thickness below top
            .center(wall_x_inner - sign_x * clip_overhang/2, wall_y_center)
            .rect(clip_overhang, clip_length)
            .extrude(clip_thickness)  # Thin for flexibility
        )
        holder = holder.union(clip_y)

    # Cut connector access in corner walls on +Y edge (back edge - connector edge)
    # Cutout is 4mm x 2mm, centered on edge
    # Need to cut notches in both back corner walls
    for sign_x in [-1, 1]:
        connector_notch = (
            cq.Workplane("XY")
            .workplane(offset=pcb_top_z - 0.1)
            .center(sign_x * corner_wall_length/4, PCB_DEPTH/2 + WALL_THICKNESS/2)
            .rect(CONNECTOR_WIDTH, WALL_THICKNESS + 2)
            .extrude(CONNECTOR_HEIGHT + 1)
        )
        holder = holder.cut(connector_notch)

    # No need for airflow edge cutouts - center is already open with corner-only walls!

    # Add alignment posts that fit into PCB mounting holes (optional, for better alignment)
    # These are 2.6mm diameter x 1mm tall posts
    post_dia = 2.6  # mm (slightly smaller than 3mm holes for clearance)
    post_height = 1.0  # mm (reduced for lower profile)
    post_adjustment = 0.0625  # mm (1/16mm) - move posts toward center away from walls

    hole_positions = [
        (-PCB_WIDTH/2 + PCB_HOLE_OFFSET + PCB_HOLE_DIA/2 + post_adjustment, -PCB_DEPTH/2 + PCB_HOLE_OFFSET + PCB_HOLE_DIA/2 + post_adjustment),
        (PCB_WIDTH/2 - PCB_HOLE_OFFSET - PCB_HOLE_DIA/2 - post_adjustment, -PCB_DEPTH/2 + PCB_HOLE_OFFSET + PCB_HOLE_DIA/2 + post_adjustment),
        (-PCB_WIDTH/2 + PCB_HOLE_OFFSET + PCB_HOLE_DIA/2 + post_adjustment, PCB_DEPTH/2 - PCB_HOLE_OFFSET - PCB_HOLE_DIA/2 - post_adjustment),
        (PCB_WIDTH/2 - PCB_HOLE_OFFSET - PCB_HOLE_DIA/2 - post_adjustment, PCB_DEPTH/2 - PCB_HOLE_OFFSET - PCB_HOLE_DIA/2 - post_adjustment),
    ]

    for x, y in hole_positions:
        post = (
            cq.Workplane("XY")
            .workplane(offset=BASE_THICKNESS + PCB_PLATFORM_HEIGHT)
            .center(x, y)
            .circle(post_dia/2)
            .extrude(post_height)
        )
        holder = holder.union(post)

    return holder

if __name__ == "__main__":
    print("=" * 60)
    print("PCB SNAP-FIT HOLDER GENERATOR")
    print("=" * 60)
    print()
    print(f"PCB dimensions: {PCB_WIDTH}mm x {PCB_DEPTH}mm x {PCB_THICKNESS}mm")
    print(f"Holder outer dimensions: {PCB_WIDTH + 2*WALL_THICKNESS}mm x {PCB_DEPTH + 2*WALL_THICKNESS}mm")
    print(f"Total height: {BASE_THICKNESS + PCB_PLATFORM_HEIGHT + PCB_THICKNESS + 2}mm")
    print()
    print("Design features:")
    print("  - Vertical drop-in insertion from top")
    print("  - Spring clips in corners for retention")
    print("  - Solid bottom platform")
    print("  - Open airflow edges (minimal obstruction)")
    print("  - Connector edge with 4mm x 2mm access cutout")
    print("  - Alignment posts for PCB mounting holes")
    print()

    print("Generating PCB holder...")
    holder = create_pcb_holder()

    # Export to STL
    cq.exporters.export(holder, "pcb_holder.stl")
    print("  Exported: pcb_holder.stl")

    print()
    print("=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print()
    print("Assembly instructions:")
    print("1. Drop PCB into holder from top")
    print("2. Press down gently - corner clips will flex and snap over PCB edges")
    print("3. PCB should sit flush on platform with clips holding it securely")
    print("4. To remove: gently flex clips outward and lift PCB")
    print()
    print("Testing notes:")
    print("- Connector edge is on +Y side (back)")
    print("- Airflow edges are on +X and -X sides (left/right)")
    print("- If clips are too tight/loose, adjust CLIP_OVERHANG in code")
    print("- If PCB rocks, check alignment post heights")
