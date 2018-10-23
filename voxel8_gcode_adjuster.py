# -*- coding: utf-8 -*-

import sys
import re
import os

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")


def enter_prompt():
    input("Press Enter / Drücke Enter ")


def conversion_error():
    print("File cannot be converted! / Datei kann nicht konvertiert werden!")


g1_command = re.compile('G1 X(?P<x>\d+\.\d+) Y(?P<y>\d+\.\d+) .* F(?P<speed>\d+)$')
extrusion_pressure_cmd = re.compile('M236 S(?P<extr_pressure>\d+)')

if len(sys.argv) <= 1:
    file_name_argument = input("Drag&drop file to be converted / Zu konvertierende Datei hier hin ziehen -> ")
else:
    file_name_argument = sys.argv[1]

path, file_name = os.path.split(file_name_argument)
if file_name.find('.gcode') == -1:
    print("File must have a .gcode ending! / Datei muss eine .gcode Dateiendung haben!")
    enter_prompt()
    exit()


buffer = ['; Converted using the Voxel8 gcode adjuster tool\n',  # Line 0
          'G90\n',  # Line 1
          '; This line shall be replaced with the G92 command\n',  # Line 2
          'G21\n',  # Line 3
          '; This line will be replaced with the tank pressure setting command M125\n',  # Line 4
          '; This line will be replaced with the extrusion pressure setting command M236\n',  # Line 5
          'T1              ;choose silver cartridge\n',
          'M42 P2 S255     ;open valve T1\n',
          'G4 P700\n',
          'G1 F500\n',
          '; End of the preamble inserted by the Voxel8 gcode adjuster tool\n\n\n']

file = open(file_name_argument, 'r')

copy_line = False

beginning_of_source_file_trimmed = False
extrusion_preamble_comment = '; Extrusion Preamble'

find_home = False
home_found = False

inside_mid_layer_wipe = False
mid_layer_wipe_comment = '; Mid-layer wipe'

end_of_source_file_trimmed = False
shut_off_heaters_comment = '; shut off heaters'

extrusion_pressure_found = False
extrusion_pressure = 0
new_base_speed = 1
orig_base_speed = 1

for i, line in enumerate(file):
    if not extrusion_pressure_found:
        match = extrusion_pressure_cmd.match(line)
        if match:
            read_pressure = match.group('extr_pressure')
            print("In the source file an extrusion pressure of {}psi is defined. / "
                  "In der Originaldatei wird ein Extrusionsdruck von {}psi verwendet. ".format(read_pressure, read_pressure))
            print("Press enter to keep the defined pressure or enter a new value. /"
                  "Drücke Enter um den Druck beizubehalten oder gib einen neuen Wert ein.")
            extrusion_pressure = input("-> ")
            if not extrusion_pressure:
                extrusion_pressure = int(read_pressure)
            else:
                extrusion_pressure = int(extrusion_pressure)

            buffer[4] = 'M125 S{}	       ;fill pressure tank\n'.format(str(int(extrusion_pressure) + 20))
            buffer[5] = 'M236 S{}        ;set extrusion pressure\n'.format(extrusion_pressure)
            extrusion_pressure_found = True

    if not beginning_of_source_file_trimmed:
        if line.find(extrusion_preamble_comment) == 0:
            copy_line = True
            beginning_of_source_file_trimmed = True
            find_home = True

    if find_home:
        match = g1_command.match(line)
        if match:
            set_home_cmd = 'G92 X{} Y{} Z0.0'.format(match.group('x'), match.group('y'))
            buffer[2] = set_home_cmd

            orig_base_speed = match.group('speed')
            print("In the source file a base speed of {} is defined. / "
                  "In der Orininaldatei wird eine Basisgeschwindigkeit von {} definiert.".format(orig_base_speed, orig_base_speed))
            print("Press enter to keep the base speed or enter a new value. /"
                  "Drücke Enter um die Basisgeschwindigkeit beizubehalten oder gib einen neuen Wert ein.")
            new_base_speed = input("-> ")
            if not new_base_speed:
                new_base_speed = int(orig_base_speed)
            else:
                new_base_speed = int(new_base_speed)
            home_found = True
            find_home = False

    if not inside_mid_layer_wipe:
        if line.find(mid_layer_wipe_comment) == 0:
            print("A mid-layer wipe was removed in line {} / Ein mid-layer wipe wurde in Zeile {} entfernt".format(i+1, i+1))
            copy_line = False
            inside_mid_layer_wipe = True
            buffer.append('\n\n\n; A mid-layer wipe was removed here \n\n\n')
    else:
        if line.find(extrusion_preamble_comment) == 0:
            copy_line = True
            inside_mid_layer_wipe = False

    if not end_of_source_file_trimmed:
        if line.find(shut_off_heaters_comment) == 0:
            copy_line = False
            break

    if copy_line:
        if orig_base_speed != new_base_speed:
            match = g1_command.match(line)
            if match:
                # print(int(match.group('speed'))/new_base_speed)
                # G1 commands always have a speed of 1.0 to 1.1 times the new_base_speed!
                read_speed = match.group('speed')
                ratio = int(read_speed)/int(orig_base_speed)
                new_speed = ratio*new_base_speed
                line = line.replace("F"+read_speed, "F"+str(new_speed))
        buffer.append(line)


buffer += ['\n\n\n; Start of postamble inserted by the Voxel8 gcode adjuster tool\n\n\n',
           'M400\n',
           'M236 S0\n',
           'M42 P2 S0\n',
           'G91\n',
           'G1 Z10 F5400\n']

if not extrusion_pressure_found:
    print("No extraction pressure was found in the original file! / "
          "In der Originaldatei wurde kein Extraktionsdruck gefunden! ")
    conversion_error()
    enter_prompt()
    exit()

if not home_found:
    print("Could not find home coordinates! / "
          "Die Ursprungskoordinaten wurden nicht gefunden! ")
    conversion_error()
    enter_prompt()
    exit()

output_file_name = os.path.join(path, 'mod_'+file_name)
output = open(output_file_name, 'w')
output.writelines(buffer)

print('Finished! / Fertig! ^__^')
enter_prompt()
