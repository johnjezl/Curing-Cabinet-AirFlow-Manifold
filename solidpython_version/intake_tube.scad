$fn = 64;
difference() {
	union() {
		difference() {
			cylinder(h = 60, r = 19.0);
			translate(v = [0, 0, -0.05]) {
				cylinder(h = 60.1, r = 17.5);
			}
		}
		translate(v = [0, 0, 58]) {
			cylinder(h = 2, r = 20.0);
		}
	}
	translate(v = [0, 0, 58]) {
		cylinder(h = 2.1, r = 18.5);
	}
}
