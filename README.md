# up-ma-bfws  Unified Planning integrator

The aim of this project is to make the multi-agent BFWS [ma-bfws](https://dl.acm.org/doi/abs/10.1016/j.artint.2023.103883) ([bibtex](https://github.com/aiplan4eu/up-ma-bfws/blob/master/ma-bfws.bib))
planning engine available in the [unified_planning
library](https://github.com/aiplan4eu/unified-planning) by the
[AIPlan4EU project](https://www.aiplan4eu-project.eu/).


## Installation

We recommend the installation from PyPi because it has pre-built wheels for all common operating systems.

### Installation from Python Package Index PyPi

To automatically get a version that works with your version of the unified planning framework, you can list it as a solver in the pip installation of ```unified_planning```:

```
pip install unified-planning[ma-bfws]
```

If you need several solvers, you can list them all within the brackets.

You can also install the ma-BFWS integration separately (in case the current version of unified_planning does not include ma-BFWS or you want to add it later to your unified planning installation). After cloning this repository run

```pip install up-ma-bfws```

you get the latest version. 

This repository incudes the ma-BFWS binaries compiled for Linux. The installation has been tested in Ubuntu 20.04.3 LTS.

If you need an older version, you can install it with:

```
pip install up-ma-bfws==<version number>
```
## Usage

### Solving a planning problem

You can for example call it as follows:

```
from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus

problem = MultiAgentProblem('myproblem')
# specify the problem (e.g. fluents, initial state, actions, goal)
...

planner = OneshotPlanner(name="ma-bfws")
result = planner.solve(problem)
if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
    print(f'{Found a plan.\nThe plan is: {result.plan}')
else:
    print("No plan found.")
```

## Planning approaches of UP supported
Multi-agent planning

## ma-BFWS Team
Current members: Alfonso E. Gerevini, Nir Lipovetzky, Alessandro Saetti and Ivan Serina

Planning group coordinator: Alfonso E. Gerevini

Past PhD students: Andrea Bonisoli, Francesco Percassi
