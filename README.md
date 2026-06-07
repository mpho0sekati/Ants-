# Ants Simulation

This repository contains a simple ant colony simulation with two ant roles:
- `collector` ants that search for food and return it to the nest
- `protector` ants that defend the nest from enemies

The code also loads learning data from `learn_data.json` and updates heuristic values as it runs.

## Run the GUI

```powershell
cd "C:\Users\Mpho Sekati\Ants_repo"
python ants_simulation_tk.py
```

## Controls
- Left click the grid to add food
- Right click the grid to spawn an enemy
- Start / Pause button
- Step button (advance one simulation tick)
- Reset button
- Speed slider

## Notes
- `learn_data.json` stores heuristic parameters and past episode summaries.
- The simulation adjusts exploration rate based on its recent performance.
- `tkinter` is included with standard Python on Windows.
