"""
grn/ — Gene Regulatory Network layer for morphogenesis-engine.

Modules
-------
grn.grn       GRNState: per-cell internal gene-activity variables
grn.signals   SignalField: diffusing morphogen gradients
grn.mapper    GRN state → cell physics parameters
grn.presets   Named GRN configurations (tree, coral, spiral)
grn.runner    GRNSimulation: couples GRN layer to physics engine
"""
