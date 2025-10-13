# Etheria Simulation Suite

A comprehensive Etheria game data management and analysis system featuring character data parsing, database management, pokedex interface, and Mathic equipment system.

## 🌟 Features

### 📚 Character System
- **HTML Parsing**: Parse character data from Plume.html and other files using BeautifulSoup
- **Database Storage**: Complete CRUD operations with SQLite database
- **Pokedex Interface**: Tkinter GUI for character search, browsing, and detailed information display

### 🔧 Mathic Equipment System  
- **6-Slot Equipment System**: Support for 4 module types - Mask, Transistor, Wristwheel, Core
- **Attribute System**: Main stat + 4 substats with enhancement upgrade support
- **Loadout Management**: Complete 6-piece equipment configuration management
- **UI Interface**: Dedicated module editor and loadout manager interfaces
- **Save System**: JSON format save and load functionality

## 📂 Project Structure

```
etheria_sim/
├── setup.py                   # 📦 Installation setup
├── rt-sandbox/                # 🐍 Python virtual environment
├── cmd/                       # command
│   └── launcher.py            # 🚀 Main launcher
│
├── html_parser/               # 🔍 HTML parser
│   └── parse_char.py          # Character data parsing
│
├── db/                        # 💾 Database system
│   └── db_routing.py          # SQLite operations class
│
├── windowing/                 # 🖼️ GUI interface
│   └── ui.py                  # Integrated main interface (Character Pokedex + Mathic System)
│
├── mathic/                    # ⚙️ Mathic equipment system
│   ├── mathic_config.json     # System configuration
│   ├── mathic_system.py       # Core system class
│
├── tests/                     # 🧪 Test files
├── testing/                   # 🧪 Test files
│   ├── testing_mathic.py      # System tests
│   └── demo_mathic.py         # Feature demonstration
│
├── utils/                     # 🛠️ Utility modules
└── var/                       # 📁 Data files
    └── Plume.html             # Character data source
```

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure Python 3.8+ is installed
python3 --version

# Activate virtual environment
source ./rt-sandbox/bin/activate

# Install dependencies (if needed)
pip install beautifulsoup4 lxml
```

### Launch Options

#### 1. Main Launcher (Recommended)
```bash
./rt-sandbox/bin/python ./cmd/launcher.py
```
Provides complete feature menu including:
- Integrated Suite (Character Pokedex + Mathic System)
- Standalone Mathic System
- HTML parsing functionality
- System tests and demonstrations

#### 2. Direct System Launch

**Integrated Suite (Character Pokedex + Mathic System):**
```bash
./rt-sandbox/bin/python windowing/ui.py
```

**Standalone Mathic Equipment System:**
```bash
./rt-sandbox/bin/python mathic/mathic_main.py
```

**HTML Parsing:**
```bash
./rt-sandbox/bin/python html_parser/parse_char.py
```

## 📖 User Guide

### Character System Usage

1. **Parse Character Data**: 
   - Place HTML files in the `./var/` directory
   - Run parser to extract character information

2. **Database Operations**:
   - Automatically creates SQLite database
   - Support for character data CRUD operations
   - JSON import/export functionality

3. **Pokedex Browsing**:
   - Search and filter characters
   - Detailed information display (base stats, skills, breakthrough effects)
   - Tabbed interface navigation

### Mathic System Usage

1. **Module Creation**:
   ```python
   # Create different types of modules
   mask = system.create_module("mask", 1, "ATK")
   transistor = system.create_module("transistor", 2, "HP")
   ```

2. **Module Enhancement**:
   ```python
   # Randomly enhance substats
   enhanced_stat = system.enhance_module_random_substat(module)
   ```

3. **Loadout Management**:
   ```python
   # Create loadout
   loadout = system.create_mathic_loadout("My Loadout")
   
   # Equip modules
   system.assign_module_to_loadout("My Loadout", slot_id, module_id)
   ```

### Interface Navigation

The integrated suite features two main tabs:
- **Character Pokedex**: Character database management and browsing
- **Mathic System**: Equipment system with module editor, loadout manager, and system overview

## ⚙️ System Configuration

### Mathic System Configuration (`mathic_config.json`)

- **Module Types**: Define main stat options and value limits for 4 module types
- **Substats**: Configure all possible substats and their value ranges  
- **Enhancement System**: Set enhancement limit and growth values
- **Slot Configuration**: Module type restrictions for 6 slots

### Database Structure

- **characters**: Character basic information table
- **character_stats**: Character stats table (foreign key relation)
- **character_skills**: Skills information table
- **character_dupes**: Breakthrough effects table

## 🧪 Testing and Validation

### Running Tests
```bash
# Mathic system comprehensive test
./rt-sandbox/bin/python testing/testing_mathic.py

# Mathic system feature demonstration
./rt-sandbox/bin/python testing/demo_mathic.py

# Or use launcher test options
./rt-sandbox/bin/python ./cmd/launcher.py  # Select 5. Run System Tests
```

### Test Coverage
- Module creation and attribute validation
- Enhancement system operations
- Loadout management functionality
- Save/load system
- Database CRUD operations
- GUI component functionality

## 📊 System Highlights

### Mathic Equipment System Features
- **Complete Attribute System**: 13 different attribute types
- **Smart Enhancement Mechanism**: Randomly select enhanceable substats
- **Efficiency Calculation**: Real-time display of substat efficiency percentage
- **Loadout Total Stats**: Automatically calculate total stat bonuses from 6 equipment pieces
- **Visual Interface**: Intuitive module editing and loadout management GUI

### Data Processing Capabilities
- **HTML Parsing**: Support for complex game data structure parsing
- **Data Validation**: Automatic data integrity and format checking
- **Batch Processing**: Support for bulk character data processing
- **Search Optimization**: Efficient database queries and indexing

### Interface Design
- **Integrated Tabs**: Top-level navigation between Character Pokedex and Mathic System
- **Real-time Updates**: Live status updates and system information
- **Sample Data**: Auto-generation of sample modules and loadouts for demonstration
- **Cross-system Integration**: Seamless operation between character and equipment management

## 🔧 Development Information

### Technology Stack
- **Python 3.8+**: Primary development language
- **tkinter**: GUI framework
- **SQLite3**: Lightweight database
- **BeautifulSoup4**: HTML parsing
- **JSON**: Configuration and data exchange format

### Architecture Design
- **Modular Design**: Independent and extensible systems
- **Configuration-Driven**: JSON configuration files control system behavior
- **Data Abstraction**: Complete data access layer abstraction
- **UI/Logic Separation**: Clear separation of interface and business logic
- **Integrated Interface**: Top-level tab navigation for unified user experience

## 📝 Changelog

### v1.1.0 - Integrated Interface Update
- ✅ Integrated Character Pokedex and Mathic System into unified interface
- ✅ Top-level tab navigation between major systems
- ✅ Enhanced user experience with seamless system switching
- ✅ Updated launcher with integrated suite option
- ✅ Improved interface organization and usability

### v1.0.0 - Complete System
- ✅ HTML character data parsing system
- ✅ SQLite database complete CRUD operations
- ✅ Tkinter character pokedex GUI
- ✅ Mathic 6-slot equipment system
- ✅ Module enhancement and loadout management
- ✅ Complete UI interface
- ✅ Save/load functionality
- ✅ System testing and demonstration

## 🎮 Usage Examples

### Starting the Integrated Suite
```bash
# Launch integrated interface
./rt-sandbox/bin/python windowing/ui.py

# Or use the main launcher
./rt-sandbox/bin/python ./cmd/launcher.py
# Then select "1. Integrated Suite (Character Pokedex + Mathic System)"
```

### Key Features Available
- **Character Management**: Search, view, and manage character data
- **Equipment System**: Create, enhance, and manage mathic modules
- **Loadout Configuration**: Build and optimize 6-slot equipment setups
- **Data Import/Export**: Handle character data and system configurations

## 📄 License

This project is licensed under the MIT License.
