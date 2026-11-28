# SPRITE//CITY — The Last Broadcast
Mission 000: original coastal analog-industrial miniature city. A small radio station reconnects fictional neighborhood relays. No real radio transmission or network access. Proposed aesthetic: alternate 1998, rain-dark streets, warm windows, CRT green, rust and sea fog.
## Warehouse experiment
Primary candidate: https://github.com/loktar00/sprite-stack-engine (README and MIT LICENSE inspected; README blob 497c0079235a0b4e9f2a52cc3d0e5d953504e4cd). Upstream WebGL2 renderer documents free camera, flat slices, voxel fallback and instrumentation. No upstream code or art has been copied or executed. Initial original Canvas2D slice-stack prototype isolates the visual/gameplay concept; it is NOT an integration of that engine. Next gate: pin upstream commit, inspect actual interfaces and asset rights, then build isolated WebGL2 adapter with attribution.
## Comparison protocol
Compare with NEON-DRIFT on same device/browser, viewport, DPR and duration. Record load bytes, median/p95 frame interval, scene density, controls, visual cohesion, development time and reuse evidence. Different gameplay and rendering workloads mean results are descriptive, not a controlled renderer benchmark. No claims of faster performance until measured.
## Run
Serve repository root over HTTP and open experiments/sprite-city/index.html. Drag to rotate, use buttons to restore fictional relays. Prototype is not deployed to live Pages. 
