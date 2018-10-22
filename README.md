In our lab we have a Voxel8 3D printer that can print pastes. We modified the printer by adding our own syringes but
now we can't use the gcodes directly outputted by the Voxel8 online slicer. The dimension don't fit anymore and when
the printer performs certain tasks, such as the 'mid-layer wipe', it destroys the nozzle.

The slicer is not open source, sadly.

In the past the gcode file was edited manually - a tedious job I wish to end with this little Python script.

It does three things:
- Adds a custom preamble to the output file, replacing the preamble of the original.
- Removes 'Mid-layer wipes'.
- Replaces the postamble of the original file with a custom one.