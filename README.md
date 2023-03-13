# Sketch Software For CNC
This project includes a sketching software for toolpaths for basic CNC.

NOTE : Canvas width is 80% if fullscreen width and height is almost full-height. mm per pixels value is currently 0.3636 (adjusted so that the canvas size and bed size of my cnc matches) but it can be easily adjusted in the utils.py files to match own requirements.

Features:
References : While drawing a shape all sorts of useful reference lines are drawn on canvas for effective and easy drawing

Buttons and Labels: 
  - Status label includes cursor position, input buffer, and other information regarding the current feature used in program (will be detailed later on)
  - Buttons to select features for different shapes (Rect., Parm., regular polygons, Arc, circle, ellipses, etc) which are generated as a combination of lines and arcs
  - Generation of gcodes for engraver (safe height and work height must be entered before generating gcode)
  - Generation of gcode of milling machine (Keep in mind that the gcodes for cnc are actually only 2d shapes extruded in third axis (safe z height, z coord. of top of  stock, stock height and cut-depth of machine should be entered)
  - Preview mode : The outer-cut and inner-cut for a shape is shown based on its count of parent shapes (How many shapes enclose the given shape). This feature will    allow for further upgrade into pocket milling instead of just contour milling.

Modes/Features:
  -Select : you can select and move edges, arcs and also delete them. vertices can be moved and deleted too. (If the vertex to be moved lies on line then no problem but the vertex of a arc cannot be moved.
  -Line : no explanation needed
  -Rectangle : 2-point rectangle
  -Parallelogram : 3-point parallelogram
  -Polygon : A n sided polygon can be drawn, where n>1. When n=2, its just a line so you can draw midpoint line. The value 'n' can be entered anytime while in this mode and it changes number of sides. They value 'n' is shown in Status label. To change it just enter a number and press 'enter' key
  -Arc : An 3-point arc where first 2 points are start and end points and last one is for calculating center and radius. Axial ratio can be changed through buffer to draw elliptical arc too (although it is not fully reliable at the moment)
  - Circle : 2 point circle (can be turned into ellipse by changing axial ratio but not fully functional so ignore axial ratio for now)
  - Z-safe, Z-work, Stock-top, stock-height, cut-depth : all are values for generating toolpaths and can be entered by clicking the button and entering value on keyboard
  - Generate-Engraving, Generate-Milling : Calculate and generate toolpaths for the shape, filename can be entered at any of these two modes
  - Save : Save gcode into gcodes/{filename}.gcode where filename is entered in above described mode.  
  
  
** Things not included in current version **
- the diameter of toolpath is not taken into account. So although in preview mode, the outer-cut contour and inner-cut contour are shown but actually they are not implemented in gcode

