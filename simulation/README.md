# 2D Top-Down Life Survival Simulation

A complex simulation featuring autonomous AI-driven characters, emergent behavior, and a fully simulated world with dynamic ecosystems and social interactions.

## Features

- Fully simulated AI-driven Characters with emergent autonomy
  - Individual memories and personality quirks
  - Dynamic daily schedules
  - Autonomous decision making
  - Skill development and learning
  - Social interactions and relationships

- Custom Calendar System
  - 10-day weeks
  - 300-day years (10 months)
  - Day periods: Firstlight, Highsun, Duskbloom, Starveil
  - Months: Brigide, Imbolka, Floralis, Lithara, Heliax, Aestium, Mabonel, Ceresio, Yulith, Hibernis

- Advanced Character Abilities
  - Resource gathering (mining, chopping, farming)
  - Combat and defense
  - Crafting and construction
  - Social interactions
  - Trading and economics
  - Teaching and learning
  - Family formation

- Deep Crafting System
  - Natural resources
  - Basic tools and items
  - Advanced equipment
  - Magical items

- Procedural World Generation
  - Diverse biomes
  - Resource distribution
  - Dynamic ecosystems
  - Weather systems

- Complex Job System
  - Construction & Infrastructure
  - Farming & Resource Gathering
  - Crafting & Production
  - Food & Drink
  - Defense & Warfare
  - Trade & Communication
  - Medicine & Magic
  - Arts & Culture
  - Exploration & Defense

## Requirements

- Python 3.8+
- Required packages:
  - pygame: Graphics and game engine
  - numpy: Numerical computations
  - networkx: Relationship graphs
  - namemaker: Character name generation
  - pyyaml: Configuration management
  - Pillow: Image processing

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Simulation

```bash
python -m simulation
```

## Project Structure

```
simulation/
├── assets/           # Game assets
│   ├── sprites/     # Character and object sprites
│   ├── fonts/       # Text fonts
│   └── sounds/      # Sound effects
├── config/          # Configuration files
├── data/            # Runtime data
├── engine/          # Core systems
│   ├── ai_system.py        # AI behavior
│   ├── config.py          # Configuration
│   ├── entity.py          # Entity management
│   ├── entity_manager.py  # Entity coordination
│   ├── game.py            # Main game loop
│   ├── job_system.py      # Jobs and work
│   ├── resource_manager.py # Resources
│   ├── time_system.py     # Time management
│   ├── utils.py           # Utilities
│   └── world.py           # World generation
├── logs/            # Log files
└── README.md        # Documentation
```

## Core Systems

### World Generation
- Procedural terrain generation
- Biome distribution
- Resource placement
- Climate and weather systems

### Entity System
- Character creation and management
- DNA-based genetics
- Stat and skill tracking
- Inventory management

### AI System
- Autonomous decision making
- Memory and personality
- Social interactions
- Goal planning and execution

### Job System
- Professional roles
- Task assignment
- Skill development
- Economic impact

### Resource System
- Resource gathering
- Crafting recipes
- Item creation
- Resource regeneration

### Time System
- Custom calendar
- Day/night cycle
- Weather progression
- Event scheduling

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to all contributors and testers
- Special thanks to the Python game development community
