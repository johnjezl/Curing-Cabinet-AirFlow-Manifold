"""
Air Flow Manifold for Curing Cabinet
Designed to concentrate airflow from 550x550mm cabinet to sensor, providing 5x speed magnification

Design principles:
- Multiple intake tubes distributed across cabinet top
- Gradual convergence to sensor chamber for laminar flow
- 120mm fan mount for active airflow control
- Modular design split into printable sections
- Snap-fit assembly with sealing grooves

Material: PETG recommended (food-safe, chemical resistant, easy to print)
"""

import cadquery as cq
import math
import sys
import io

# Fix Windows encoding issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==================== DESIGN PARAMETERS ====================

# Cabinet and airflow parameters
CABINET_WIDTH = 550  # mm
CABINET_DEPTH = 550  # mm
TARGET_SPEED_MULTIPLIER = 5  # 5x magnification

# Intake tubes (pierce freezer top)
# Calculation: To get 5x speed increase, we need intake_area = 5 * sensor_area
# With 3x3 = 9 tubes at 35mm ID: area = 9 * pi * (17.5)^2 = 8659 mm²
# Sensor chamber: 42mm x 42mm = 1764 mm²
# Ratio: 8659 / 1764 = 4.9x ≈ 5x ✓
TUBE_OD = 38  # mm outer diameter (larger tubes for better flow)
TUBE_ID = 35  # mm inner diameter
TUBE_LENGTH = 60  # mm (accommodate 1.5-2.5 inch / 38-64mm freezer top)
TUBE_THREAD_LENGTH = 15  # mm for nut/gasket mounting
NUM_TUBES_X = 3  # tubes in X direction (fewer tubes, larger diameter)
NUM_TUBES_Y = 3  # tubes in Y direction
TUBE_SPACING_X = CABINET_WIDTH / (NUM_TUBES_X + 1)
TUBE_SPACING_Y = CABINET_DEPTH / (NUM_TUBES_Y + 1)

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
FAN_HUB_DIA = 40  # mm (approximate fan hub)

# Manifold geometry
MANIFOLD_BASE_HEIGHT = 40  # mm
TRANSITION_LENGTH = 150  # mm (gradual taper for laminar flow)
WALL_THICKNESS = 3  # mm
MANIFOLD_OUTER_MARGIN = 20  # mm margin around tubes

# Snap-fit parameters
SNAP_FIT_WIDTH = 6  # mm
SNAP_FIT_HEIGHT = 8  # mm
SNAP_FIT_DEPTH = 2  # mm
SNAP_FIT_TAPER = 0.3  # mm taper for insertion
SNAP_FIT_CLEARANCE = 0.3  # mm clearance for fit
ORING_GROOVE_WIDTH = 3  # mm
ORING_GROOVE_DEPTH = 1.5  # mm

# Print bed constraints
MAX_PRINT_X = 240  # mm (with safety margin)
MAX_PRINT_Y = 210  # mm
MAX_PRINT_Z = 210  # mm

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
    if abs(actual_multiplier - TARGET_SPEED_MULTIPLIER) > 0.5:
        print(f"WARNING: Speed multiplier deviation: {abs(actual_multiplier - TARGET_SPEED_MULTIPLIER):.2f}x")
    return actual_multiplier

# ==================== COMPONENT BUILDERS ====================

def create_intake_tube():
    """Create a single intake tube with threading support"""
    # Create outer cylinder
    tube = (
        cq.Workplane("XY")
        .circle(TUBE_OD/2)
        .extrude(TUBE_LENGTH)
    )

    # Cut inner hole - but NOT all the way through, leave bottom open
    # Create a hollow tube by cutting from top
    tube = (
        tube.faces(">Z").workplane()
        .circle(TUBE_ID/2)
        .cutBlind(-TUBE_LENGTH)  # Cut down but not through bottom
    )

    # Add grooves for o-ring/gasket at top
    tube = (
        tube.faces(">Z").workplane()
        .circle(TUBE_OD/2 + 1)
        .circle(TUBE_OD/2 - 0.5)
        .extrude(-2)
    )

    return tube

def create_sensor_mount():
    """Create sensor PCB mounting bracket with screw holes"""
    mount_base_size = SENSOR_PCB_SIZE + 10
    mount_thickness = 3

    # Calculate hole positions
    hole_distance = SENSOR_PCB_SIZE - 2 * SENSOR_HOLE_OFFSET

    mount = (
        cq.Workplane("XY")
        .rect(mount_base_size, mount_base_size)
        .extrude(mount_thickness)
    )

    # Add screw holes at corners
    positions = [
        (hole_distance/2, hole_distance/2),
        (-hole_distance/2, hole_distance/2),
        (hole_distance/2, -hole_distance/2),
        (-hole_distance/2, -hole_distance/2),
    ]

    for x, y in positions:
        mount = (
            mount.faces(">Z").workplane()
            .pushPoints([(x, y)])
            .circle(SENSOR_HOLE_DIA/2)
            .cutThruAll()
        )

    # Cut center opening for airflow - leave room for sensor element
    mount = (
        mount.faces(">Z").workplane()
        .rect(SENSOR_PCB_SIZE - 8, SENSOR_PCB_SIZE - 8)
        .cutThruAll()
    )

    return mount

def create_fan_mount():
    """Create 120mm fan mounting interface"""
    fan_mount_thickness = 4

    mount = (
        cq.Workplane("XY")
        .rect(FAN_SIZE + 10, FAN_SIZE + 10)
        .extrude(fan_mount_thickness)
    )

    # Cut center hole for airflow
    mount = (
        mount.faces(">Z").workplane()
        .circle(FAN_SIZE/2 - 5)
        .cutThruAll()
    )

    # Add mounting holes at standard 120mm fan positions
    hole_offset = FAN_MOUNT_HOLE_SPACING / 2
    positions = [
        (hole_offset, hole_offset),
        (-hole_offset, hole_offset),
        (hole_offset, -hole_offset),
        (-hole_offset, -hole_offset),
    ]

    for x, y in positions:
        mount = (
            mount.faces(">Z").workplane()
            .pushPoints([(x, y)])
            .circle(FAN_MOUNT_HOLE_DIA/2)
            .cutThruAll()
        )

    return mount

# ==================== SNAP-FIT HELPERS ====================

def add_male_snap_fit(part, width, depth, at_height):
    """Add male snap-fit connectors around perimeter"""
    # Create snap-fit tabs on all four sides
    tab_spacing = 60  # mm between tabs

    # Calculate number of tabs per side
    num_tabs_x = max(2, int(width / tab_spacing))
    num_tabs_y = max(2, int(depth / tab_spacing))

    for i in range(num_tabs_x):
        x_pos = -width/2 + (i + 0.5) * (width / num_tabs_x)
        # Front edge (+Y)
        tab = create_snap_tab(at_height, "Y")
        tab = tab.translate((x_pos, depth/2, 0))
        part = part.union(tab)
        # Back edge (-Y)
        tab = create_snap_tab(at_height, "Y")
        tab = tab.rotate((0, 0, 0), (0, 0, 1), 180)
        tab = tab.translate((x_pos, -depth/2, 0))
        part = part.union(tab)

    for i in range(num_tabs_y):
        y_pos = -depth/2 + (i + 0.5) * (depth / num_tabs_y)
        # Right edge (+X)
        tab = create_snap_tab(at_height, "X")
        tab = tab.rotate((0, 0, 0), (0, 0, 1), 90)
        tab = tab.translate((width/2, y_pos, 0))
        part = part.union(tab)
        # Left edge (-X)
        tab = create_snap_tab(at_height, "X")
        tab = tab.rotate((0, 0, 0), (0, 0, 1), -90)
        tab = tab.translate((-width/2, y_pos, 0))
        part = part.union(tab)

    return part

def create_snap_tab(base_height, direction):
    """Create a single snap-fit tab"""
    # Tab extends outward from edge
    tab = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .moveTo(0, base_height)
        .lineTo(0, base_height + SNAP_FIT_HEIGHT)
        .lineTo(SNAP_FIT_DEPTH, base_height + SNAP_FIT_HEIGHT - SNAP_FIT_TAPER)
        .lineTo(SNAP_FIT_DEPTH, base_height)
        .close()
        .extrude(SNAP_FIT_WIDTH, both=True)
    )
    return tab

def add_female_snap_fit(part, width, depth, at_height):
    """Add female snap-fit receptacles around perimeter"""
    # Create slots matching the male tabs
    tab_spacing = 60  # mm between tabs (must match male)

    num_tabs_x = max(2, int(width / tab_spacing))
    num_tabs_y = max(2, int(depth / tab_spacing))

    for i in range(num_tabs_x):
        x_pos = -width/2 + (i + 0.5) * (width / num_tabs_x)
        # Front edge
        slot = create_snap_slot(at_height)
        slot = slot.translate((x_pos, depth/2, 0))
        part = part.cut(slot)
        # Back edge
        slot = create_snap_slot(at_height)
        slot = slot.rotate((0, 0, 0), (0, 0, 1), 180)
        slot = slot.translate((x_pos, -depth/2, 0))
        part = part.cut(slot)

    for i in range(num_tabs_y):
        y_pos = -depth/2 + (i + 0.5) * (depth / num_tabs_y)
        # Right edge
        slot = create_snap_slot(at_height)
        slot = slot.rotate((0, 0, 0), (0, 0, 1), 90)
        slot = slot.translate((width/2, y_pos, 0))
        part = part.cut(slot)
        # Left edge
        slot = create_snap_slot(at_height)
        slot = slot.rotate((0, 0, 0), (0, 0, 1), -90)
        slot = slot.translate((-width/2, y_pos, 0))
        part = part.cut(slot)

    return part

def create_snap_slot(base_height):
    """Create a single snap-fit slot"""
    slot = (
        cq.Workplane("XZ")
        .workplane(offset=0)
        .moveTo(-SNAP_FIT_CLEARANCE, base_height)
        .lineTo(-SNAP_FIT_CLEARANCE, base_height + SNAP_FIT_HEIGHT)
        .lineTo(SNAP_FIT_DEPTH + SNAP_FIT_CLEARANCE, base_height + SNAP_FIT_HEIGHT - SNAP_FIT_TAPER + SNAP_FIT_CLEARANCE)
        .lineTo(SNAP_FIT_DEPTH + SNAP_FIT_CLEARANCE, base_height)
        .close()
        .extrude(SNAP_FIT_WIDTH + 2*SNAP_FIT_CLEARANCE, both=True)
    )
    return slot

def add_oring_groove(part, width, depth, at_height):
    """Add o-ring groove for sealing around perimeter"""
    groove = (
        cq.Workplane("XY")
        .workplane(offset=at_height - ORING_GROOVE_DEPTH)
        .rect(width - 2*WALL_THICKNESS + ORING_GROOVE_WIDTH,
              depth - 2*WALL_THICKNESS + ORING_GROOVE_WIDTH)
        .rect(width - 2*WALL_THICKNESS - ORING_GROOVE_WIDTH,
              depth - 2*WALL_THICKNESS - ORING_GROOVE_WIDTH)
        .extrude(ORING_GROOVE_DEPTH)
    )
    part = part.cut(groove)
    return part

# ==================== MAIN MANIFOLD SECTIONS ====================

def create_manifold_base():
    """
    Create the base section with intake tubes
    This mounts on top of the freezer
    """
    # Calculate base dimensions
    base_width = CABINET_WIDTH - 2 * MANIFOLD_OUTER_MARGIN
    base_depth = CABINET_DEPTH - 2 * MANIFOLD_OUTER_MARGIN

    # Create base plate
    base = (
        cq.Workplane("XY")
        .rect(base_width, base_depth)
        .extrude(WALL_THICKNESS)
    )

    # Calculate tube positions
    tube_positions = []
    for i in range(NUM_TUBES_X):
        for j in range(NUM_TUBES_Y):
            # Distribute evenly, avoiding the edges
            x = -base_width/2 + (i + 1) * (base_width / (NUM_TUBES_X + 1))
            y = -base_depth/2 + (j + 1) * (base_depth / (NUM_TUBES_Y + 1))
            tube_positions.append((x, y))

    # Create collection chamber walls above base
    base = (
        base.faces(">Z").workplane()
        .rect(base_width, base_depth)
        .rect(base_width - 2*WALL_THICKNESS, base_depth - 2*WALL_THICKNESS)
        .extrude(MANIFOLD_BASE_HEIGHT)
    )

    # Add tube mounting bosses with through holes
    for x, y in tube_positions:
        # Create boss
        boss = (
            cq.Workplane("XY")
            .workplane(offset=0)
            .moveTo(x, y)
            .circle(TUBE_OD/2 + 3)
            .extrude(MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)
        )
        # Cut hole for tube
        boss = (
            boss.faces(">Z").workplane()
            .moveTo(x, y)
            .circle(TUBE_OD/2 + 0.2)  # Slight clearance for tube insertion
            .cutThruAll()
        )
        base = base.union(boss)

    # Add snap-fit male connectors on top edge
    base = add_male_snap_fit(base, base_width, base_depth, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)

    # Add o-ring groove
    base = add_oring_groove(base, base_width, base_depth, MANIFOLD_BASE_HEIGHT + WALL_THICKNESS)

    return base

def create_transition_section():
    """
    Create the transition section that gradually narrows from base to sensor chamber
    This ensures laminar flow and even distribution
    NOTE: This is too tall for most printers - use create_transition_section_split() instead
    """
    base_width = CABINET_WIDTH - 2 * MANIFOLD_OUTER_MARGIN
    base_depth = CABINET_DEPTH - 2 * MANIFOLD_OUTER_MARGIN
    sensor_width = SENSOR_CHAMBER_WIDTH + 2*WALL_THICKNESS

    # Bottom margin for connecting to base sections
    bottom_margin = 15  # mm solid margin around edge for sealing

    # Create bottom plate with open center for airflow
    bottom_plate = (
        cq.Workplane("XY")
        .rect(base_width, base_depth)
        .extrude(WALL_THICKNESS)
    )

    # Cut center opening, leaving margin around edges for connection
    bottom_plate = (
        bottom_plate.faces(">Z").workplane()
        .rect(base_width - 2*bottom_margin, base_depth - 2*bottom_margin)
        .cutThruAll()
    )

    # Create outer shell with taper - starting from bottom plate
    outer = (
        cq.Workplane("XY")
        .workplane(offset=WALL_THICKNESS)  # Start above bottom plate
        .rect(base_width, base_depth)
        .workplane(offset=TRANSITION_LENGTH)
        .rect(sensor_width, sensor_width)
        .loft(combine=True)
    )

    # Create inner cavity with taper
    inner = (
        cq.Workplane("XY")
        .workplane(offset=WALL_THICKNESS * 2)  # Start above bottom plate
        .rect(base_width - 2*WALL_THICKNESS, base_depth - 2*WALL_THICKNESS)
        .workplane(offset=TRANSITION_LENGTH - WALL_THICKNESS)
        .rect(SENSOR_CHAMBER_WIDTH, SENSOR_CHAMBER_WIDTH)
        .loft(combine=True)
    )

    transition = outer.cut(inner)

    # Add bottom plate
    transition = transition.union(bottom_plate)

    # Add female snap-fit on bottom
    transition = add_female_snap_fit(transition, base_width, base_depth, 0)

    # Add male snap-fit on top
    transition = add_male_snap_fit(transition, sensor_width, sensor_width, TRANSITION_LENGTH + WALL_THICKNESS)

    # Add o-ring groove on top
    transition = add_oring_groove(transition, sensor_width, sensor_width, TRANSITION_LENGTH + WALL_THICKNESS)

    return transition

def create_transition_section_quadrant(quadrant=1):
    """
    Create one quadrant of the transition section split vertically into 4 pieces
    quadrant: 1-4 (1=front-left, 2=front-right, 3=back-left, 4=back-right)

    The transition is split like this (top view):
    +-------+-------+
    |   3   |   4   |  (back)
    +-------+-------+
    |   1   |   2   |  (front)
    +-------+-------+
    """
    base_width = CABINET_WIDTH - 2 * MANIFOLD_OUTER_MARGIN
    base_depth = CABINET_DEPTH - 2 * MANIFOLD_OUTER_MARGIN
    sensor_width = SENSOR_CHAMBER_WIDTH + 2*WALL_THICKNESS
    bottom_margin = 15  # mm solid margin around edge for sealing

    # Joint overlap for assembly
    # With 510mm base and 220mm bed: 510/2 = 255mm, need to be <= 218mm (with 2mm safety)
    # Strategy: Trim outer edges, add small overlap on inner edges
    joint_width = 4  # mm overlap for joining pieces on interior edges
    outer_trim = 38  # mm to trim from each outer edge to fit print bed
    bolt_spacing = 40  # mm between bolt holes

    # Determine quadrant position
    # Quadrant 1: x<0, y<0 (front-left)
    # Quadrant 2: x>0, y<0 (front-right)
    # Quadrant 3: x<0, y>0 (back-left)
    # Quadrant 4: x>0, y>0 (back-right)

    is_right = quadrant in [2, 4]  # x > 0
    is_back = quadrant in [3, 4]   # y > 0

    # Create bottom plate quadrant with open center
    # Split the base into 4 quadrants
    plate_half_width = base_width / 2
    plate_half_depth = base_depth / 2

    # Determine the extents for this quadrant
    # Start with half dimensions, then trim outer edges and add overlap on inner edges
    x_min = 0 if is_right else -plate_half_width
    x_max = plate_half_width if is_right else 0
    y_min = 0 if is_back else -plate_half_depth
    y_max = plate_half_depth if is_back else 0

    # Trim outer edges to fit print bed
    if not is_right:  # Left edge (x min)
        x_min += outer_trim
    else:  # Right edge (x max)
        x_max -= outer_trim

    if not is_back:  # Front edge (y min)
        y_min += outer_trim
    else:  # Back edge (y max)
        y_max -= outer_trim

    # Add small joint overlap on interior edges only
    if is_right:
        x_min -= joint_width / 2
    else:
        x_max += joint_width / 2

    if is_back:
        y_min -= joint_width / 2
    else:
        y_max += joint_width / 2

    quadrant_width = x_max - x_min
    quadrant_depth = y_max - y_min
    x_center = (x_min + x_max) / 2
    y_center = (y_min + y_max) / 2

    # Create bottom plate for this quadrant
    bottom_plate = (
        cq.Workplane("XY")
        .center(x_center, y_center)
        .rect(quadrant_width, quadrant_depth)
        .extrude(WALL_THICKNESS)
    )

    # Cut center opening if not near the outer edge
    # Only cut if we're not at the outer perimeter
    inner_x_min = max(x_min, -base_width/2 + bottom_margin)
    inner_x_max = min(x_max, base_width/2 - bottom_margin)
    inner_y_min = max(y_min, -base_depth/2 + bottom_margin)
    inner_y_max = min(y_max, base_depth/2 - bottom_margin)

    if inner_x_max > inner_x_min and inner_y_max > inner_y_min:
        inner_width = inner_x_max - inner_x_min
        inner_depth = inner_y_max - inner_y_min
        inner_x_center = (inner_x_min + inner_x_max) / 2
        inner_y_center = (inner_y_min + inner_y_max) / 2

        bottom_plate = (
            bottom_plate.faces(">Z").workplane()
            .center(inner_x_center - x_center, inner_y_center - y_center)
            .rect(inner_width, inner_depth)
            .cutThruAll()
        )

    # Create the tapered transition for this specific quadrant
    # Calculate dimensions at bottom and top of transition

    # At bottom (z = WALL_THICKNESS), the quadrant should match our x_min/x_max extents
    # At top (z = TRANSITION_LENGTH + WALL_THICKNESS), calculate the tapered size

    # The full transition goes from base_width to sensor_width over TRANSITION_LENGTH
    # We need to figure out what portion of sensor_width this quadrant represents

    # Calculate the width at the top for this quadrant
    # The sensor opening is in the center, so all quadrants converge toward it
    top_width_full = sensor_width
    # Each quadrant at the top should be sensor_width / 2 (plus small overlap)
    top_half = top_width_full / 2

    # Determine top extents for this quadrant
    top_x_min = -top_half if not is_right else -joint_width / 2
    top_x_max = top_half if is_right else joint_width / 2
    top_y_min = -top_half if not is_back else -joint_width / 2
    top_y_max = top_half if is_back else joint_width / 2

    top_quadrant_width = top_x_max - top_x_min
    top_quadrant_depth = top_y_max - top_y_min
    top_x_center = (top_x_min + top_x_max) / 2
    top_y_center = (top_y_min + top_y_max) / 2

    # Create outer shell for just this quadrant
    # Start at Z=0 (bottom of the plate) and go to top
    outer = (
        cq.Workplane("XY")
        .workplane(offset=0)  # Start at Z=0, same as bottom plate
        .center(x_center, y_center)
        .rect(quadrant_width, quadrant_depth)
        .workplane(offset=TRANSITION_LENGTH + WALL_THICKNESS)  # Go to full height
        .center(top_x_center - x_center, top_y_center - y_center)  # Relative movement
        .rect(top_quadrant_width, top_quadrant_depth)
        .loft(combine=True)
    )

    # Create inner cavity for just this quadrant
    # Inner starts at WALL_THICKNESS (above bottom plate) and is inset by WALL_THICKNESS
    inner_bottom_width = quadrant_width - 2 * WALL_THICKNESS
    inner_bottom_depth = quadrant_depth - 2 * WALL_THICKNESS
    inner_top_width = top_quadrant_width - 2 * WALL_THICKNESS
    inner_top_depth = top_quadrant_depth - 2 * WALL_THICKNESS

    inner = (
        cq.Workplane("XY")
        .workplane(offset=WALL_THICKNESS)  # Start above bottom plate
        .center(x_center, y_center)
        .rect(inner_bottom_width, inner_bottom_depth)
        .workplane(offset=TRANSITION_LENGTH)  # Go to just below top
        .center(top_x_center - x_center, top_y_center - y_center)
        .rect(inner_top_width, inner_top_depth)
        .loft(combine=True)
    )

    quadrant_transition = outer.cut(inner)

    # Union with bottom plate
    section = bottom_plate.union(quadrant_transition)

    # Add bolt holes on interior edges (for joining quadrants)
    total_height = TRANSITION_LENGTH + WALL_THICKNESS

    # Interior edge in X direction (at x=0)
    if not (is_right and not is_back):  # All except quadrant 2 edge
        num_bolts = max(2, int(total_height / bolt_spacing))
        for i in range(num_bolts):
            z_pos = WALL_THICKNESS + (i + 1) * (total_height - WALL_THICKNESS) / (num_bolts + 1)
            hole_x = 0 if is_right else 0
            hole = (
                cq.Workplane("YZ")
                .workplane(offset=hole_x)
                .center(y_center, z_pos)
                .circle(2.5)  # M5 bolt clearance
                .extrude(20, both=True)
            )
            section = section.cut(hole)

    # Interior edge in Y direction (at y=0)
    if not (is_back and not is_right):  # All except quadrant 3 edge
        num_bolts = max(2, int(total_height / bolt_spacing))
        for i in range(num_bolts):
            z_pos = WALL_THICKNESS + (i + 1) * (total_height - WALL_THICKNESS) / (num_bolts + 1)
            hole_y = 0 if is_back else 0
            hole = (
                cq.Workplane("XZ")
                .workplane(offset=hole_y)
                .center(x_center, z_pos)
                .circle(2.5)  # M5 bolt clearance
                .extrude(20, both=True)
            )
            section = section.cut(hole)

    return section

def create_sensor_chamber():
    """
    Create the sensor chamber with mounting for 1"x1" PCB sensor
    This section has the concentrated airflow for measurement
    """
    chamber_size = SENSOR_CHAMBER_WIDTH + 2*WALL_THICKNESS

    # Create chamber body
    chamber = (
        cq.Workplane("XY")
        .rect(chamber_size, chamber_size)
        .extrude(SENSOR_CHAMBER_HEIGHT)
    )

    # Cut internal cavity
    chamber = (
        chamber.faces(">Z").workplane()
        .rect(SENSOR_CHAMBER_WIDTH, SENSOR_CHAMBER_WIDTH)
        .cutBlind(-SENSOR_CHAMBER_HEIGHT + WALL_THICKNESS)
    )

    # Add sensor mount brackets - create mounting struts across chamber
    # Horizontal strut
    strut_h = (
        cq.Workplane("XY")
        .workplane(offset=SENSOR_CHAMBER_HEIGHT/2)
        .center(0, 0)
        .rect(SENSOR_PCB_SIZE + 10, 3)
        .extrude(3)
    )

    # Vertical strut
    strut_v = (
        cq.Workplane("XY")
        .workplane(offset=SENSOR_CHAMBER_HEIGHT/2)
        .center(0, 0)
        .rect(3, SENSOR_PCB_SIZE + 10)
        .extrude(3)
    )

    chamber = chamber.union(strut_h).union(strut_v)

    # Add screw holes for sensor mounting
    hole_distance = SENSOR_PCB_SIZE - 2 * SENSOR_HOLE_OFFSET
    positions = [
        (hole_distance/2, hole_distance/2),
        (-hole_distance/2, hole_distance/2),
        (hole_distance/2, -hole_distance/2),
        (-hole_distance/2, -hole_distance/2),
    ]

    for x, y in positions:
        chamber = (
            chamber.faces(">Z").workplane(offset=-SENSOR_CHAMBER_HEIGHT/2)
            .pushPoints([(x, y)])
            .circle(SENSOR_HOLE_DIA/2)
            .cutBlind(-10)  # Deep enough for mounting screws
        )

    # Add female snap-fit on bottom
    chamber = add_female_snap_fit(chamber, chamber_size, chamber_size, 0)

    # Add male snap-fit on top
    chamber = add_male_snap_fit(chamber, chamber_size, chamber_size, SENSOR_CHAMBER_HEIGHT)

    # Add o-ring groove on top
    chamber = add_oring_groove(chamber, chamber_size, chamber_size, SENSOR_CHAMBER_HEIGHT)

    return chamber

def create_fan_adapter():
    """
    Create adapter from sensor chamber to 120mm fan mount
    """
    chamber_size = SENSOR_CHAMBER_WIDTH + 2*WALL_THICKNESS
    adapter_height = 40

    # Create outer shell transition
    outer = (
        cq.Workplane("XY")
        .rect(chamber_size, chamber_size)
        .workplane(offset=adapter_height)
        .rect(FAN_SIZE + 10, FAN_SIZE + 10)
        .loft(combine=True)
    )

    # Create inner passage
    inner = (
        cq.Workplane("XY")
        .workplane(offset=WALL_THICKNESS)
        .rect(SENSOR_CHAMBER_WIDTH, SENSOR_CHAMBER_WIDTH)
        .workplane(offset=adapter_height - WALL_THICKNESS)
        .circle(FAN_SIZE/2 - 5)
        .loft(combine=True)
    )

    adapter = outer.cut(inner)

    # Add fan mount on top
    fan_mount = create_fan_mount()
    fan_mount = fan_mount.translate((0, 0, adapter_height))
    adapter = adapter.union(fan_mount)

    # Add female snap-fit on bottom
    adapter = add_female_snap_fit(adapter, chamber_size, chamber_size, 0)

    return adapter

# ==================== ASSEMBLY & EXPORT ====================

def split_large_part(part, part_name, max_x, max_y):
    """Split a part that's too large for the print bed"""
    # This is a placeholder - actual implementation would be complex
    # For now, we'll export the full part and note it needs splitting
    print(f"    NOTE: {part_name} exceeds print bed and needs manual splitting")
    return [part]

def generate_all_parts():
    """Generate all parts and export to STL"""
    print("="*60)
    print("AIR FLOW MANIFOLD GENERATOR")
    print("="*60)
    print()

    # Verify design parameters
    multiplier = verify_speed_multiplier()
    print()

    # Check print bed constraints
    base_width = CABINET_WIDTH - 2 * MANIFOLD_OUTER_MARGIN
    base_depth = CABINET_DEPTH - 2 * MANIFOLD_OUTER_MARGIN

    print(f"Base dimensions: {base_width:.1f} x {base_depth:.1f} mm")
    print(f"Transition length: {TRANSITION_LENGTH} mm")
    print(f"Sensor chamber: {SENSOR_CHAMBER_WIDTH + 2*WALL_THICKNESS:.1f} x {SENSOR_CHAMBER_WIDTH + 2*WALL_THICKNESS:.1f} x {SENSOR_CHAMBER_HEIGHT} mm")
    print(f"Print bed limits: {MAX_PRINT_X} x {MAX_PRINT_Y} x {MAX_PRINT_Z} mm")
    print()

    needs_splitting = False
    if base_width > MAX_PRINT_X or base_depth > MAX_PRINT_Y:
        print("WARNING: Base exceeds print bed dimensions!")
        num_x_sections = math.ceil(base_width / MAX_PRINT_X)
        num_y_sections = math.ceil(base_depth / MAX_PRINT_Y)
        print(f"  Recommended split: {num_x_sections} x {num_y_sections} sections")
        needs_splitting = True

    if TRANSITION_LENGTH > MAX_PRINT_Z:
        print("WARNING: Transition section exceeds print bed height!")
        print(f"  Consider splitting into {math.ceil(TRANSITION_LENGTH / MAX_PRINT_Z)} sections")
        needs_splitting = True

    print()
    print("Generating parts...")
    print()

    # Generate each component
    parts_generated = []

    try:
        print("  [1/4] Manifold base with intake tube sockets...")
        base = create_manifold_base()
        cq.exporters.export(base, "manifold_base.stl")
        print("        Exported: manifold_base.stl")
        parts_generated.append("manifold_base")
    except Exception as e:
        print(f"        ERROR: {e}")

    try:
        print("  [2/4] Transition section (base to sensor chamber) - QUADRANT SPLIT...")
        print("        This section is split vertically into 4 quadrants")

        quadrant_names = [
            "front_left",
            "front_right",
            "back_left",
            "back_right"
        ]

        for i in range(1, 5):
            print(f"        Generating quadrant {i} ({quadrant_names[i-1]})...")
            quadrant = create_transition_section_quadrant(quadrant=i)
            filename = f"manifold_transition_{quadrant_names[i-1]}.stl"
            cq.exporters.export(quadrant, filename)
            print(f"        Exported: {filename}")
            parts_generated.append(f"manifold_transition_{quadrant_names[i-1]}")
    except Exception as e:
        print(f"        ERROR: {e}")
        import traceback
        traceback.print_exc()

    try:
        print("  [3/4] Sensor chamber with PCB mount...")
        chamber = create_sensor_chamber()
        cq.exporters.export(chamber, "manifold_sensor_chamber.stl")
        print("        Exported: manifold_sensor_chamber.stl")
        parts_generated.append("manifold_sensor_chamber")
    except Exception as e:
        print(f"        ERROR: {e}")

    try:
        print("  [4/4] Fan adapter (sensor chamber to 120mm fan)...")
        adapter = create_fan_adapter()
        cq.exporters.export(adapter, "manifold_fan_adapter.stl")
        print("        Exported: manifold_fan_adapter.stl")
        parts_generated.append("manifold_fan_adapter")
    except Exception as e:
        print(f"        ERROR: {e}")

    try:
        print("  [Bonus] Individual intake tube (print 9x)...")
        tube = create_intake_tube()
        cq.exporters.export(tube, "intake_tube.stl")
        print("        Exported: intake_tube.stl")
        parts_generated.append("intake_tube")
    except Exception as e:
        print(f"        ERROR: {e}")

    print()
    print("="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print()
    print(f"Parts generated: {len(parts_generated)}")
    for part in parts_generated:
        print(f"  - {part}.stl")
    print()

    if needs_splitting:
        print("IMPORTANT: Some parts exceed print bed dimensions.")
        print("You'll need to split these in your slicer or CAD software.")

    print()
    print("Assembly order:")
    print("  1. manifold_base (bottom, mounts on freezer)")
    print("     NOTE: Base is 510x510mm - use manifold_design_split.py for 3x3 split")
    print("  2. Insert intake_tube (x9) into base from below")
    print("     NOTE: Tubes are now OPEN at bottom for airflow!")
    print("  3. Assemble 4 transition quadrants together using M5 bolts:")
    print("     - manifold_transition_front_left")
    print("     - manifold_transition_front_right")
    print("     - manifold_transition_back_left")
    print("     - manifold_transition_back_right")
    print("     Each quadrant is ~219x219x150mm (trimmed to fit 220x220 bed)")
    print("  4. Attach assembled transition to base (snaps on)")
    print("     NOTE: Bottom plate has open center for airflow!")
    print("  5. manifold_sensor_chamber (snaps onto transition top)")
    print("  6. Install sensor PCB in chamber")
    print("  7. manifold_fan_adapter (top, snaps onto chamber)")
    print("  8. Mount 120mm fan on top")
    print()
    print("Transition quadrant layout (top view):")
    print("  +-------+-------+")
    print("  | back_ | back_ |  (back)")
    print("  | left  | right |")
    print("  +-------+-------+")
    print("  |front_ |front_ |  (front)")
    print("  | left  | right |")
    print("  +-------+-------+")
    print()
    print("Sealing: Use o-rings or silicone gasket maker between sections")
    print("Material: PETG recommended (food-safe, chemical resistant)")
    print()
    print("FIXES APPLIED:")
    print("  ✓ Intake tubes now open at bottom for airflow")
    print("  ✓ Transition split VERTICALLY into 4 quadrants")
    print("    - Each quadrant: ~219x219x150mm (fits 220x220mm bed!)")
    print("    - Outer edges trimmed by 38mm")
    print("    - Inner edges have 4mm overlap for assembly")
    print("  ✓ Transition starts at Z=0 (not floating)")
    print("  ✓ Bottom plate has open center for airflow (15mm margin)")
    print("  ✓ Bolt holes added for joining quadrants (M5 bolts every 40mm)")
    print()
    print("NOTE: The quadrants are trimmed on outer edges to fit your printer.")
    print("      Make sure the base is also trimmed or split to match!")
    print()

if __name__ == "__main__":
    generate_all_parts()
