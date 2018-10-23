import sys, re, os

g1_command = re.compile('G1 X(?P<x_home>\d+\.\d+) Y(?P<y_home>\d+\.\d+)')

if len(sys.argv) <= 1:
    # No command line arguments are given 
    file_name_argument = input("Bitte ziehe die zu konvertierende Datei hier hinein -> ")
else:
    file_name_argument = sys.argv[1]

path, file_name = os.path.split(file_name_argument)
if file_name.find('.gcode') == -1:
    print("File must have a .gcode ending!")
    input("Hit enter to close")
    exit()


pressure = input("What should the extrusion pressure be? Numbers only! -> ")
buffer = [';converted using the Voxel8 gcode adjuster tool\n',  # Line 0
          'G90\n',  # Line 1
          '; This line shall be replaced with the G92 command\n',  # Line 2
          'G21\n',
          'M125 S{}	       ;fill pressure tank\n'.format(str(int(pressure)+20)),
          'M236 S{}        ;set extrusion pressure\n'.format(pressure),
          'T1              ;choose silver cartridge\n',
          'M42 P2 S255     ;open valve T1\n',
          'G4 P700\n',
          'G1 F500\n',
          '; End of the preamble inserted by the Voxel8 gcode adjuster tool\n\n\n']

file = open(file_name_argument, 'r')

output_file_name = os.path.join(path, 'mod_'+file_name)
output = open(output_file_name, 'w')

copy_line = False

beginning_of_source_file_trimmed = False
extrusion_preamble_comment = '; Extrusion Preamble'

find_home = False

inside_mid_layer_wipe = False
mid_layer_wipe_comment = '; Mid-layer wipe'

end_of_source_file_trimmed = False
shut_off_heaters_comment = '; shut off heaters'

for i, line in enumerate(file):
    if not beginning_of_source_file_trimmed:
        if line.find(extrusion_preamble_comment) == 0:
            print("Starting copying lines of source file starting line {}".format(i+1))
            copy_line = True
            beginning_of_source_file_trimmed = True
            find_home = True

    if find_home:
        match = g1_command.match(line)
        if match:
            set_home_cmd = 'G92 X{} Y{} Z0.0'.format(match.group('x_home'), match.group('y_home'))
            buffer[2] = set_home_cmd

    if not inside_mid_layer_wipe:
        if line.find(mid_layer_wipe_comment) == 0:
            print("Mid-layer wipe found in line {}".format(i+1))
            copy_line = False
            inside_mid_layer_wipe = True
            buffer.append('\n\n\n; A mid-layer wipe was removed here \n\n\n')
    else:
        if line.find(extrusion_preamble_comment) == 0:
            copy_line = True
            inside_mid_layer_wipe = False

    if not end_of_source_file_trimmed:
        if line.find(shut_off_heaters_comment) == 0:
            print("Stopped copying lines of source file starting line {}".format(i+1))
            copy_line = False
            break

    if copy_line:
        buffer.append(line)


buffer += ['\n\n\n; Start of postamble inserted by the Voxel8 gcode adjuster tool\n\n\n',
           'M400\n',
           'M236 S0\n',
           'M42 P2 S0\n',
           'G91\n',
           'G1 Z10 F5400\n']

output.writelines(buffer)

print('Finished! ^__^')
