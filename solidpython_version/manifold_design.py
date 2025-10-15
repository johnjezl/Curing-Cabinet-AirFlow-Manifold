"""
Air Flow Manifold for Curing Cabinet - SolidPython Version
Designed to concentrate airflow from 550x550mm cabinet to sensor, providing 5x speed magnification

Design principles:
- Multiple intake tubes distributed across cabinet top
- Gradual convergence to sensor chamber for laminar flow
- 120mm fan mount for active airflow control
- Modular design split into printable sections
- All parts fit on 220x220mm print bed

Material: PETG recommended (food-safe, chemical resistant, easy to print)
"""

from solid2 import *
import math

# ==================== DESIGN PARAMETERS ====================

# Cabinet and airflow parameters
CABINET_WIDTH = 550  # mm
CABINET_DEPTH = 550  # mm
TARGET_SPEED_MULTIPLIER = 5  # 5x magnification

# Intake tubes (pierce freezer top)
TUBE_OD = 38  # mm outer diameter
TUBE_ID = 35  # mm inner diameter
TUBE_LENGTH = 60  # mm (accommodate 1.5-2.5 inch / 38-64mm freezer top)
NUM_TUBES_X = 3  # tubes in X direction
NUM_TUBES_Y = 3  # tubes in Y direction

# Sensor parameters
SENSOR_PCB_SIZE = 25.4  # mm (1 inch)
SENSOR_HOLE_DIA = 4  # mm
SENSOR_HOLE_OFFSET = 1  # mm from edge
SENSOR_CHAMBER_WIDTH = 42  # mm (adjusted for 5x concentration)
SENSOR_CHAMBER_HEIGHT = 80  # mm

# Fan parameters
FAN_SIZE = 120  # mm (standard 120mm fan)
FAN_MOUNT_HOLE_SPACING = 105  # mm (standard 120mm fan mounting)
FAN_MOUNT_HOLE_DIA = 4.5  # mm

# Manifold geometry
MANIFOLD_BASE_HEIGHT = 40  # mm
TRANSITION_LENGTH = 150  # mm (gradual taper for laminar flow)
WALL_THICKNESS = 3  # mm
MANIFOLD_OUTER_MARGIN = 20  # mm margin around tubes
BOTTOM_PLATE_MARGIN = 15  # mm solid margin for sealing

# Print bed constraints
MAX_PRINT_X = 220  # mm
MAX_PRINT_Y = 220  # mm
MAX_PRINT_Z = 210  # mm

# Joint parameters for assembly
JOINT_OVERLAP = 4  # mm overlap on interior edges
OUTER_TRIM = 38  # mm trim from outer edges to fit print bed
BOLT_DIA = 5  # mm (M5 bolts)
BOLT_SPACING = 40  # mm between bolt holes

# ==================== HELPER FUNCTIONS ====================

def calculate_intake_area():
    """Calculate total intake area from all tubes"""
    return NUM_TUBES_X * NUM_TUBES_Y * math.pi * (TUBE_ID/2)**2

def calculate_sensor_area():
    """Calculate sensor chamber cross-sectional area"""
    return SENSOR_CHAMBER_WIDTH ** 2

def verify_speed_multiplier():
    """Verify that the area ratio provides desired speed magnification"""
    intake_area = calculate_intake_area()
    sensor_area = calculate_sensor_area()
    actual_multiplier = intake_area / sensor_area
    print(f"Intake area: {intake_area:.1f} mm²")
    print(f"Sensor area: {sensor_area:.1f} mm²")
    print(f"Actual speed multiplier: {actual_multiplier:.2f}x")
    print(f"Target multiplier: {TARGET_SPEED_MULTIPLIER}x")
    return actual_multiplier

# ==================== COMPONENT BUILDERS ====================

def create_intake_tube():
    """Create a single intake tube - hollow cylinder open at both ends"""
    outer = cylinder(r=TUBE_OD/2, h=TUBE_LENGTH)
    inner = cylinder(r=TUBE_ID/2, h=TUBE_LENGTH + 0.1)
    inner = translate([0, 0, -0.05])(inner)

    # O-ring groove at top
    groove = cylinder(r=TUBE_OD/2 + 1, h=2)
    groove = translate([0, 0, TUBE_LENGTH - 2])(groove)

    tube = outer - inner + groove - translate([0, 0, TUBE_LENGTH - 2])(
        cylinder(r=TUBE_OD/2 - 0.5, h=2.1)
    )

    return tube

def create_transition_quadrant(quadrant=1):
    """
    Create one quadrant of the transition section
    quadrant: 1-4 (1=front-left, 2=front-right, 3=back-left, 4=back-right)

    Quadrant layout (top view):
    +-------+-------+
    |   3   |   4   |  (back)
    +-------+-------+
    |   1   |   2   |  (front)
    +-------+-------+
    """
    base_width = CABINET_WIDTH - 2 * MANIFOLD_OUTER_MARGIN
    base_depth = CABINET_DEPTH - 2 * MANIFOLD_OUTER_MARGIN
    sensor_width = SENSOR_CHAMBER_WIDTH + 2 * WALL_THICKNESS

    # Determine quadrant position
    is_right = quadrant in [2, 4]
    is_back = quadrant in [3, 4]

    # Calculate quadrant dimensions at base
    plate_half_width = base_width / 2
    plate_half_depth = base_depth / 2

    # Quadrant extents with trimming and overlap
    x_min = 0 if is_right else -plate_half_width
    x_max = plate_half_width if is_right else 0
    y_min = 0 if is_back else -plate_half_depth
    y_max = plate_half_depth if is_back else 0

    # Trim outer edges
    if not is_right:
        x_min += OUTER_TRIM
    else:
        x_max -= OUTER_TRIM
    if not is_back:
        y_min += OUTER_TRIM
    else:
        y_max -= OUTER_TRIM

    # Add overlap on interior edges
    if is_right:
        x_min -= JOINT_OVERLAP / 2
    else:
        x_max += JOINT_OVERLAP / 2
    if is_back:
        y_min -= JOINT_OVERLAP / 2
    else:
        y_max += JOINT_OVERLAP / 2

    quadrant_width = x_max - x_min
    quadrant_depth = y_max - y_min
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2

    # Bottom plate with open center
    bottom_plate = translate([x_center, y_center, 0])(
        cube([quadrant_width, quadrant_depth, WALL_THICKNESS], center=True)
    )

    # Cut center opening (leave margin for sealing)
    inner_x_min = max(x_min, -base_width/2 + BOTTOM_PLATE_MARGIN)
    inner_x_max = min(x_max, base_width/2 - BOTTOM_PLATE_MARGIN)
    inner_y_min = max(y_min, -base_depth/2 + BOTTOM_PLATE_MARGIN)
    inner_y_max = min(y_max, base_depth/2 - BOTTOM_PLATE_MARGIN)

    if inner_x_max > inner_x_min and inner_y_max > inner_y_min:
        inner_width = inner_x_max - inner_x_min
        inner_depth = inner_y_max - inner_y_min
        inner_x_center = (inner_x_min + inner_x_max) / 2
        inner_y_center = (inner_y_min + inner_y_max) / 2

        cutout = translate([inner_x_center, inner_y_center, WALL_THICKNESS/2])(
            cube([inner_width, inner_depth, WALL_THICKNESS + 0.1], center=True)
        )
        bottom_plate = bottom_plate - cutout

    # Calculate top dimensions (converges to sensor opening)
    top_half = sensor_width / 2
    top_x_min = -top_half if not is_right else -JOINT_OVERLAP / 2
    top_x_max = top_half if is_right else JOINT_OVERLAP / 2
    top_y_min = -top_half if not is_back else -JOINT_OVERLAP / 2
    top_y_max = top_half if is_back else JOINT_OVERLAP / 2

    top_width = top_x_max - top_x_min
    top_depth = top_y_max - top_y_min
    top_x_center = (top_x_min + top_x_max) / 2
    top_y_center = (top_y_min + top_y_max) / 2

    total_height = TRANSITION_LENGTH + WALL_THICKNESS

    # Create tapered hull (outer shell)
    bottom_corners = [
        [x_min, y_min, 0],
        [x_max, y_min, 0],
        [x_max, y_max, 0],
        [x_min, y_max, 0],
    ]

    top_corners = [
        [top_x_min, top_y_min, total_height],
        [top_x_max, top_y_min, total_height],
        [top_x_max, top_y_max, total_height],
        [top_x_min, top_y_max, total_height],
    ]

    # Build outer shell using hull between bottom and top
    outer_shell = hull()(
        translate([x_center, y_center, 0])(
            cube([quadrant_width, quadrant_depth, 0.1], center=True)
        ),
        translate([top_x_center, top_y_center, total_height])(
            cube([top_width, top_depth, 0.1], center=True)
        )
    )

    # Create inner cavity
    inner_bottom_width = quadrant_width - 2 * WALL_THICKNESS
    inner_bottom_depth = quadrant_depth - 2 * WALL_THICKNESS
    inner_top_width = top_width - 2 * WALL_THICKNESS
    inner_top_depth = top_depth - 2 * WALL_THICKNESS

    inner_cavity = hull()(
        translate([x_center, y_center, WALL_THICKNESS])(
            cube([inner_bottom_width, inner_bottom_depth, 0.1], center=True)
        ),
        translate([top_x_center, top_y_center, total_height - WALL_THICKNESS])(
            cube([inner_top_width, inner_top_depth, 0.1], center=True)
        )
    )

    # Combine parts
    quadrant_piece = bottom_plate + outer_shell - inner_cavity

    # Add bolt holes on interior edges
    bolt_holes = union()
    num_bolts = max(2, int(total_height / BOLT_SPACING))

    for i in range(num_bolts):
        z_pos = WALL_THICKNESS + (i + 1) * (total_height - WALL_THICKNESS) / (num_bolts + 1)

        # X-direction interior edge (at x=0)
        if not (is_right and not is_back):
            hole = translate([0, y_center, z_pos])(
                rotate([0, 90, 0])(
                    cylinder(r=BOLT_DIA/2, h=30, center=True)
                )
            )
            bolt_holes = bolt_holes + hole

        # Y-direction interior edge (at y=0)
        if not (is_back and not is_right):
            hole = translate([x_center, 0, z_pos])(
                rotate([90, 0, 0])(
                    cylinder(r=BOLT_DIA/2, h=30, center=True)
                )
            )
            bolt_holes = bolt_holes + hole

    quadrant_piece = quadrant_piece - bolt_holes

    return quadrant_piece

def create_sensor_chamber():
    """Create sensor chamber with PCB mount"""
    chamber_size = SENSOR_CHAMBER_WIDTH + 2 * WALL_THICKNESS

    # Chamber body
    outer = cube([chamber_size, chamber_size, SENSOR_CHAMBER_HEIGHT], center=True)
    inner = cube([SENSOR_CHAMBER_WIDTH, SENSOR_CHAMBER_WIDTH,
                  SENSOR_CHAMBER_HEIGHT - WALL_THICKNESS], center=True)
    inner = translate([0, 0, -WALL_THICKNESS/2])(inner)

    chamber = outer - inner

    # Sensor mounting struts
    strut_h = translate([0, 0, 0])(
        cube([SENSOR_PCB_SIZE + 10, 3, 3], center=True)
    )
    strut_v = translate([0, 0, 0])(
        cube([3, SENSOR_PCB_SIZE + 10, 3], center=True)
    )

    chamber = chamber + strut_h + strut_v

    # Mounting screw holes
    hole_distance = SENSOR_PCB_SIZE - 2 * SENSOR_HOLE_OFFSET
    holes = union()
    for x in [-hole_distance/2, hole_distance/2]:
        for y in [-hole_distance/2, hole_distance/2]:
            hole = translate([x, y, -5])(
                cylinder(r=SENSOR_HOLE_DIA/2, h=15)
            )
            holes = holes + hole

    chamber = chamber - holes
    chamber = translate([0, 0, SENSOR_CHAMBER_HEIGHT/2])(chamber)

    return chamber

def create_fan_adapter():
    """Create adapter from sensor chamber to 120mm fan"""
    chamber_size = SENSOR_CHAMBER_WIDTH + 2 * WALL_THICKNESS
    adapter_height = 40

    # Bottom and top profiles
    bottom = cube([chamber_size, chamber_size, 0.1], center=True)
    top = cube([FAN_SIZE + 10, FAN_SIZE + 10, 0.1], center=True)
    top = translate([0, 0, adapter_height])(top)

    # Outer shell
    outer = hull()(bottom, top)

    # Inner cavity
    inner_bottom = cube([SENSOR_CHAMBER_WIDTH, SENSOR_CHAMBER_WIDTH, 0.1], center=True)
    inner_bottom = translate([0, 0, WALL_THICKNESS])(inner_bottom)
    inner_top = cylinder(r=FAN_SIZE/2 - 5, h=0.1)
    inner_top = translate([0, 0, adapter_height - WALL_THICKNESS])(inner_top)

    inner = hull()(inner_bottom, inner_top)

    adapter = outer - inner

    # Fan mount plate
    fan_plate = translate([0, 0, adapter_height])(
        cube([FAN_SIZE + 10, FAN_SIZE + 10, 4], center=True)
    )
    fan_opening = translate([0, 0, adapter_height])(
        cylinder(r=FAN_SIZE/2 - 5, h=5, center=True)
    )
    fan_plate = fan_plate - fan_opening

    # Fan mounting holes
    hole_offset = FAN_MOUNT_HOLE_SPACING / 2
    fan_holes = union()
    for x in [-hole_offset, hole_offset]:
        for y in [-hole_offset, hole_offset]:
            hole = translate([x, y, adapter_height])(
                cylinder(r=FAN_MOUNT_HOLE_DIA/2, h=10, center=True)
            )
            fan_holes = fan_holes + hole

    adapter = adapter + fan_plate - fan_holes

    return adapter

# ==================== MAIN GENERATION ====================

def generate_all_parts():
    """Generate all manifold parts"""
    print("=" * 60)
    print("AIR FLOW MANIFOLD GENERATOR - SolidPython Version")
    print("=" * 60)
    print()

    verify_speed_multiplier()
    print()

    base_width = CABINET_WIDTH - 2 * MANIFOLD_OUTER_MARGIN
    print(f"Base dimensions: {base_width:.1f} x {base_width:.1f} mm")
    print(f"Transition height: {TRANSITION_LENGTH + WALL_THICKNESS} mm")
    print(f"Quadrant size: ~219 x 219 x {TRANSITION_LENGTH + WALL_THICKNESS} mm")
    print(f"Print bed: {MAX_PRINT_X} x {MAX_PRINT_Y} x {MAX_PRINT_Z} mm")
    print()
    print("Generating parts...")
    print()

    parts = {}

    # Generate transition quadrants
    print("  [1/7] Transition quadrants (4 pieces)...")
    quadrant_names = ["front_left", "front_right", "back_left", "back_right"]
    for i in range(1, 5):
        name = f"transition_{quadrant_names[i-1]}"
        print(f"        Generating {name}...")
        parts[name] = create_transition_quadrant(i)

    # Generate other components
    print("  [2/7] Intake tube (print 9x)...")
    parts["intake_tube"] = create_intake_tube()

    print("  [3/7] Sensor chamber...")
    parts["sensor_chamber"] = create_sensor_chamber()

    print("  [4/7] Fan adapter...")
    parts["fan_adapter"] = create_fan_adapter()

    print()
    print("  Generating SCAD files...")
    for name, part in parts.items():
        scad_filename = f"{name}.scad"
        scad_render_to_file(part, scad_filename, file_header=f'$fn = 64;\n')
        print(f"        {scad_filename}")

    print()
    print("=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print()
    print(f"Generated {len(parts)} SCAD files")
    print()
    print("To convert to STL files, you have two options:")
    print()
    print("Option 1: Use OpenSCAD GUI")
    print("  - Open each .scad file in OpenSCAD")
    print("  - Press F6 to render")
    print("  - File > Export > Export as STL")
    print()
    print("Option 2: Use OpenSCAD command line")
    print("  - Install OpenSCAD from https://openscad.org/")
    print("  - Run these commands:")
    for name in parts.keys():
        print(f"    openscad -o {name}.stl {name}.scad")
    print()
    print("=" * 60)
    print("ASSEMBLY INSTRUCTIONS")
    print("=" * 60)
    print()
    print("  1. Print 9x intake_tube.stl (hollow tubes, open at both ends)")
    print("  2. Print all 4 transition quadrants:")
    print("     - transition_front_left.stl")
    print("     - transition_front_right.stl")
    print("     - transition_back_left.stl")
    print("     - transition_back_right.stl")
    print("  3. Bolt the 4 quadrants together using M5 bolts")
    print("     (bolt holes are pre-drilled)")
    print("  4. Print sensor_chamber.stl")
    print("  5. Print fan_adapter.stl")
    print("  6. Stack and seal all sections with silicone gasket maker")
    print()
    print("Material: PETG recommended (food-safe, chemical resistant)")
    print()

if __name__ == "__main__":
    generate_all_parts()
