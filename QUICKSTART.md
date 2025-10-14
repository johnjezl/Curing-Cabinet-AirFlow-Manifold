# Quick Start Guide - Air Flow Manifold

## What You Have

A complete 3D-printable air flow manifold system for your curing cabinet that:
- ✅ Concentrates airflow 5x (cabinet 0-1 m/s → sensor sees 0-4.91 m/s)
- ✅ Fits your 550mm × 550mm freezer
- ✅ Mounts a 1"×1" airflow sensor
- ✅ Uses a standard 120mm PC fan
- ✅ Everything fits on your Ender 3 V3 KE printer

## Choose Your Build Path

### Path A: Split Base (RECOMMENDED for Ender 3 V3 KE)
**Pros**: Fits print bed perfectly, easier to print
**Cons**: Requires assembly of 9 base sections with bolts

**Print these files:**
- `base_section_0_0.stl` through `base_section_2_2.stl` (9 parts)
- `manifold_transition.stl` (1 part)
- `manifold_sensor_chamber.stl` (1 part)
- `manifold_fan_adapter.stl` (1 part)
- `intake_tube.stl` (print 9 times)

**Total**: 13 prints

### Path B: Monolithic Base
**Pros**: Fewer parts to assemble
**Cons**: Base (510×510mm) must be split in your slicer

**Print these files:**
- `manifold_base.stl` (1 part - **MUST SPLIT IN SLICER**)
- `manifold_transition.stl` (1 part)
- `manifold_sensor_chamber.stl` (1 part)
- `manifold_fan_adapter.stl` (1 part)
- `intake_tube.stl` (print 9 times)

**Total**: 13 prints (after splitting base)

## Print Settings (PETG Recommended)

```
Material: PETG
Layer Height: 0.2mm
Infill: 25%
Walls: 4
Top/Bottom Layers: 6
Supports: Enable (for fan adapter and possibly transition)
Adhesion: Brim recommended
Print Speed: 60mm/s
Temperature: 235°C / Bed 80°C (adjust for your PETG)
```

## Hardware You'll Need

### Path A (Split Base):
- 24× M4 bolts (25-30mm length)
- 24× M4 nuts
- 24× M4 washers
- 4× M3 screws (10-15mm) for sensor mounting
- Silicone gasket maker (1 tube)
- 9× rubber grommets (38mm ID) for freezer penetrations

### Path B (Monolithic):
- 4× M3 screws (10-15mm) for sensor mounting
- Silicone gasket maker (1 tube)
- 9× rubber grommets (38mm ID) for freezer penetrations

### Both Paths:
- 1× 120mm PC fan (12V PWM recommended)
- 4× M4 screws (20mm) for fan mounting
- 1× Airflow sensor (1"×1" PCB with 4mm corner holes)
- 12V power supply for fan

## Assembly Steps (Split Base - Path A)

### Step 1: Print All Parts
Print all 13 parts using settings above. Estimated print time: 60-80 hours total.

### Step 2: Assemble Base Sections
1. Layout the 9 base sections according to the grid (see README.md)
2. Apply silicone gasket maker to all mating edges
3. Align sections using alignment pins
4. Bolt sections together with M4 hardware
5. Tighten evenly, working from center outward
6. Let gasket cure 24 hours

### Step 3: Prepare Freezer
1. Mark 9 hole positions on freezer top:
   - Grid: 3 rows × 3 columns
   - Spacing: 137.5mm between centers
   - First hole at 137.5mm from each edge
2. Drill 38mm diameter holes
3. Install rubber grommets in each hole

### Step 4: Install Intake Tubes
1. Insert each tube from below through freezer top
2. Tube should protrude ~60mm above freezer
3. Apply silicone sealant around each tube
4. Let cure 24 hours

### Step 5: Mount Base Assembly
1. Place assembled base on top of freezer
2. Align intake tube sockets with protruding tubes
3. Press base down onto tubes
4. Verify all 9 tubes are seated in their sockets

### Step 6: Stack Upper Sections
1. Apply gasket maker to top of base
2. Align transition section and press down firmly
3. Engage snap-fit tabs (should hear/feel clicks)
4. Apply gasket maker to top of transition
5. Snap on sensor chamber
6. Apply gasket maker to top of chamber
7. Snap on fan adapter

### Step 7: Install Sensor and Fan
1. Mount 1"×1" sensor PCB in chamber using M3 screws
2. Connect sensor wiring (route through fan adapter)
3. Mount 120mm fan on top using M4 screws
4. Connect fan power

### Step 8: Test
1. Power on fan at low speed
2. Check for air leaks (listen/feel)
3. Verify sensor readings
4. Calculate cabinet airflow = sensor reading ÷ 4.91
5. Adjust fan speed as needed

## Calibration

Your sensor should read approximately 5× the actual cabinet airflow (actual multiplier: 4.91×).

**Example**:
- Target cabinet airflow: 0.5 m/s
- Expected sensor reading: 0.5 × 4.91 = 2.46 m/s
- Adjust fan PWM until sensor shows ~2.46 m/s

## Troubleshooting

**Air leaks?**
- Check all snap-fits are fully engaged
- Add more gasket maker at joints
- Check freezer penetrations are sealed

**Low airflow?**
- Check fan is running at correct voltage
- Verify all 9 tubes are open
- Check sensor chamber isn't blocked

**Weird sensor readings?**
- Ensure sensor is firmly mounted (no vibration)
- Check sensor element is clean
- Verify airflow is smooth (not turbulent)

## Next Steps

Once assembled and tested:
1. Fine-tune fan speed for your desired airflow
2. Set up control system (Arduino/Raspberry Pi/etc) to:
   - Read sensor continuously
   - Adjust fan PWM to maintain target airflow
   - Log data over time
3. Begin curing process!

## Files Reference

- **README.md** - Complete documentation
- **manifold_design.py** - Python source for monolithic design
- **manifold_design_split.py** - Python source for split base
- **requirements.txt** - Python dependencies (if you want to modify design)

## Need to Modify the Design?

1. Install Python 3.x
2. Run: `pip install -r requirements.txt`
3. Edit parameters in `manifold_design.py`
4. Run: `python manifold_design.py` to regenerate STL files

See README.md for detailed modification instructions.

---

**Questions?** Check README.md for detailed information on every aspect of the design.

**Problems?** Common issues and solutions are in the Troubleshooting section of README.md.

**Happy printing and curing!** 🥓
