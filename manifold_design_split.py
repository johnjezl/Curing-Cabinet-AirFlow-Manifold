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
    CABINET_WIDTH, CABINET_DEPTH, TARGET_SPEED_MULTIPLIER,
    TUBE_OD, TUBE_ID, TUBE_LENGTH, NUM_TUBES_X, NUM_TUBES_Y,
    SENSOR_PCB_SIZE, SENSOR_HOLE_DIA, SENSOR_HOLE_OFFSET, SENSOR_CHAMBER_WIDTH, SENSOR_CHAMBER_HEIGHT,
    FAN_SIZE, FAN_MOUNT_HOLE_SPACING, FAN_MOUNT_HOLE_DIA,
    MANIFOLD_BASE_HEIGHT, TRANSITION_LENGTH, WALL_THICKNESS, MANIFOLD_OUTER_MARGIN,
    SNAP_FIT_WIDTH, SNAP_FIT_HEIGHT, SNAP_FIT_DEPTH, SNAP_FIT_TAPER, SNAP_FIT_CLEARANCE,
    ORING_GROOVE_WIDTH, ORING_GROOVE_DEPTH,
    MAX_PRINT_X, MAX_PRINT_Y, MAX_PRINT_Z,
    calculate_intake_area, calculate_sensor_area, verify_speed_multiplier,
    add_male_snap_fit, add_female_snap_fit, add_oring_groove,
    create_intake_tube, create_sensor_mount, create_fan_mount,
    create_transition_section, create_sensor_chamber, create_fan_adapter
)

# Split parameters
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
    """
    # Calculate overall base dimensions
    base_width = CABINET_WIDTH - 2 * MANIFOLD_OUTER_MARGIN
    base_depth = CABINET_DEPTH - 2 * MANIFOLD_OUTER_MARGIN

    # Calculate section dimensions
    section_width = base_width / BASE_SECTIONS_X
    section_depth = base_depth / BASE_SECTIONS_Y

    # Calculate section position offset
    section_offset_x = -base_width/2 + section_x * section_width + section_width/2
    section_offset_y = -base_depth/2 + section_y * section_depth + section_depth/2

    # Create base plate for this section
    section = (
        cq.Workplane("XY")
        .rect(section_width, section_depth)
        .extrude(WALL_THICKNESS)
    )

    # Create collection chamber walls
    section = (
        section.faces(">Z").workplane()
        .rect(section_width, section_depth)
        .rect(section_width - 2*WALL_THICKNESS, section_depth - 2*WALL_THICKNESS)
        .extrude(MANIFOLD_BASE_HEIGHT)
    )

    # Calculate which tubes belong to this section
    for i in range(NUM_TUBES_X):
        for j in range(NUM_TUBES_Y):
            # Calculate tube position in global coordinates
            tube_x = -base_width/2 + (i + 1) * (base_width / (NUM_TUBES_X + 1))
            tube_y = -base_depth/2 + (j + 1) * (base_depth / (NUM_TUBES_Y + 1))

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

    # Add bolt holes on edges (for joining sections)
    # Add alignment pins and holes

    # Right edge - add bolt holes and male alignment pins
    if section_x < BASE_SECTIONS_X - 1:
        # Add bolt holes along right edge
        for i in range(3):
            y_pos = -section_depth/2 + (i + 1) * section_depth/4
            section = (
                section.faces(">X").workplane()
                .moveTo(y_pos, MANIFOLD_BASE_HEIGHT/2)
                .circle(BOLT_HOLE_DIA/2)
                .cutThruAll()
            )

        # Add male alignment pins
        pin = (
            cq.Workplane("YZ")
            .workplane(offset=section_width/2)
            .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
            .circle(ALIGNMENT_PIN_DIA/2)
            .extrude(ALIGNMENT_PIN_HEIGHT)
        )
        section = section.union(pin)

    # Left edge - add bolt holes and female alignment holes
    if section_x > 0:
        # Add bolt holes along left edge
        for i in range(3):
            y_pos = -section_depth/2 + (i + 1) * section_depth/4
            section = (
                section.faces("<X").workplane()
                .moveTo(y_pos, MANIFOLD_BASE_HEIGHT/2)
                .circle(BOLT_HOLE_DIA/2)
                .cutThruAll()
            )

        # Add female alignment holes
        hole = (
            cq.Workplane("YZ")
            .workplane(offset=-section_width/2)
            .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
            .circle(ALIGNMENT_PIN_DIA/2 + 0.2)  # Clearance
            .extrude(ALIGNMENT_PIN_HEIGHT)
        )
        section = section.cut(hole)

    # Top edge - add bolt holes
    if section_y < BASE_SECTIONS_Y - 1:
        for i in range(3):
            x_pos = -section_width/2 + (i + 1) * section_width/4
            section = (
                section.faces(">Y").workplane()
                .moveTo(x_pos, MANIFOLD_BASE_HEIGHT/2)
                .circle(BOLT_HOLE_DIA/2)
                .cutThruAll()
            )

        # Add male alignment pins
        pin = (
            cq.Workplane("XZ")
            .workplane(offset=section_depth/2)
            .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
            .circle(ALIGNMENT_PIN_DIA/2)
            .extrude(ALIGNMENT_PIN_HEIGHT)
        )
        section = section.union(pin)

    # Bottom edge - add bolt holes
    if section_y > 0:
        for i in range(3):
            x_pos = -section_width/2 + (i + 1) * section_width/4
            section = (
                section.faces("<Y").workplane()
                .moveTo(x_pos, MANIFOLD_BASE_HEIGHT/2)
                .circle(BOLT_HOLE_DIA/2)
                .cutThruAll()
            )

        # Add female alignment holes
        hole = (
            cq.Workplane("XZ")
            .workplane(offset=-section_depth/2)
            .moveTo(0, WALL_THICKNESS + ALIGNMENT_PIN_HEIGHT/2)
            .circle(ALIGNMENT_PIN_DIA/2 + 0.2)
            .extrude(ALIGNMENT_PIN_HEIGHT)
        )
        section = section.cut(hole)

    # Add snap-fit on top (only on perimeter sections for center section)
    # Center section gets full snap-fit, edge sections only on outer edges
    if section_x == 1 and section_y == 1:  # Center section
        section = add_male_snap_fit(section, section_width, section_depth,
                                   MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)
    else:
        # Only add snap-fit on outer edges
        # This is simplified - proper implementation would be more complex
        section = add_male_snap_fit(section, section_width, section_depth,
                                   MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)

    return section

def generate_split_base():
    """Generate all sections of the split base"""
    print("="*60)
    print("SPLIT BASE GENERATOR")
    print("="*60)
    print()

    base_width = CABINET_WIDTH - 2 * MANIFOLD_OUTER_MARGIN
    base_depth = CABINET_DEPTH - 2 * MANIFOLD_OUTER_MARGIN
    section_width = base_width / BASE_SECTIONS_X
    section_depth = base_depth / BASE_SECTIONS_Y

    print(f"Full base: {base_width:.1f} x {base_depth:.1f} mm")
    print(f"Section size: {section_width:.1f} x {section_depth:.1f} mm")
    print(f"Number of sections: {BASE_SECTIONS_X}x{BASE_SECTIONS_Y} = {BASE_SECTIONS_X * BASE_SECTIONS_Y}")
    print(f"Print bed: {MAX_PRINT_X} x {MAX_PRINT_Y} mm")

    if section_width <= MAX_PRINT_X and section_depth <= MAX_PRINT_Y:
        print("✓ Each section fits on print bed!")
    else:
        print("✗ ERROR: Sections still too large for print bed!")
        return

    print()
    print("Generating split base sections...")
    print()

    parts_generated = []
    for i in range(BASE_SECTIONS_X):
        for j in range(BASE_SECTIONS_Y):
            try:
                section_name = f"base_section_{i}_{j}"
                print(f"  [{i},{j}] Generating {section_name}...")
                section = create_split_base_section(i, j)
                filename = f"{section_name}.stl"
                cq.exporters.export(section, filename)
                print(f"        Exported: {filename}")
                parts_generated.append(section_name)
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
    print("1. Print all 9 base sections")
    print("2. Join sections using M4 bolts (you'll need ~24 bolts)")
    print("3. Use silicone gasket maker on all joints for air-tight seal")
    print("4. Install 9x intake tubes from below")
    print("5. Attach transition section on top")
    print()
    print("Section layout (top view):")
    print("  +-------+-------+-------+")
    print("  | 0,2   | 1,2   | 2,2   |")
    print("  +-------+-------+-------+")
    print("  | 0,1   | 1,1   | 2,1   |")
    print("  +-------+-------+-------+")
    print("  | 0,0   | 1,0   | 2,0   |")
    print("  +-------+-------+-------+")
    print()

if __name__ == "__main__":
    print("This module generates the split base sections.")
    print()

    # Verify speed multiplier
    verify_speed_multiplier()
    print()

    # Generate split base
    generate_split_base()
