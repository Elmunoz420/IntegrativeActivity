INTEGRATIVE ACTIVITY – MULTI-AGENT SYSTEMS WITH COMPUTER GRAPHICS
=================================================================

This project implements a simple warehouse simulation using 
autonomous multi-agent robots and a 3D visualization in Unity.

-----------------------------------------------------------------
PART 1 – MULTI-AGENT SYSTEM (PYTHON)
-----------------------------------------------------------------

[Description]
- 5 robots move autonomously inside a warehouse.
- Robots can move, pick boxes, drop boxes, and detect conflicts.
- Boxes must be stacked (max 5 per stack) in a DROP row.
- No central controller is used — robots make decisions using 
  only local sensing.

[Run Simulation]
Command:
   python sim.py

[Outputs]
The simulation reports:
1. Number of steps
2. Number of robot movements
3. Whether all boxes were organized

Example Output:
   Steps: 3000
   Moves: 180–250
   Organized: False

[Files]
- sim.py ........... Main simulation script
- Integrative Activity - Multiagent Systems with CG.pdf ....... Agent protocol, cooperative strategy, and analysis

-----------------------------------------------------------------
PART 2 – COMPUTER GRAPHICS (UNITY)
-----------------------------------------------------------------

[Includes]
- Warehouse environment (floor, walls, door)
- Shelves
- Boxes
- Robots
- Basic movement animation
- Directional light and optional robot lights
- Simple collision handling

[How to Import]
1. Go to: Assets -> Import Package -> Custom Package
2. Select the .unitypackage file included in this repository.

-----------------------------------------------------------------
TEAM MEMBERS
-----------------------------------------------------------------
- Juan Pablo Buenrostro
- Joaquín Hiroki Campos
- Esteban Camilo Muñóz Rosero
- Fernanda Yaltzin Jiménez Ramos
