# Etheria Simulation Suite

A comprehensive Etheria game data management and analysis system featuring unified database architecture, advanced HTML parsing, and multi-system GUI interfaces with visual elements.

## 🌟 Features

### 📊 Unified Database System
- **Integrated Database**: Unified SQLite database with EtheriaManager for cross-system data management
- **Multi-Entity Support**: Complete CRUD operations for Characters (20), Shells (20), and Matrix Effects (21)
- **Data Integrity**: Advanced referencing system with shell-matrix compatibility tracking (160 relationships)
- **Statistics Engine**: Comprehensive system metrics and usage analytics

### 🔍 Advanced HTML Parsing Suite
- **Multi-Parser System**: Specialized parsers for characters, shells, and matrix effects
- **Unified Parser**: Coordinated parsing with correct data order (Matrix → Shell → Character)
- **Data Validation**: Automatic integrity checking and format validation
- **Batch Processing**: Support for bulk data processing with progress tracking

### 🎮 Character System
- **Character Pokedex**: Advanced GUI with search, filtering, and detailed character information
- **Rich Data Display**: Stats, skills, dupes/prowess with tabbed interface
- **Advanced Filtering**: By rarity (SSR/SR/R) and element (Disorder/Reason/Hollow/Odd/Constant)
- **Complete Coverage**: 20 characters with full stats and skill descriptions

### 🛡️ Shell System with Visual Interface
- **Shell Pokedex**: Comprehensive shell browsing and management interface
- **Matrix Integration**: Advanced matrix filtering with ALL/ANY modes for effect combinations
- **Visual Enhancement**: 64x64 pixel shell images in Shell Details panel
- **Smart Filtering**: Class-based filtering (Striker/Supporter/Survivor/Healer) with matrix compatibility

### ⚙️ Matrix Effects System
- **Matrix Database**: 21 matrix effects with complete shell compatibility mapping
- **Visual Checkboxes**: 24x24 pixel matrix icons for intuitive selection
- **Usage Analytics**: Matrix popularity tracking across shells
- **Effect Categories**: Organized by source (Aurora/DokiDoki/Terrormaton)

### 🔧 Mathic Equipment System  
- **6-Slot Equipment System**: Support for 4 module types - Mask, Transistor, Wristwheel, Core
- **Attribute System**: Main stat + 4 substats with enhancement upgrade support
- **Loadout Management**: Complete 6-piece equipment configuration management
- **Enhancement Simulator**: Advanced enhancement prediction and optimization tools
- **Save System**: JSON format save and load functionality

### 🖼️ Visual Interface System
- **MVC Architecture**: Clean separation with Models, Views, and Controllers
- **Image Integration**: PIL/Pillow support for matrix and shell images
- **Responsive UI**: Adaptive layouts with proper grid weight configuration
- **Real-time Updates**: Live status updates and dynamic content refresh

## 📂 Project Structure

```text
etheria_sim/
├── setup.py                        # 📦 Installation setup
├── rt-sandbox/                     # 🐍 Python virtual environment
├── windowing/                      # 🖼️ MVC GUI Framework
│   ├── ui_mvc.py                   # 🚀 Main MVC application entry point
│   ├── models.py                   # 📊 Data models (Character/Shell/Mathic)
│   ├── views.py                    # 🎨 GUI views with image support
│   ├── controllers.py              # 🎮 Application controllers
│   └── ui.py                       # 🖥️ Legacy integrated interface
│
├── db/                             # 💾 Unified Database System
│   ├── etheria_manager.py          # 🔧 Main database manager
│   ├── character_manager.py        # 👤 Character data operations
│   ├── shell_manager.py            # 🛡️ Shell data operations
│   ├── matrix_manager.py           # ⚡ Matrix effects operations
│   └── db_routing.py               # 🔗 Database connection routing
│
├── html_parser/                    # 🔍 Advanced HTML Processing
│   ├── unified_parser.py           # 🎯 Coordinated parsing system
│   ├── parse_char.py               # 👤 Character data parsing
│   ├── parse_shells.py             # 🛡️ Shell data parsing
│   └── parse_matrix.py             # ⚡ Matrix effects parsing
│
├── img/                            # 🖼️ Visual Assets
│   ├── matrices/                   # ⚡ Matrix effect icons (21 x 24x24px)
│   └── shells/                     # 🛡️ Shell images (20 x 64x64px)
│
├── mathic/                         # ⚙️ Equipment System
│   ├── mathic_system.py            # 🔧 Core equipment logic
│   └── mathic_config.json          # ⚙️ System configuration
│
├── testing/                        # 🧪 Comprehensive Test Suite
│   ├── test_shell_images.py        # 🖼️ Shell image functionality tests
│   ├── demo_shell_images.py        # 🎭 Shell image demonstration
│   ├── testing_unified_database.py # 💾 Database integration tests
│   └── demo_unified_system.py      # 🎯 Complete system demonstration
│
├── cmd/                            # 🚀 Command Interface
│   └── launcher.py                 # 🎮 Main application launcher
│
├── tools/                          # 🛠️ Utility Tools
├── utils/                          # 🧰 Utility Modules
└── var/                            # 📁 Data Files
   └── *.html                       # 🌐 Source data files
```

## 🚀 Quick Start

### Prerequisites
```bash
# Ensure Python 3.8+ is installed
python3 --version

# Activate virtual environment
source ./rt-sandbox/bin/activate

# Install dependencies
pip install beautifulsoup4 lxml pillow
```

### Launch Options

#### 1. MVC Application (Recommended)
```bash
# Modern MVC architecture with full feature set
./rt-sandbox/bin/python windowing/ui_mvc.py
```
Features complete system with:
- Character Pokedex with advanced filtering
- Shell Pokedex with matrix filtering and images
- Mathic Equipment System
- Unified status updates and navigation

#### 2. Main Launcher
```bash
./rt-sandbox/bin/python ./cmd/launcher.py
```
Provides feature menu including:
- MVC Application launcher
- Individual system components
- HTML parsing tools
- System testing and demonstrations

#### 3. Direct System Components

**Character System:**
```bash
# Character Pokedex interface
./rt-sandbox/bin/python -c "
from windowing.models import CharacterModel
from windowing.views import CharacterListView
import tkinter as tk
# Creates character browsing interface
"
```

**Shell System:**
```bash
# Shell Pokedex with matrix filtering
./rt-sandbox/bin/python testing/demo_shell_images.py
```

**HTML Parsing:**
```bash
# Unified parsing system
./rt-sandbox/bin/python html_parser/unified_parser.py
```

## 📖 User Guide

### Character System Usage

1. **Browse Characters**: 
   - Use Character Pokedex for searching and filtering 20 characters
   - Filter by rarity (SSR/SR/R) and element types
   - View detailed stats, skills, and dupes information

2. **Database Operations**:
   - Automatic unified database management
   - Real-time character data updates
   - JSON import/export support

### Shell System Usage

1. **Shell Management**:
   - Browse 20 shells in Shell Pokedex interface
   - Filter by class (Striker/Supporter/Survivor/Healer) and rarity
   - View 64x64 pixel shell images in details panel

2. **Matrix Filtering**:
   - Visual matrix selection with 24x24 pixel icons
   - ALL mode: shells compatible with all selected matrices
   - ANY mode: shells compatible with any selected matrix
   - Real-time filtering updates

### Matrix Effects System

1. **Matrix Management**:
   - 21 matrix effects with complete shell compatibility
   - Visual icons for easy identification
   - Usage analytics and popularity tracking

2. **Shell Compatibility**:
   - 160 shell-matrix relationships tracked
   - Instant compatibility checking
   - Matrix recommendation system

### Unified Database Operations

1. **Data Parsing**:
   ```bash
   # Parse all data with correct order
   ./rt-sandbox/bin/activate
   python html_parser/unified_parser.py
   ```

2. **System Statistics**:
   ```python
   from db.etheria_manager import EtheriaManager
   manager = EtheriaManager()
   stats = manager.get_comprehensive_stats()
   # Returns complete system metrics
   ```

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

### MVC Application Navigation

The MVC application features integrated tabs:
- **Character Pokedex**: Character database browsing with advanced search
- **Shell Pokedex**: Shell management with matrix filtering and visual elements
- **Mathic System**: Equipment system with module editor and loadout manager
- **System Overview**: Real-time statistics and system health monitoring

## ⚙️ System Configuration

### Database Configuration

Current database contains:
- **Characters**: 20 (12 SSR, 7 SR, 1 R)
- **Shells**: 20 (7 Striker, 6 Supporter, 5 Survivor, 2 Healer)
- **Matrix Effects**: 21 (7 Aurora, 7 DokiDoki, 7 Terrormaton)
- **Shell-Matrix Relationships**: 160 compatibility mappings

### Visual Assets Configuration

- **Matrix Icons**: 21 x 24x24 pixel WEBP images in `./img/matrices/`
- **Shell Images**: 20 x 64x64 pixel WEBP images in `./img/shells/`
- **Image Caching**: PIL/Pillow integration with memory caching
- **File Naming**: Standardized format (`set_[name].webp`, `shell_[name].webp`)

### Mathic System Configuration (`mathic_config.json`)

- **Module Types**: Define main stat options and value limits for 4 module types
- **Substats**: Configure all possible substats and their value ranges  
- **Enhancement System**: Set enhancement limit and growth values
- **Slot Configuration**: Module type restrictions for 6 slots

### MVC Architecture Configuration

- **Models**: Unified data access layer with EtheriaManager integration
- **Views**: Component-based UI with image support and responsive layouts
- **Controllers**: Event handling and business logic coordination
- **App State**: Centralized state management with real-time updates

### Unified Database Schema

```sql
-- Core entities
characters (id, name, rarity, element, ...)
shells (id, name, rarity, class, cooldown, ...)
matrix_effects (id, name, source, effect_type, ...)

-- Relationship tables
shell_matrix_compatibility (shell_id, matrix_id)
character_stats (character_id, stat_name, base_value, ...)
shell_skills (shell_id, skill_type, description, ...)
```

## 🧪 Testing and Validation

### Running Tests
```bash
# Activate environment
source ./rt-sandbox/bin/activate

# Comprehensive system tests
python testing/testing_unified_database.py
python testing/test_shell_images.py
python testing/testing_shell_pokedex.py

# Visual demonstrations
python testing/demo_shell_images.py
python testing/demo_unified_system.py

# Mathic system tests
python testing/demo_mathic.py

# Or use launcher for organized testing
python ./cmd/launcher.py  # Select test options
```

### Test Coverage
- **Database Integration**: Unified database operations and cross-system compatibility
- **Image System**: Matrix and shell image loading, caching, and display
- **GUI Components**: MVC architecture validation and UI responsiveness
- **Shell-Matrix Filtering**: Advanced filtering logic with ALL/ANY modes
- **Data Parsing**: HTML parsing accuracy and data integrity validation
- **Enhancement System**: Module creation, enhancement, and loadout management
- **Visual Interface**: Image integration and responsive layout testing

### Validation Metrics
- **Database Coverage**: 100% entity coverage (Characters: 20/20, Shells: 20/20, Matrices: 21/21)
- **Image Coverage**: 100% visual asset coverage (Matrix icons: 21/21, Shell images: 20/20)
- **Shell-Matrix Compatibility**: 160 validated relationships with usage analytics
- **GUI Functionality**: Complete MVC pattern implementation with real-time updates
- **Performance**: Image caching reduces load times, responsive filtering under 100ms

## 📊 System Highlights

### Advanced Database Architecture
- **Unified Management**: Single EtheriaManager for all data operations
- **Cross-System Integration**: Character-Shell-Matrix relationship mapping
- **Performance Optimization**: Efficient querying with 160 pre-computed shell-matrix relationships
- **Data Integrity**: Automatic validation and referential integrity checking
- **Analytics Engine**: Real-time usage statistics and system metrics

### Visual Interface Innovation
- **Image Integration**: PIL/Pillow powered visual elements with memory caching
- **Responsive Design**: Adaptive layouts with proper weight distribution
- **Multi-Resolution Support**: 24x24 matrix icons and 64x64 shell images
- **Real-time Updates**: Live filtering and search with visual feedback
- **MVC Architecture**: Clean separation of concerns for maintainable code

### Shell-Matrix System Features
- **Advanced Filtering**: Dual-mode filtering (ALL/ANY) for complex matrix combinations
- **Visual Selection**: Image-enhanced checkboxes for intuitive matrix selection
- **Compatibility Engine**: Instant shell-matrix compatibility validation
- **Usage Analytics**: Matrix popularity tracking across all shells
- **Smart Recommendations**: Intelligent shell suggestions based on matrix selections

### Mathic Equipment System Features
- **Complete Attribute System**: 13 different attribute types with full customization
- **Smart Enhancement Mechanism**: Randomly select enhanceable substats with probability weighting
- **Efficiency Calculation**: Real-time display of substat efficiency percentage
- **Loadout Total Stats**: Automatically calculate total stat bonuses from 6 equipment pieces
- **Visual Interface**: Intuitive module editing and loadout management GUI with drag-drop simulation

### Data Processing Capabilities
- **Unified HTML Parsing**: Support for complex game data structure parsing with order validation
- **Data Validation**: Automatic data integrity and format checking with error reporting
- **Batch Processing**: Support for bulk character, shell, and matrix data processing
- **Search Optimization**: Efficient database queries with indexed searching
- **Cross-Reference Validation**: Automatic shell-matrix compatibility verification

## 🔧 Development Information

### Technology Stack
- **Python 3.8+**: Primary development language with modern async support
- **tkinter**: GUI framework with PIL/Pillow image integration
- **SQLite3**: Lightweight database with advanced relationship mapping
- **BeautifulSoup4**: HTML parsing with XPath and CSS selector support
- **PIL/Pillow**: Image processing for visual interface elements
- **JSON**: Configuration and data exchange format

### Architecture Design
- **MVC Pattern**: Complete Model-View-Controller separation with unified state management
- **Modular Design**: Independent and extensible systems with clear interfaces
- **Configuration-Driven**: JSON configuration files control system behavior
- **Data Abstraction**: Complete data access layer abstraction with EtheriaManager
- **UI/Logic Separation**: Clear separation of interface and business logic
- **Image Management**: Efficient caching and processing of visual assets

### Database Design Principles
- **Unified Schema**: Single database for all entities with proper foreign key relationships
- **Performance Optimization**: Indexed queries and pre-computed compatibility matrices
- **Data Integrity**: Comprehensive validation and referential integrity constraints
- **Scalability**: Designed for easy extension with new entity types
- **Analytics Support**: Built-in usage tracking and statistics generation

### Visual System Architecture
- **Image Caching**: Memory-efficient image loading with LRU cache implementation
- **Responsive Layouts**: Grid-based layouts with proper weight distribution
- **Component Reusability**: Modular UI components with consistent styling
- **Event-Driven Updates**: Real-time UI updates with efficient event propagation
- **Multi-Resolution Support**: Scalable image handling for different display contexts

## 📝 Changelog

### v2.0.0 - Advanced Visual System with Unified Database
- ✅ **Unified Database Architecture**: Complete EtheriaManager integration with cross-system data management
- ✅ **Shell Pokedex System**: Advanced shell browsing with matrix filtering and 64x64 pixel shell images
- ✅ **Matrix Effects Integration**: 21 matrix effects with 24x24 pixel icons and ALL/ANY filtering modes
- ✅ **Visual Interface Enhancement**: PIL/Pillow integration with memory caching for optimal performance
- ✅ **MVC Architecture Implementation**: Complete Model-View-Controller pattern with unified state management
- ✅ **Advanced HTML Parsing**: Unified parser system with correct data order validation (Matrix → Shell → Character)
- ✅ **Shell-Matrix Compatibility System**: 160 pre-computed relationships with usage analytics
- ✅ **Comprehensive Testing Suite**: Complete test coverage for database, UI, and image systems
- ✅ **Real-time Statistics Engine**: System-wide metrics and performance monitoring
- ✅ **Cross-System Integration**: Seamless data flow between Character, Shell, and Matrix systems

### v1.1.0 - Integrated Interface Update
- ✅ Integrated Character Pokedex and Mathic System into unified interface
- ✅ Top-level tab navigation between major systems
- ✅ Enhanced user experience with seamless system switching
- ✅ Updated launcher with integrated suite option
- ✅ Improved interface organization and usability

### v1.0.0 - Complete System Foundation
- ✅ HTML character data parsing system
- ✅ SQLite database complete CRUD operations
- ✅ Tkinter character pokedex GUI
- ✅ Mathic 6-slot equipment system
- ✅ Module enhancement and loadout management
- ✅ Complete UI interface
- ✅ Save/load functionality
- ✅ System testing and demonstration

## 🎮 Usage Examples

### Starting the MVC Application
```bash
# Launch modern MVC interface with full feature set
source ./rt-sandbox/bin/activate
python windowing/ui_mvc.py

# Or use the main launcher
python ./cmd/launcher.py
# Then select "1. MVC Application (Recommended)"
```

### Database Statistics and Analytics
```python
# Get comprehensive system statistics
from db.etheria_manager import EtheriaManager

manager = EtheriaManager()
stats = manager.get_comprehensive_stats()

print(f"Characters: {stats['database']['total_characters']}")
print(f"Shells: {stats['database']['total_shells']}")
print(f"Matrix Effects: {stats['database']['total_matrix_effects']}")
print(f"Shell-Matrix Relationships: {stats['database']['shell_matrix_relationships']}")

# Matrix usage analytics
matrix_usage = stats['matrix_usage_by_shells']
print(f"Most popular matrix: {max(matrix_usage, key=matrix_usage.get)}")
```

### Shell and Matrix Operations
```python
# Shell filtering with matrix compatibility
from windowing.models import ShellModel

shell_model = ShellModel()

# Get shells compatible with specific matrices
filtered_shells = shell_model.filter_shells_by_matrix(['Timeweave', 'Swiftrush'])
print(f"Shells compatible with Timeweave AND Swiftrush: {len(filtered_shells)}")

# Get shells compatible with any of the matrices
any_compatible = shell_model.filter_shells_by_matrix_any(['Bloodbath', 'Fury'])
print(f"Shells compatible with Bloodbath OR Fury: {len(any_compatible)}")

# Get all matrix effects
matrices = shell_model.get_all_matrix_effects()
print(f"Available matrix effects: {matrices}")
```

### Visual System Integration
```python
# Load and display shell images
from windowing.views import ShellListView
from PIL import Image
import tkinter as tk

root = tk.Tk()
shell_view = ShellListView(tk.Frame(root))

# Load shell image (automatically cached)
shell_image = shell_view._load_shell_image("Alicorn")
if shell_image:
    print("Successfully loaded 64x64 shell image")

# Load matrix icon (automatically cached)
matrix_image = shell_view._load_matrix_image("Timeweave")
if matrix_image:
    print("Successfully loaded 24x24 matrix icon")
```

### Key Features Available
- **Character Management**: Search, view, and manage 20 characters with complete stats and skills
- **Shell System**: Browse 20 shells with visual images and advanced matrix filtering
- **Matrix Integration**: 21 matrix effects with visual icons and compatibility tracking
- **Equipment System**: Create, enhance, and manage mathic modules with loadout optimization
- **Data Import/Export**: Handle character data and system configurations
- **Real-time Analytics**: System statistics and usage metrics
- **Visual Interface**: Image-enhanced UI with responsive layouts and real-time updates

### Advanced Usage Scenarios
```bash
# Parse new data files
python html_parser/unified_parser.py

# Run comprehensive system tests
python testing/testing_unified_database.py

# Launch visual shell system demonstration
python testing/demo_shell_images.py

# Test matrix icon functionality
python testing/test_shell_matrix_icons.py

# Generate system performance reports
python -c "
from db.etheria_manager import EtheriaManager
import json
manager = EtheriaManager()
stats = manager.get_comprehensive_stats()
print(json.dumps(stats, indent=2))
"
```

## 📄 License

This project is licensed under the MIT License.
