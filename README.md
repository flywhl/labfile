<div align="center">
  
  ![logo](https://github.com/user-attachments/assets/78c35cdc-74af-49da-8ea3-5f09d26a6b9c)
  
  **A declarative language for orchestrating computational experiments.**

  [Discord](https://discord.gg/kTkF2e69fH) • [Website](https://flywhl.dev) • [Installation](#installation)
</div>

*Labfile is in proof-of-concept stage.*


### Installation
`rye add labfile --git https://github.com/flywhl/labfile`

```python
  from pathlib import Path
  from labfile import parse
  

  labfile = Path("path/to/Labfile")
  tree = parse(labfile)
  ```

### Example
(Pseudocode, check `tests/parser/Labfile.test` for current syntax)

<p align="center">
  
  <img width="600" alt="image" src="https://github.com/user-attachments/assets/11ec6161-b8b5-4dd1-955f-87d1bb471e70">
</p>

### Development

* `git clone https://github.com/flywhl/labfile.git`
* `cd labfile`
* `rye sync`

### Contributing

Labfile is in early development. We will start accepting PRs soon once it has stabilised a little. However, please join the [discussions](https://github.com/flywhl/labfile/discussions), add [issues](https://github.com/flywhl/labfile/issues), and share your use-cases to help steer the design.

## Flywheel

Science needs better software tools. [Flywheel](https://flywhl.dev/) is an open source collective building (dev)tools to accelerate scientific momentum.
