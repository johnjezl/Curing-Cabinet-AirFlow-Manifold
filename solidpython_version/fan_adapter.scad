$fn = 64;
difference() {
	union() {
		difference() {
			hull() {
				cube(center = true, size = [48, 48, 0.1]);
				translate(v = [0, 0, 40]) {
					cube(center = true, size = [130, 130, 0.1]);
				}
			}
			hull() {
				translate(v = [0, 0, 3]) {
					cube(center = true, size = [42, 42, 0.1]);
				}
				translate(v = [0, 0, 37]) {
					cylinder(h = 0.1, r = 55.0);
				}
			}
		}
		difference() {
			translate(v = [0, 0, 40]) {
				cube(center = true, size = [130, 130, 4]);
			}
			translate(v = [0, 0, 40]) {
				cylinder(center = true, h = 5, r = 55.0);
			}
		}
	}
	union() {
		translate(v = [-52.5, -52.5, 40]) {
			cylinder(center = true, h = 10, r = 2.25);
		}
		translate(v = [-52.5, 52.5, 40]) {
			cylinder(center = true, h = 10, r = 2.25);
		}
		translate(v = [52.5, -52.5, 40]) {
			cylinder(center = true, h = 10, r = 2.25);
		}
		translate(v = [52.5, 52.5, 40]) {
			cylinder(center = true, h = 10, r = 2.25);
		}
	}
}
