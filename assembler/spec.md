# Output formatting for asmv3
There are 3 main things grouped together: entry point, functions, and data.

Since this is for assembling to flat binary, this assembler will try to organize it as much a possible without an executable format

As such, these things are rearranged to always have the entry point (main function) first, then functions, then data