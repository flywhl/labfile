<p align="center">
  <img src="https://github.com/user-attachments/assets/17fe0d37-489d-43e5-b54c-3b018212c1d1">
</p>
<p align="center">
  <b>A declarative language for orchestrating computational experiments.</b>
</p>
<br/>

## Note

*Labfile is in proof-of-concept stage.*

This repository is the *parser* for `Labfile`, to be used as a library for building more complex tools.

## Example
(Pseudocode, check `tests/parser/Labfile.test` for current syntax)

<p align="center">
  
  <img width="600" alt="image" src="https://github.com/user-attachments/assets/11ec6161-b8b5-4dd1-955f-87d1bb471e70">
</p>


## Installation and usage

* `rye add labfile --git https://github.com/flywhl/labfile`
* ```python
  from pathlib import Path
  from labfile import parse
  

  labfile = Path("path/to/Labfile")
  tree = parse(labfile)
  ```

## Development

* `git clone https://github.com/flywhl/labfile.git`
* `cd labfile`
* `rye sync`

## Contributing

Labfile is in early development. We will start accepting PRs soon once it has stabilised a little. However, please join the [discussions](https://github.com/flywhl/labfile/discussions), add [issues](https://github.com/flywhl/labfile/issues), and share your use-cases to help steer the design.

## Flywheel

Science needs better software tools. [Flywheel](https://flywhl.dev/) is an open source collective building (dev)tools to accelerate scientific momentum.
