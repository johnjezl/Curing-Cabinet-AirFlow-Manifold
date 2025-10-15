$fn = 64;
difference() {
	union() {
		difference() {
			translate(v = [-107.5, 107.5, 0]) {
				cube(center = true, size = [219.0, 219.0, 3]);
			}
			translate(v = [-107.5, 107.5, 1.5]) {
				cube(center = true, size = [219.0, 219.0, 3.1]);
			}
		}
		hull() {
			translate(v = [-107.5, 107.5, 0]) {
				cube(center = true, size = [219.0, 219.0, 0.1]);
			}
			translate(v = [-11.0, 11.0, 153]) {
				cube(center = true, size = [26.0, 26.0, 0.1]);
			}
		}
	}
	hull() {
		translate(v = [-107.5, 107.5, 3]) {
			cube(center = true, size = [213.0, 213.0, 0.1]);
		}
		translate(v = [-11.0, 11.0, 150]) {
			cube(center = true, size = [20.0, 20.0, 0.1]);
		}
	}
	union() {
		translate(v = [0, 107.5, 40.5]) {
			rotate(a = [0, 90, 0]) {
				cylinder(center = true, h = 30, r = 2.5);
			}
		}
		translate(v = [0, 107.5, 78.0]) {
			rotate(a = [0, 90, 0]) {
				cylinder(center = true, h = 30, r = 2.5);
			}
		}
		translate(v = [0, 107.5, 115.5]) {
			rotate(a = [0, 90, 0]) {
				cylinder(center = true, h = 30, r = 2.5);
			}
		}
	}
}
