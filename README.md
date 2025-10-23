# Air Flow Manifold for Curing Cabinet

3D-printable manifold system designed to control and measure airflow in a curing cabinet for dry-cured sausage production.

## Design Goals

- **Airflow Control**: 0-1 m/s cabinet airflow, controllable in 0.05 m/s increments
- **Speed Magnification**: 5x concentration (cabinet 0-1 m/s → sensor sees 0-5 m/s)
- **Sensor Integration**: Mount for 1"×1" PCB with 4mm corner mounting holes
- **Fan Control**: Standard 120mm PWM fan mount for active airflow control
- **Modular Design**: Snap-fit assembly with multiple printable sections

## Design Specifications

### Airflow Performance
- **Cabinet Size**: 550mm × 550mm interior cross-section
- **Intake Tubes**: 9 tubes (3×3 grid), 35mm ID, 39.5mm OD
- **Tube Threads**: ISO metric M39.5×2.5 external threads (using cq_warehouse IsoThread)
- **Total Intake Area**: 8,659 mm²
- **Sensor Chamber**: 42mm × 42mm = 1,764 mm²
- **Actual Speed Multiplier**: 4.91x (within 2% of target)

### Physical Dimensions
- **Full Assembly Height**: ~290mm (base 43mm + transition 150mm + chamber 80mm + adapter 44mm)
- **Base Footprint**: 510mm × 510mm (fits on freezer with 20mm margin each side)
- **Sensor Chamber**: 48mm × 48mm × 80mm
- **Fan Mount**: Standard 120mm × 120mm with 105mm bolt circle

### Materials
- **Recommended**: PETG (food-safe, chemical resistant, easy to print, temperature stable)
- **Alternative**: ABS (higher temperature resistance) or ASA (UV resistant)
- **Not Recommended**: PLA (not food-safe, poor temperature stability)

## Files

### Main Design Files
- **manifold_design.py** - Main design generator (monolithic parts with IsoThread)
- **manifold_design_split.py** - Split base generator (for print bed constraints)
- **pcb_holder.py** - PCB chip holder for sensor mounting
- **print_layout_transitions.py** - Multi-quadrant transition layout for printing
- **test_tube_and_nut.py** - Test script for tube and nut generation
- **requirements.txt** - Python dependencies

### Dependencies
- **cadquery** - 3D CAD library for Python
- **cq_warehouse** - Thread generation library (for perfect ISO metric threads)
  - Install: `python3 -m pip install git+https://github.com/gumyr/cq_warehouse.git#egg=cq_warehouse`

### Generated STL Files

#### Option 1: Monolithic Base (requires large printer or splitting in slicer)
- **manifold_base.stl** (510×510×43mm) - Base with 9 intake tube sockets
- **manifold_transition.stl** (510×510→48×48×150mm) - Tapered transition
- **manifold_sensor_chamber.stl** (48×48×80mm) - Sensor mounting chamber
- **manifold_fan_adapter.stl** (48×48→130×130×44mm) - Fan adapter
- **intake_tube.stl** (~40×40×79mm with flange) - Individual tube with ISO metric threads (print 9×)
- **nut.stl** (~55×55×16mm) - Threaded mounting nut for each tube (print 9×)

#### Option 2: Split Base (fits Ender 3 V3 KE)
- **base_section_0_0.stl** through **base_section_2_2.stl** (9 sections, each ~170×170×43mm)
- Plus same transition, chamber, adapter, and tubes as Option 1

## Assembly Instructions

### Option 1: Monolithic Base

1. **Print Parts**:
   - 1× manifold_base (may need to split in slicer for Ender 3 V3 KE)
   - 1× manifold_transition
   - 1× manifold_sensor_chamber
   - 1× manifold_fan_adapter
   - 9× intake_tube

2. **Prepare Freezer**:
   - Drill 9 holes in freezer top (39.5mm diameter for tube body, or slightly larger for clearance)
   - Position in 3×3 grid: spacing based on base design
   - Recommended spacing: evenly distributed across 510mm base

3. **Install Intake Tubes**:
   - Insert tubes from above (flange stays on top)
   - Tube drops down through freezer top
   - Add gasket/o-ring between flange and freezer surface
   - Thread nut from below (inside freezer) onto tube threads
   - Tighten nut to secure tube and compress gasket
   - **Threads**: ISO metric M39.5×2.5, no-twist IsoThread design for perfect fit

4. **Assemble Manifold**:
   - Place manifold_base on top of freezer
   - Insert tubes into base sockets from below
   - Apply gasket maker or o-ring to base top edge
   - Snap manifold_transition onto base
   - Verify snap-fit engagement
   - Apply gasket maker to transition top
   - Snap manifold_sensor_chamber onto transition
   - Mount sensor PCB (1"×1") using M3 screws in corner holes
   - Apply gasket maker to chamber top
   - Snap manifold_fan_adapter onto chamber
   - Mount 120mm fan using M4 screws (105mm bolt circle)

### Option 2: Split Base

1. **Print Parts**:
   - 9× base sections (base_section_0_0 through base_section_2_2)
   - 1× manifold_transition
   - 1× manifold_sensor_chamber
   - 1× manifold_fan_adapter
   - 9× intake_tube
   - **Hardware needed**: ~24 M4 bolts, ~48 M4 nuts/washers

2. **Assemble Base Sections**:
   - Layout all 9 sections according to diagram (see below)
   - Alignment pins on one edge mate with holes on adjacent section
   - Join sections with M4 bolts through edge holes
   - Apply silicone gasket maker to all joints
   - Tighten bolts evenly to avoid warping

3. **Install and Continue**:
   - Follow steps 2-4 from Option 1

### Section Layout (Top View)
```
     +-------+-------+-------+
     | 0,2   | 1,2   | 2,2   |  ← Back of freezer
     +-------+-------+-------+
     | 0,1   | 1,1   | 2,1   |  ← Middle
     +-------+-------+-------+
     | 0,0   | 1,0   | 2,0   |  ← Front of freezer
     +-------+-------+-------+
```

## Print Settings

### Recommended Settings
- **Layer Height**: 0.2mm (standard quality)
- **Infill**: 20-30% (gyroid or grid pattern)
- **Perimeters**: 3-4 walls
- **Top/Bottom Layers**: 5-6 layers
- **Supports**: May be needed for:
  - Fan adapter overhang
  - Sensor chamber struts (if needed)
- **Adhesion**: Brim recommended for tall parts
- **Print Speed**: 50-80mm/s (PETG works well at these speeds)

### Part-Specific Notes
- **Base Sections**: Print flat (as oriented), no supports needed
- **Transition**: May need supports if overhang >45° (depends on taper)
- **Sensor Chamber**: Supports may be needed for struts
- **Fan Adapter**: Supports recommended for overhang
- **Intake Tubes**: Print vertically (flange down) for best thread quality, no supports needed
- **Nuts**: Print flat (base down), no supports needed. Threads print cleanly with IsoThread design

## Sealing and Finishing

### Between Manifold Sections
- **Option 1**: O-rings in grooves (design includes o-ring grooves)
  - Recommended size: 3mm cross-section
  - Groove is 3mm wide × 1.5mm deep
- **Option 2**: Silicone gasket maker (e.g., Permatex, high-temp RTV)
  - Apply thin bead around perimeter
  - Assemble while wet
  - Allow 24hrs to cure before operation

### Between Base Sections (Split Version)
- **Required**: Silicone gasket maker on all joints
- Apply to mating surfaces before bolting together
- Critical for air-tight operation

### Freezer Penetrations
- Use rubber gaskets between tube flange and freezer top surface
- Threaded nut secures from inside freezer and compresses gasket
- Optional: Add silicone caulk around tube on both sides for extra seal
- Ensure air-tight seal to prevent outside air infiltration
- Hex wrench grips on nut allow proper tightening without over-torquing

## Operation

### Airflow Calibration
1. Install airflow sensor in sensor chamber
2. Set fan to known speed (e.g., 50% PWM)
3. Measure sensor reading
4. Calculate actual cabinet airflow: sensor_reading ÷ 4.91
5. Adjust fan speed to achieve desired cabinet airflow
6. Example: To get 0.5 m/s in cabinet, set fan to achieve 2.45 m/s at sensor

### Expected Performance
- **Cabinet Range**: 0-1 m/s (0-200 fpm)
- **Sensor Range**: 0-5 m/s (0-1000 fpm)
- **Resolution**: 0.05 m/s cabinet steps = 0.25 m/s sensor steps
- **Distribution**: 9 intake points ensure even airflow across cabinet

## Sensor Specifications

### Required Sensor Specs
- **PCB Size**: 1" × 1" (25.4mm × 25.4mm)
- **Mounting**: 4mm holes at corners, 1mm from edge (23.4mm hole spacing)
- **Measurement Range**: 0-7.2 m/s (using 0-5 m/s range recommended)
- **Sensing Element**: Should be centered on PCB for accurate reading

### Recommended Sensors
- **Option 1**: Sensirion SFM3000 series (I2C, high accuracy)
- **Option 2**: Honeywell AWM series (analog, cost-effective)
- **Option 3**: Modern Device Wind Sensor Rev. C (Arduino-compatible)

## Maintenance

### Regular Cleaning
- Remove fan and adapter section
- Clean fan blades and grille
- Inspect sensor chamber for debris
- Wipe down interior surfaces
- Check for mold growth (should be minimal with proper airflow)

### Seal Inspection
- Check snap-fit connections annually
- Re-apply gasket maker if air leaks detected
- Check for warping or degradation of printed parts

### Calibration Verification
- Re-calibrate sensor reading every 6 months
- Check that multiplier ratio remains ~4.91×
- If ratio changes significantly, inspect for:
  - Air leaks at joints
  - Debris buildup in transition section
  - Damaged intake tubes

## Troubleshooting

### Low Airflow
- **Check**: Fan operation (voltage, RPM)
- **Check**: Intake tubes not blocked
- **Check**: Sensor chamber not obstructed
- **Check**: All snap-fit connections secure
- **Check**: No air leaks at gaskets/seals

### Uneven Airflow
- **Check**: All 9 intake tubes installed and open
- **Check**: Transition section properly seated
- **Check**: No debris blocking specific tubes
- **Consider**: Adding flow straighteners in transition section

### Sensor Readings Inconsistent
- **Check**: Sensor mounting secure (no vibration)
- **Check**: Sensor element clean and unobstructed
- **Check**: Airflow is laminar (not turbulent) at sensor
- **Check**: Sensor chamber properly sealed
- **Consider**: Adding flow straightener before sensor

### Air Leaks
- **Check**: All snap-fits fully engaged (should hear/feel click)
- **Check**: O-rings seated in grooves
- **Check**: Gasket maker fully cured (24hrs)
- **Check**: Freezer penetrations sealed
- **Test**: Smoke test - introduce smoke at intake, watch for leaks

## Design Modifications

### Changing Airflow Range
To modify for different airflow ranges, adjust these parameters in [manifold_design.py](manifold_design.py):

```python
# For different speed multiplier:
TARGET_SPEED_MULTIPLIER = 5  # Change this value

# Then adjust either:
# - Number of tubes: NUM_TUBES_X, NUM_TUBES_Y
# - Tube diameter: TUBE_ID
# - Sensor chamber size: SENSOR_CHAMBER_WIDTH

# Formula: multiplier = (intake_area) / (sensor_chamber_area)
# intake_area = NUM_TUBES_X * NUM_TUBES_Y * pi * (TUBE_ID/2)²
# sensor_chamber_area = SENSOR_CHAMBER_WIDTH²
```

### Adapting for Different Cabinet Size
```python
# Change cabinet dimensions:
CABINET_WIDTH = 550  # mm
CABINET_DEPTH = 550  # mm

# Adjust tube spacing automatically or manually:
TUBE_SPACING_X = CABINET_WIDTH / (NUM_TUBES_X + 1)
TUBE_SPACING_Y = CABINET_DEPTH / (NUM_TUBES_Y + 1)
```

### Different Fan Size
```python
# For 80mm fan:
FAN_SIZE = 80  # mm
FAN_MOUNT_HOLE_SPACING = 71.5  # mm

# For 140mm fan:
FAN_SIZE = 140  # mm
FAN_MOUNT_HOLE_SPACING = 124.5  # mm
```

## Advanced Features

### Snap-Fit Design
- Tapered male tabs with female slots
- 0.3mm clearance for easy assembly
- 2mm engagement depth for secure hold
- 8mm tab height for adequate strength
- Tabs spaced 60mm around perimeter

### O-Ring Grooves
- 3mm wide × 1.5mm deep
- Located at top of each section
- Standard AS568 o-ring sizes compatible
- Groove around perimeter (not at snap-fits)

### Alignment Features
- Split base sections have male/female alignment pins
- 6mm diameter pins prevent misalignment
- 10mm pin height ensures positive engagement
- Prevents rotation during bolting

## Theory of Operation

### Venturi Effect
This manifold uses the principle of conservation of mass (continuity equation) for incompressible flow:

```
A₁ × V₁ = A₂ × V₂

Where:
  A = cross-sectional area
  V = velocity

Therefore: V₂ = V₁ × (A₁ / A₂)
```

In our design:
- A₁ = 8,659 mm² (intake area)
- A₂ = 1,764 mm² (sensor chamber area)
- V₂ = V₁ × (8659 / 1764) = V₁ × 4.91

### Laminar Flow Transition
The gradual 150mm transition section ensures:
- Smooth convergence (minimize turbulence)
- Even flow distribution
- Accurate sensor readings
- Low pressure drop

The taper angle is:
```
θ = arctan((510 - 42) / (2 × 150)) ≈ 57.3°
```

This is steeper than ideal (10-15° preferred for laminar flow), but necessary for compact design. The long transition length helps compensate.

### Pressure Considerations
Pressure drop through manifold (estimated):
- Intake tubes: ~5 Pa
- Transition: ~10 Pa
- Sensor chamber: ~5 Pa
- Fan adapter: ~5 Pa
- **Total**: ~25 Pa (~0.1 inch H₂O)

Standard 120mm PC fans can easily overcome this at low-medium speeds.

## License

This design is provided as-is for personal use. Feel free to modify and adapt for your needs.

## Credits

Designed using:
- **CadQuery** 2.4.0 (Python-based CAD library)
- **Python** 3.x

For questions or improvements, please open an issue or submit a pull request.

## Changelog

### Version 2.0 (Current)
- **IsoThread Integration**: Perfect ISO metric M39.5×2.5 threads using cq_warehouse
  - External threads on intake tubes (no twist, uniform profile)
  - Internal threads on mounting nuts (perfect mate)
  - Valley cut technique for visible, functional threads
- **Improved Tube Mounting**: Threaded nut system for secure, adjustable installation
- **Thread Design**:
  - Tube: Valley depth = 1.125mm (half wall thickness)
  - Nut: Bore matches tube OD, threads through full height
  - Both use IsoThread for perfect engagement
- **Code Cleanup**: Removed unused functions, imports, and dead code
- **New Test Scripts**: test_tube_and_nut.py for validation printing

### Version 1.0 (Initial)
- Modular 4-piece design with snap-fits
- 5x speed magnification (4.91x actual)
- 9-tube intake (3×3 grid, 35mm ID)
- Split base option for Ender 3 print bed
- 120mm fan mount
- 1"×1" sensor PCB mount
- O-ring grooves for sealing
- Alignment pins for split base assembly

---

**Happy Curing!** 🥓🌭
