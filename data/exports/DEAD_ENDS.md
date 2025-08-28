# Kryptos K4 — Eliminated or De-prioritized Methods

This file documents approaches that have been tested and ruled out, so future contributors do not repeat work.

## Eliminated
1. **Direct Berlin Clock lamp-count → shift mappings (linear or piecewise)**  
   *Fails to satisfy all 24 shift constraints simultaneously.*

2. **Simple tableau pointer walks using the extra 'L' row**  
   *Do not reproduce the observed 27-cycle or preserve island indices.*

3. **Repeating keystream periods 2–26**  
   *Conflict with island-implied keystream residues.*

4. **Simple columnar transposition (all factors of 97/98)**
   *Grids of size `W x H` where `W*H` is 97 or 98. Reading columns in order `0, 1, 2, ...` conflicts with island constraints for all dimensions.*

5. **Keyed columnar transposition (common keywords)**
   *Using keywords KRYPTOS, PALIMPSEST, BERLIN, CLOCK, etc. to define column order. All tested keywords resulted in island constraint conflicts.*

## De-prioritized
- **Period 28/29 repeating keystreams**: compatible with constraints, but weaker motivation and lower scores than period 27.

---
*Keep this file updated as additional approaches are tested and eliminated.*
