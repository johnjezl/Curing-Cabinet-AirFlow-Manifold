$fn = 64;
translate(v = [0, 0, 40.0]) {
	difference() {
		union() {
			difference() {
				cube(center = true, size = [48, 48, 80]);
				translate(v = [0, 0, -1.5]) {
					cube(center = true, size = [42, 42, 77]);
				}
			}
			translate(v = [0, 0, 0]) {
				cube(center = true, size = [35.4, 3, 3]);
			}
			translate(v = [0, 0, 0]) {
				cube(center = true, size = [3, 35.4, 3]);
			}
		}
		union() {
			translate(v = [-11.7, -11.7, -5]) {
				cylinder(h = 15, r = 2.0);
			}
			translate(v = [-11.7, 11.7, -5]) {
				cylinder(h = 15, r = 2.0);
			}
			translate(v = [11.7, -11.7, -5]) {
				cylinder(h = 15, r = 2.0);
			}
			translate(v = [11.7, 11.7, -5]) {
				cylinder(h = 15, r = 2.0);
			}
		}
	}
}
