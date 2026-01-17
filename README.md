# Episema

A Python library for rendering Gregorian Chant in square note notation.

**Episema** is a Python twin of the [exsurge](https://github.com/frmatthew/exsurge) JavaScript library, designed to parse and render Gregorian chant notation.

## Installation

```bash
pip install episema
```

## Features

- Parse GABC (Gregorio) notation
- Render Gregorian chant in square note notation
- Support for various chant elements (neumes, clefs, lyrics, etc.)
- Extensible architecture for custom rendering

## Architecture

![Architecture Diagram](assets/architecture_diagram.png)

## Usage

```python
from episema import ChantScore

# Create a chant score from GABC notation
gabc = "c4 c(e) d(f) e(g)"
score = ChantScore.from_gabc(gabc)

# Render to SVG
svg_output = score.render()
```

## Development

This project uses [Poetry](https://python-poetry.org/) for dependency management.

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Gabrieljoseg/episema.git
cd episema

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## License

MIT License - See LICENSE file for details

## Credits

Inspired by [exsurge](https://github.com/frmatthew/exsurge) by Fr. Matthew Spencer, O.S.J.

## Keywords

gregorian, chant, square note, solesmes, gabc, liturgy, music notation
