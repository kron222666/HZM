# HZM - Hierarchical Zero Mathematics

**HZM** (Hierarchical Zero Mathematics) is a new mathematical system that allows correct and safe handling of division by zero without raising errors, exceptions, or producing NaN values.

Instead of forbidding division by zero, HZM transforms it into a **controlled hierarchical process** using depth levels \(k\).

## Core Idea

- Regular real numbers remain unchanged.
- When a singularity occurs (division by zero, vanishing gradients, etc.), the result becomes either a **deep zero \(0_k\)** or a **hierarchical infinity \(∞_k\)**.
- The level \(k\) quantitatively represents the **depth of the singularity** — how severe the problem is.
- All arithmetic operations remain well-defined and closed.

## Features

- Full support for all arithmetic operations with hierarchical zeros and infinities
- Automatic level deepening when singularities appear
- Projection onto machine floating-point numbers (IEEE 754) for compatibility
- Support for vector and matrix operations
- Built-in logging of level \(k\) for debugging and analysis

## Applications

- **Machine Learning** — stable gradient descent, handling vanishing and exploding gradients
- **Physics Simulation** — modeling singularities in black holes and other gravitational phenomena
- **Safety-Critical Programming** — fault-tolerant real-time systems
- **Financial Mathematics** — modeling crises and risk assessment
  
### The library is under active development. Changes are possible.
### This project was completed as part of a research project in mathematics called "Algebra of Zeros".
## Installation

```bash
pip install hzm
