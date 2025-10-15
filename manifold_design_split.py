"""
Air Flow Manifold for Curing Cabinet - SPLIT VERSION
This version splits the large base plate into printable sections that bolt together

Design principles:
- Base split into 3x3 grid to fit print bed
- Sections bolt together with alignment pins
- Gasket grooves for air-tight seal between sections
- All other features same as main design
"""

import cadquery as cq
import math

# Import parameters from main design
from manifold_design import (
    MANIFOLD_BASE_SIZE, TARGET_SPEED_MULTIPLIER,
    TUBE_OD, TUBE_ID, TUBE_LENGTH, NUM_TUBES_X, NUM_TUBES_Y,
    SENSOR_PCB_SIZE, SENSOR_HOLE_DIA, SENSOR_HOLE_OFFSET, SENSOR_CHAMBER_WIDTH, SENSOR_CHAMBER_HEIGHT,
    FAN_SIZE, FAN_MOUNT_HOLE_SPACING, FAN_MOUNT_HOLE_DIA,
    MANIFOLD_BASE_HEIGHT, TRANSITION_LENGTH, WALL_THICKNESS, MANIFOLD_OUTER_MARGIN,
    SNAP_FIT_WIDTH, SNAP_FIT_HEIGHT, SNAP_FIT_DEPTH, SNAP_FIT_TAPER, SNAP_FIT_CLEARANCE,
    ORING_GROOVE_WIDTH, ORING_GROOVE_DEPTH,
    MAX_PRINT_X, MAX_PRINT_Y, MAX_PRINT_Z,
    calculate_intake_area, calculate_sensor_area, verify_speed_multiplier,
    add_male_snap_fit, add_female_snap_fit, add_oring_groove,
    create_snap_tab, create_snap_slot,
    create_intake_tube, create_sensor_mount, create_fan_mount,
    create_transition_section, create_sensor_chamber, create_fan_adapter
)

# Split parameters - 3x3 to align with 3x3 tube grid (each section gets 1 tube)
BASE_SECTIONS_X = 3  # Number of sections in X direction
BASE_SECTIONS_Y = 3  # Number of sections in Y direction
BOLT_HOLE_DIA = 5  # mm (M4 bolt)
ALIGNMENT_PIN_DIA = 6  # mm
ALIGNMENT_PIN_HEIGHT = 10  # mm
JOINT_OVERLAP = 10  # mm overlap at section joints

def create_split_base_section(section_x, section_y):
    """
    Create one section of the split base
    section_x, section_y: indices from 0 to BASE_SECTIONS_X/Y-1

    Design creates rotationally symmetric pieces:
    - All 4 corner pieces are IDENTICAL (rotate 90° as needed)
    - All 4 edge pieces are IDENTICAL (rotate 90° as needed)
    - Center piece is unique

    Corner pieces have: male pins on 2 adjacent edges
    Edge pieces have: female on 1 edge, male on 2 adjacent edges
    Center piece has: female on all 4 edges
    """
    # Calculate overall base dimensions
    base_width = MANIFOLD_BASE_SIZE - 2 * MANIFOLD_OUTER_MARGIN
    base_depth = MANIFOLD_BASE_SIZE - 2 * MANIFOLD_OUTER_MARGIN

    # Calculate section dimensions
    section_width = base_width / BASE_SECTIONS_X
    section_depth = base_depth / BASE_SECTIONS_Y

    # Calculate section position offset
    section_offset_x = -base_width/2 + section_x * section_width + section_width/2
    section_offset_y = -base_depth/2 + section_y * section_depth + section_depth/2

    # Calculate which tubes belong to this section FIRST
    # Keep track of tube positions for cutting airflow holes
    tube_positions_local = []
    tube_separation = (base_depth - 2*WALL_THICKNESS - 2*TUBE_OD) / (NUM_TUBES_X - 1)
    first_tube_offet = WALL_THICKNESS + TUBE_OD
    for i in range(NUM_TUBES_X):
        for j in range(NUM_TUBES_Y):
            # Calculate tube position in global coordinates

            tube_x = -base_depth/2 + first_tube_offet + i*tube_separation
            tube_y = -base_depth/2 + first_tube_offet + j*tube_separation

            # Check if tube belongs in this section (with small margin)
            section_min_x = -base_width/2 + section_x * section_width
            section_max_x = section_min_x + section_width
            section_min_y = -base_depth/2 + section_y * section_depth
            section_max_y = section_min_y + section_depth

            if (section_min_x <= tube_x <= section_max_x and
                section_min_y <= tube_y <= section_max_y):
                # Convert to local coordinates
                local_x = tube_x - section_offset_x
                local_y = tube_y - section_offset_y
                tube_positions_local.append((local_x, local_y))

    # Override tube positions for corner and edge pieces to avoid clustering
    is_corner = (section_x == 0 and section_y == 0)
    is_edge = (section_x == 1 and section_y == 0)

    if is_corner and len(tube_positions_local) > 0:
        # Corner piece: move tube diagonally to opposite corner
        # Original is at bottom-left, move to top-right
        tube_positions_local = [(first_tube_offet-section_width/2, first_tube_offet-section_width/2)]
#        tube_positions_local = [(section_width/4, section_depth/4)]

    if is_edge and len(tube_positions_local) > 0:
        # Edge piece: move tube to opposite side
        # Original is at center-bottom, move to center-top
        tube_positions_local = [(0, first_tube_offet-section_width/2)]
#        tube_positions_local = [(0, section_depth/4)]

    # Create base plate for this section
    section = (
        cq.Workplane("XY")
        .rect(section_width, section_depth)
        .extrude(WALL_THICKNESS)
    )

    # Cut airflow holes in base plate BEFORE adding chamber walls
    for local_x, local_y in tube_positions_local:
        section = (
            section.faces(">Z").workplane()  # Work from top of base plate
            .pushPoints([(local_x, local_y)])
            .circle(TUBE_ID/2)  # Match inner diameter of tube
            .cutThruAll()  # Cut through base plate
        )

    # Create collection chamber walls
    section = (
        section.faces(">Z").workplane()
        .rect(section_width, section_depth)
        .rect(section_width - 2*WALL_THICKNESS, section_depth - 2*WALL_THICKNESS)
        .extrude(MANIFOLD_BASE_HEIGHT)
    )

    # Add tube bosses
    for local_x, local_y in tube_positions_local:
        print(f"Tube Boss: {local_x} {local_y}")
        # Add tube boss
        boss = (
            cq.Workplane("XY")
            .workplane(offset=0)
            .moveTo(local_x, local_y)
            .circle(TUBE_OD/2 + 3)
            .extrude(MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)
        )
        # Cut hole for tube
        boss = (
            boss.faces(">Z").workplane()
            .moveTo(local_x, local_y)
            .circle(TUBE_OD/2 + 0.2)
            .cutThruAll()
        )
        section = section.union(boss)

    # Determine piece type
    is_center = (section_x == 1 and section_y == 1)
    is_corner = (section_x == 0 and section_y == 0)
    is_edge = (section_x == 1 and section_y == 0)

    # CENTER PIECE SPECIAL: All 4 sides get bolt holes AND male pins
    if is_center:
        # Bolt hole height (middle of the wall)
        hole_z = WALL_THICKNESS + MANIFOLD_BASE_HEIGHT/2

        # Right edge (+X) - 3 holes along Y axis, pin points outward
        for i in range(3):
            y_pos = -section_depth/2 + (i + 1) * (section_depth / 4)
            hole = (
                cq.Workplane("YZ")
                .workplane(offset=section_width/2)  # Start at outer surface
                .moveTo(y_pos, hole_z)
                .circle(BOLT_HOLE_DIA/2)
                .extrude(-WALL_THICKNESS - 2)  # Extrude inward through wall
            )
            section = section.cut(hole)
        pin = (
            cq.Workplane("YZ")
            .workplane(offset=section_width/2)
            .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
            .circle(ALIGNMENT_PIN_DIA/2)
            .extrude(ALIGNMENT_PIN_HEIGHT)  # Extrude outward in +X
        )
        section = section.union(pin)

        # Left edge (-X) - 3 holes along Y axis, pin points outward
        for i in range(3):
            y_pos = -section_depth/2 + (i + 1) * (section_depth / 4)
            hole = (
                cq.Workplane("YZ")
                .workplane(offset=-section_width/2)  # Start at outer surface
                .moveTo(y_pos, hole_z)
                .circle(BOLT_HOLE_DIA/2)
                .extrude(WALL_THICKNESS + 2)  # Extrude inward through wall
            )
            section = section.cut(hole)
        pin = (
            cq.Workplane("YZ")
            .workplane(offset=-section_width/2)
            .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
            .circle(ALIGNMENT_PIN_DIA/2)
            .extrude(-ALIGNMENT_PIN_HEIGHT)  # Extrude outward in -X
        )
        section = section.union(pin)

        # Top edge (+Y) - 3 holes along X axis, pin points outward
        for i in range(3):
            x_pos = -section_width/2 + (i + 1) * (section_width / 4)
            hole = (
                cq.Workplane("XZ")
                .workplane(offset=section_depth/2)  # Start at outer surface
                .moveTo(x_pos, hole_z)
                .circle(BOLT_HOLE_DIA/2)
                .extrude(-WALL_THICKNESS - 2)  # Extrude inward through wall
            )
            section = section.cut(hole)
        pin = (
            cq.Workplane("XZ")
            .workplane(offset=section_depth/2)
            .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
            .circle(ALIGNMENT_PIN_DIA/2)
            .extrude(ALIGNMENT_PIN_HEIGHT)  # Extrude outward in +Y
        )
        section = section.union(pin)

        # Bottom edge (-Y) - 3 holes along X axis, pin points outward
        for i in range(3):
            x_pos = -section_width/2 + (i + 1) * (section_width / 4)
            hole = (
                cq.Workplane("XZ")
                .workplane(offset=-section_depth/2)  # Start at outer surface
                .moveTo(x_pos, hole_z)
                .circle(BOLT_HOLE_DIA/2)
                .extrude(WALL_THICKNESS + 2)  # Extrude inward through wall
            )
            section = section.cut(hole)
        pin = (
            cq.Workplane("XZ")
            .workplane(offset=-section_depth/2)
            .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
            .circle(ALIGNMENT_PIN_DIA/2)
            .extrude(-ALIGNMENT_PIN_HEIGHT)  # Extrude outward in -Y
        )
        section = section.union(pin)

        # Add orientation marker on the +X (right) edge - small triangular notch
        marker = (
            cq.Workplane("YZ")
            .workplane(offset=section_width/2 - 1)  # Just inside the right edge
            .moveTo(0, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)
            .lineTo(-5, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)
            .lineTo(-5, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS - 3)
            .close()
            .extrude(2)
        )
        section = section.cut(marker)

    else:
        # NON-CENTER PIECES: Add features based on piece type
        hole_z = WALL_THICKNESS + MANIFOLD_BASE_HEIGHT/2

        if is_corner:
            # CORNER PIECE (0,0): Bolt holes + male pins on RIGHT (+X) and BOTTOM (-Y), snap-fit on LEFT (-X) and BOTTOM (-Y)
            # Indexing mark is on RIGHT (+X), clockwise from mark is BOTTOM (-Y), counter-clockwise is TOP (+Y)

            # Right edge (+X) - 3 bolt holes + 1 male pin
            for i in range(3):
                y_pos = -section_depth/2 + (i + 1) * (section_depth / 4)
                hole = (
                    cq.Workplane("YZ")
                    .workplane(offset=section_width/2)
                    .moveTo(y_pos, hole_z)
                    .circle(BOLT_HOLE_DIA/2)
                    .extrude(-WALL_THICKNESS - 2)
                )
                section = section.cut(hole)
            pin = (
                cq.Workplane("YZ")
                .workplane(offset=section_width/2)
                .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
                .circle(ALIGNMENT_PIN_DIA/2)
                .extrude(ALIGNMENT_PIN_HEIGHT)
            )
            section = section.union(pin)

            # Bottom edge (-Y) - 3 bolt holes + 1 male pin
            for i in range(3):
                x_pos = -section_width/2 + (i + 1) * (section_width / 4)
                hole = (
                    cq.Workplane("XZ")
                    .workplane(offset=-section_depth/2)
                    .moveTo(x_pos, hole_z)
                    .circle(BOLT_HOLE_DIA/2)
                    .extrude(WALL_THICKNESS + 2)
                )
                section = section.cut(hole)
            pin = (
                cq.Workplane("XZ")
                .workplane(offset=-section_depth/2)
                .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
                .circle(ALIGNMENT_PIN_DIA/2)
                .extrude(-ALIGNMENT_PIN_HEIGHT)
            )
            section = section.union(pin)

            # Add orientation marker on the +X (right) edge - small triangular notch
            marker = (
                cq.Workplane("YZ")
                .workplane(offset=section_width/2 - 1)
                .moveTo(0, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)
                .lineTo(-5, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)
                .lineTo(-5, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS - 3)
                .close()
                .extrude(2)
            )
            section = section.cut(marker)

        elif is_edge:
            # EDGE PIECE (1,0): Bolt holes on LEFT (-X), RIGHT (+X), and BOTTOM (-Y)
            # Female alignment holes on LEFT (-X), RIGHT (+X), and BOTTOM (-Y) only
            # Indexing mark is on RIGHT (+X), clockwise from mark is BOTTOM (-Y), counter-clockwise is TOP (+Y)

            # Right edge (+X) - 3 bolt holes + 1 female alignment hole
            for i in range(3):
                y_pos = -section_depth/2 + (i + 1) * (section_depth / 4)
                hole = (
                    cq.Workplane("YZ")
                    .workplane(offset=section_width/2)
                    .moveTo(y_pos, hole_z)
                    .circle(BOLT_HOLE_DIA/2)
                    .extrude(-WALL_THICKNESS - 2)
                )
                section = section.cut(hole)
            # Female alignment hole (cut into the wall)
            alignment_hole = (
                cq.Workplane("YZ")
                .workplane(offset=section_width/2)
                .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
                .circle(ALIGNMENT_PIN_DIA/2 + 0.2)
                .extrude(-ALIGNMENT_PIN_HEIGHT - 2)
            )
            section = section.cut(alignment_hole)

            # Left edge (-X) - 3 bolt holes + 1 female alignment hole
            for i in range(3):
                y_pos = -section_depth/2 + (i + 1) * (section_depth / 4)
                hole = (
                    cq.Workplane("YZ")
                    .workplane(offset=-section_width/2)
                    .moveTo(y_pos, hole_z)
                    .circle(BOLT_HOLE_DIA/2)
                    .extrude(WALL_THICKNESS + 2)
                )
                section = section.cut(hole)
            # Female alignment hole (cut into the wall)
            alignment_hole = (
                cq.Workplane("YZ")
                .workplane(offset=-section_width/2)
                .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
                .circle(ALIGNMENT_PIN_DIA/2 + 0.2)
                .extrude(ALIGNMENT_PIN_HEIGHT + 2)
            )
            section = section.cut(alignment_hole)

            # Bottom edge (-Y) - 3 bolt holes + 1 female alignment hole (clockwise from mark)
            for i in range(3):
                x_pos = -section_width/2 + (i + 1) * (section_width / 4)
                hole = (
                    cq.Workplane("XZ")
                    .workplane(offset=-section_depth/2)
                    .moveTo(x_pos, hole_z)
                    .circle(BOLT_HOLE_DIA/2)
                    .extrude(WALL_THICKNESS + 2)
                )
                section = section.cut(hole)
            # Female alignment hole (cut into the wall)
            alignment_hole = (
                cq.Workplane("XZ")
                .workplane(offset=-section_depth/2)
                .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
                .circle(ALIGNMENT_PIN_DIA/2 + 0.2)
                .extrude(ALIGNMENT_PIN_HEIGHT + 2)
            )
            section = section.cut(alignment_hole)

            # Top edge (+Y) - NO bolt holes, NO alignment hole (counter-clockwise from mark)

            # Add orientation marker on the +X (right) edge - small triangular notch
            marker = (
                cq.Workplane("YZ")
                .workplane(offset=section_width/2 - 1)
                .moveTo(0, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)
                .lineTo(-5, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)
                .lineTo(-5, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS - 3)
                .close()
                .extrude(2)
            )
            section = section.cut(marker)

    # Add snap-fit features based on piece type
    if is_corner:
        # Add snap-fit only on LEFT (-X) and BOTTOM (-Y) edges
        snap_height = MANIFOLD_BASE_HEIGHT + WALL_THICKNESS
        tab_spacing = 60
        num_tabs = max(2, int(section_width / tab_spacing))

        # Left edge (-X) snap-fit tabs
        for i in range(num_tabs):
            y_pos = -section_depth/2 + (i + 0.5) * (section_depth / num_tabs)
            tab = create_snap_tab(snap_height, "Y")
            tab = tab.rotate((0, 0, 0), (0, 0, 1), -90)
            tab = tab.translate((-section_width/2, y_pos, 0))
            section = section.union(tab)

        # Bottom edge (-Y) snap-fit tabs
        for i in range(num_tabs):
            x_pos = -section_width/2 + (i + 0.5) * (section_width / num_tabs)
            tab = create_snap_tab(snap_height, "X")
            tab = tab.rotate((0, 0, 0), (0, 0, 1), 180)
            tab = tab.translate((x_pos, -section_depth/2, 0))
            section = section.union(tab)

    elif is_edge:
        # Add snap-fit only on BOTTOM (-Y) edge (clockwise from mark)
        snap_height = MANIFOLD_BASE_HEIGHT + WALL_THICKNESS
        tab_spacing = 60
        num_tabs = max(2, int(section_width / tab_spacing))

        # Bottom edge (-Y) snap-fit tabs
        for i in range(num_tabs):
            x_pos = -section_width/2 + (i + 0.5) * (section_width / num_tabs)
            tab = create_snap_tab(snap_height, "X")
            tab = tab.rotate((0, 0, 0), (0, 0, 1), 180)
            tab = tab.translate((x_pos, -section_depth/2, 0))
            section = section.union(tab)

    return section

def generate_split_base():
    """Generate only the 3 unique base sections (corner, edge, center)"""
    print("="*60)
    print("SPLIT BASE GENERATOR")
    print("="*60)
    print()

    base_width = MANIFOLD_BASE_SIZE - 2 * MANIFOLD_OUTER_MARGIN
    base_depth = MANIFOLD_BASE_SIZE - 2 * MANIFOLD_OUTER_MARGIN
    section_width = base_width / BASE_SECTIONS_X
    section_depth = base_depth / BASE_SECTIONS_Y

    print(f"Full base: {base_width:.1f} x {base_depth:.1f} mm")
    print(f"Section size: {section_width:.1f} x {section_depth:.1f} mm")
    print(f"Number of unique pieces: 3 (corner, edge, center)")
    print(f"Print bed: {MAX_PRINT_X} x {MAX_PRINT_Y} mm")

    if section_width <= MAX_PRINT_X and section_depth <= MAX_PRINT_Y:
        print("✓ Each section fits on print bed!")
    else:
        print("✗ ERROR: Sections still too large for print bed!")
        return

    print()
    print("Generating 3 unique base sections...")
    print()

    parts_generated = []

    # Generate corner piece (0,0)
    try:
        print(f"  [CORNER] Generating base_section_corner...")
        section = create_split_base_section(0, 0)
        filename = "base_section_corner.stl"
        cq.exporters.export(section, filename)
        print(f"        Exported: {filename}")
        print(f"        Print 4x and rotate as needed for corners")
        parts_generated.append("base_section_corner")
    except Exception as e:
        print(f"        ERROR: {e}")
        import traceback
        traceback.print_exc()

    # Generate edge piece (1,0)
    try:
        print(f"  [EDGE] Generating base_section_edge...")
        section = create_split_base_section(1, 0)
        filename = "base_section_edge.stl"
        cq.exporters.export(section, filename)
        print(f"        Exported: {filename}")
        print(f"        Print 4x and rotate as needed for edges")
        parts_generated.append("base_section_edge")
    except Exception as e:
        print(f"        ERROR: {e}")
        import traceback
        traceback.print_exc()

    # Generate center piece (1,1)
    try:
        print(f"  [CENTER] Generating base_section_center...")
        section = create_split_base_section(1, 1)
        filename = "base_section_center.stl"
        cq.exporters.export(section, filename)
        print(f"        Exported: {filename}")
        print(f"        Print 1x")
        parts_generated.append("base_section_center")
    except Exception as e:
        print(f"        ERROR: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("="*60)
    print("SPLIT BASE GENERATION COMPLETE")
    print("="*60)
    print()
    print(f"Parts generated: {len(parts_generated)}/{BASE_SECTIONS_X * BASE_SECTIONS_Y}")
    print()
    print("Assembly instructions:")
    print("1. Print all 9 base sections (each section has 1 tube)")
    print("2. Join sections using M5 bolts (you'll need ~24 bolts)")
    print("3. Use silicone gasket maker on all joints for air-tight seal")
    print("4. Install 9x intake tubes from below (1 per section)")
    print("5. Attach transition section on top")
    print()
    print("Section layout (top view):")
    print("  +-------+-------+-------+")
    print("  | 0,2   | 1,2   | 2,2   |  (back)")
    print("  +-------+-------+-------+")
    print("  | 0,1   | 1,1   | 2,1   |  (middle)")
    print("  +-------+-------+-------+")
    print("  | 0,0   | 1,0   | 2,0   |  (front)")
    print("  +-------+-------+-------+")
    print()
    print("NOTE: 3x3 split ensures no tube is cut by section boundaries!")
    print()

if __name__ == "__main__":
    print("This module generates the split base sections.")
    print()

    # Verify speed multiplier
    verify_speed_multiplier()
    print()

    # Generate split base
    generate_split_base()
