"""R2 indoor-localization risk assessment (Dayana Romo's individual activity).

Takes position readings taken at tape-measured grid points, checks them against the
Risk Reduction Plan limit (<= 10 cm at every point), and reports whether the R2 warning
signal is tripped. Runs on simulated sensors now; loads real bench-test CSV data later.
"""
__version__ = "1.0.0"
