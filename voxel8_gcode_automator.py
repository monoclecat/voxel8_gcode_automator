import sys, re
g1_xy_code_with_speed = re.compile('G1 X(?P<x_coord>(\d+\.\d+)) Y(?P<y_coord>(\d+\.\d+)) F(?P<speed>(\d+\.\d+))')
# g1_no_xy_with_speed = re.compile('G1 (?P<number>(\d+\.\d+)) F(?P<speed>(\d+\.\d+))')
turn_off_temp = re.compile('M104 S0.*')

MAX_SPEED = 800.0

if len(sys.argv) != 2 or not sys.argv[1].find('.gcode'):
    print("Usage: python voxel8_gcode_automator.py file_to_modify.gcode")

file = open(sys.argv[1], 'r')
output = open('mod_'+sys.argv[1], 'w')
pre_code = open('pre_gcode_snippet.gcode', 'r')
post_code = open('post_gcode_snippet.gcode', 'r')

output.write(pre_code.read())

start_copy = False
stop_copy = False
for i, line in enumerate(file):
    if not start_copy:
        match = g1_xy_code_with_speed.match(line)
        if match and float(match.group('speed')) < MAX_SPEED:
            print("G92 X"+match.group('x_coord')+" Y"+match.group('y_coord')+" Z0")
            start_copy = True
    if start_copy:
        match = turn_off_temp.match(line)
        if match:
            output.write(post_code.read())
            break
    if start_copy:
        output.write(line)

print("Finished! ^__^ Feed me more files!")
