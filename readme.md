# GridWorld: Reinforcement Learning with Policy & Value Iteration

A simple, extensible GridWorld environment for experimenting with classic reinforcement learning algorithms — **Policy Iteration** and **Value Iteration** — featuring obstacles, portals, start/end states, and customizable rewards.

---

## Features

- Grid environment with customizable size, defined via a **menu-based GUI**  
- Obstacles (black) randomly placed to block agent movement  
- Traps (red) randomly placed with strong negative rewards  
- Rest areas (pink) randomly placed with neutral rewards  
- **Fixed two-way portals** in opposite corners (blue) for teleportation  
- Start and end states, with the end goal giving a high positive reward  
- Reward structure:  
  - Step penalty: **-1** per move  
  - Trap penalty: **-10**  
  - Neutral zones: **0**  
  - End goal: **+100**  
- Supports both **synchronous** and **asynchronous** Policy Iteration and Value Iteration  
- Policies are **deterministic** and displayed with **gradient arrows** indicating direction and intensity  
- Environment supports **stochastic or deterministic transition models**  
- Visualizations include:  
  - Numerical value function displayed **inside each grid cell**  
  - Dedicated **policy arrow gradient page**  
  - **Convergence graphs** generated automatically to track algorithm progress  

[![GridWorld Demo](https://img.youtube.com/vi/9Do_KB7WzRQ/0.jpg)](https://youtu.be/9Do_KB7WzRQ)


