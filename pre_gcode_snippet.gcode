;converted using the Voxel8 gcode automation tool
;
G90
G21

M125 S40		;fill pressure tank
M236 S15      	;set extrusion pressure 15


T1			    ;choose silver cartridge
M42 P2 S255		;open valve T1
G4 P700
G1 F500

