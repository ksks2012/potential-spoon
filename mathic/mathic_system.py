import json
import random
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from copy import deepcopy


@dataclass
class Substat:
    """Represents a substat on a module"""
    stat_name: str
    current_value: float
    rolls_used: int = 0
    max_rolls: int = 5
    
    def can_enhance(self) -> bool:
        """Check if this substat can be enhanced further"""
        return self.rolls_used < self.max_rolls
    
    def enhance(self, roll_value: float) -> bool:
        """Enhance this substat with a roll value"""
        if not self.can_enhance():
            return False
        
        self.current_value += roll_value
        self.rolls_used += 1
        return True
    
    def get_efficiency_percentage(self, max_possible_value: float) -> float:
        """Calculate the efficiency percentage of this substat"""
        if max_possible_value == 0:
            return 0.0
        return (self.current_value / max_possible_value) * 100


@dataclass
class Module:
    """Represents a single mathic module"""
    module_id: str
    module_type: str  # mask, transistor, wristwheel, core
    slot_position: int
    level: int = 0
    main_stat: str = ""
    main_stat_value: float = 0.0
    substats: List[Substat] = None
    set_tag: str = ""  # For future set effects
    
    def __post_init__(self):
        if self.substats is None:
            self.substats = []
    
    def add_substat(self, stat_name: str, initial_value: float) -> bool:
        """Add a new substat to this module"""
        if len(self.substats) >= 4:
            return False
        
        # Check if this stat already exists
        for substat in self.substats:
            if substat.stat_name == stat_name:
                return False
        
        self.substats.append(Substat(stat_name, initial_value))
        return True
    
    def enhance_substat(self, stat_name: str, roll_value: float) -> bool:
        """Enhance a specific substat"""
        for substat in self.substats:
            if substat.stat_name == stat_name:
                return substat.enhance(roll_value)
        return False
    
    def get_substat(self, stat_name: str) -> Optional[Substat]:
        """Get a specific substat"""
        for substat in self.substats:
            if substat.stat_name == stat_name:
                return substat
        return None
    
    def calculate_total_stats(self) -> Dict[str, float]:
        """Calculate total stats including main stat and substats"""
        stats = {self.main_stat: self.main_stat_value}
        
        for substat in self.substats:
            if substat.stat_name in stats:
                stats[substat.stat_name] += substat.current_value
            else:
                stats[substat.stat_name] = substat.current_value
        
        return stats


class MathicSystem:
    """Main system for managing mathic modules"""
    
    def __init__(self, config_path: str = None):
        """Initialize the mathic system with configuration"""
        if config_path is None:
            # Get absolute path to the mathic directory
            mathic_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(mathic_dir, "mathic_config.json")
        
        self.config_path = config_path
        self.config = self.load_config()
        self.modules = {}  # module_id -> Module
        self.mathic_loadouts = {}  # loadout_name -> Dict[slot_id, module_id]
    
    def load_config(self) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Invalid JSON in config file: {e}")
            return {}
    
    def create_module(self, module_type: str, slot_position: int, 
                     main_stat: str = None, set_tag: str = "") -> Optional[Module]:
        """Create a new module"""
        if module_type not in self.config.get("module_types", {}):
            print(f"Invalid module type: {module_type}")
            return None
        
        module_config = self.config["module_types"][module_type]
        
        # Auto-select main stat if not provided
        if main_stat is None:
            main_stat_options = module_config["main_stat_options"]
            if len(main_stat_options) == 1:
                main_stat = main_stat_options[0]
            else:
                print(f"Please specify main stat for {module_type}. Options: {main_stat_options}")
                return None
        
        # Validate main stat
        if main_stat not in module_config["main_stat_options"]:
            print(f"Invalid main stat {main_stat} for {module_type}")
            return None
        
        # Generate unique module ID
        module_id = f"{module_type}_{slot_position}_{len(self.modules)}"
        
        # Get max main stat value
        max_main_stat_value = module_config["max_main_stats"][main_stat]
        
        module = Module(
            module_id=module_id,
            module_type=module_type,
            slot_position=slot_position,
            level=0,
            main_stat=main_stat,
            main_stat_value=max_main_stat_value,
            set_tag=set_tag
        )
        
        self.modules[module_id] = module
        return module
    
    def generate_random_substats(self, module: Module, count: int = 4) -> bool:
        """Generate random substats for a module"""
        if not module:
            return False
        
        available_stats = list(self.config.get("substats", {}).keys())
        
        # Remove main stat from available substats
        if module.main_stat in available_stats:
            available_stats.remove(module.main_stat)
        
        # Remove percentage version if flat version is main stat (and vice versa)
        main_stat_base = module.main_stat.replace('%', '')
        for stat in available_stats[:]:
            stat_base = stat.replace('%', '')
            if stat_base == main_stat_base and stat != module.main_stat:
                available_stats.remove(stat)
        
        if len(available_stats) < count:
            print(f"Not enough available substats for module {module.module_id}")
            return False
        
        # Randomly select substats
        selected_stats = random.sample(available_stats, count)
        
        for stat_name in selected_stats:
            stat_config = self.config["substats"][stat_name]
            roll_range = stat_config["roll_range"]
            initial_value = random.randint(roll_range[0], roll_range[1])
            
            module.add_substat(stat_name, float(initial_value))
        
        return True
    
    def enhance_module_random_substat(self, module: Module) -> Optional[str]:
        """Randomly enhance one substat of a module"""
        if not module or not module.substats:
            return None
        
        # Get substats that can be enhanced
        enhanceable_substats = [s for s in module.substats if s.can_enhance()]
        
        if not enhanceable_substats:
            return None
        
        # Randomly select a substat to enhance
        selected_substat = random.choice(enhanceable_substats)
        
        # Get roll value
        stat_config = self.config["substats"][selected_substat.stat_name]
        roll_range = stat_config["roll_range"]
        roll_value = random.randint(roll_range[0], roll_range[1])
        
        # Enhance the substat
        success = selected_substat.enhance(float(roll_value))
        
        if success:
            module.level += 1
            return selected_substat.stat_name
        
        return None
    
    def create_mathic_loadout(self, loadout_name: str) -> Dict[int, Optional[str]]:
        """Create a new mathic loadout with 6 slots"""
        loadout = {}
        for slot_info in self.config.get("mathic_slots", []):
            slot_id = slot_info["slot_id"]
            loadout[slot_id] = None
        
        self.mathic_loadouts[loadout_name] = loadout
        return loadout
    
    def assign_module_to_loadout(self, loadout_name: str, slot_id: int, module_id: str) -> bool:
        """Assign a module to a specific slot in a loadout"""
        if loadout_name not in self.mathic_loadouts:
            print(f"Loadout '{loadout_name}' not found")
            return False
        
        if module_id not in self.modules:
            print(f"Module '{module_id}' not found")
            return False
        
        # Check if slot is valid
        slot_info = None
        for slot in self.config.get("mathic_slots", []):
            if slot["slot_id"] == slot_id:
                slot_info = slot
                break
        
        if not slot_info:
            print(f"Invalid slot ID: {slot_id}")
            return False
        
        # Check if module type is allowed in this slot
        module = self.modules[module_id]
        if module.module_type not in slot_info["allowed_types"]:
            print(f"Module type '{module.module_type}' not allowed in slot {slot_id}")
            return False
        
        self.mathic_loadouts[loadout_name][slot_id] = module_id
        return True
    
    def calculate_loadout_stats(self, loadout_name: str) -> Dict[str, float]:
        """Calculate total stats for a mathic loadout"""
        if loadout_name not in self.mathic_loadouts:
            return {}
        
        total_stats = {}
        loadout = self.mathic_loadouts[loadout_name]
        
        for slot_id, module_id in loadout.items():
            if module_id and module_id in self.modules:
                module_stats = self.modules[module_id].calculate_total_stats()
                
                for stat_name, value in module_stats.items():
                    if stat_name in total_stats:
                        total_stats[stat_name] += value
                    else:
                        total_stats[stat_name] = value
        
        return total_stats
    
    def get_loadout_modules(self, loadout_name: str) -> Dict[int, Optional[Module]]:
        """Get all modules in a loadout"""
        if loadout_name not in self.mathic_loadouts:
            return {}
        
        result = {}
        loadout = self.mathic_loadouts[loadout_name]
        
        for slot_id, module_id in loadout.items():
            if module_id and module_id in self.modules:
                result[slot_id] = self.modules[module_id]
            else:
                result[slot_id] = None
        
        return result
    
    def remove_module_from_loadout(self, loadout_name: str, slot_id: int) -> bool:
        """Remove a module from a loadout slot"""
        if loadout_name not in self.mathic_loadouts:
            return False
        
        if slot_id in self.mathic_loadouts[loadout_name]:
            self.mathic_loadouts[loadout_name][slot_id] = None
            return True
        
        return False
    
    def delete_module(self, module_id: str) -> bool:
        """Delete a module completely"""
        if module_id not in self.modules:
            return False
        
        # Remove from all loadouts first
        for loadout_name, loadout in self.mathic_loadouts.items():
            for slot_id, assigned_module_id in loadout.items():
                if assigned_module_id == module_id:
                    loadout[slot_id] = None
        
        # Remove from modules
        del self.modules[module_id]
        return True
    
    def export_loadout_to_dict(self, loadout_name: str) -> Dict:
        """Export a loadout to a dictionary for saving/loading"""
        if loadout_name not in self.mathic_loadouts:
            return {}
        
        loadout_data = {
            "name": loadout_name,
            "slots": {},
            "total_stats": self.calculate_loadout_stats(loadout_name)
        }
        
        for slot_id, module_id in self.mathic_loadouts[loadout_name].items():
            if module_id and module_id in self.modules:
                module = self.modules[module_id]
                loadout_data["slots"][slot_id] = {
                    "module_id": module_id,
                    "module_type": module.module_type,
                    "level": module.level,
                    "main_stat": module.main_stat,
                    "main_stat_value": module.main_stat_value,
                    "substats": [asdict(substat) for substat in module.substats],
                    "set_tag": module.set_tag
                }
            else:
                loadout_data["slots"][slot_id] = None
        
        return loadout_data
    
    def save_to_file(self, filename: str) -> bool:
        """Save all modules and loadouts to a JSON file"""
        try:
            data = {
                "modules": {},
                "loadouts": {}
            }
            
            # Save modules
            for module_id, module in self.modules.items():
                data["modules"][module_id] = {
                    "module_id": module.module_id,
                    "module_type": module.module_type,
                    "slot_position": module.slot_position,
                    "level": module.level,
                    "main_stat": module.main_stat,
                    "main_stat_value": module.main_stat_value,
                    "substats": [asdict(substat) for substat in module.substats],
                    "set_tag": module.set_tag
                }
            
            # Save loadouts
            for loadout_name in self.mathic_loadouts:
                data["loadouts"][loadout_name] = self.export_loadout_to_dict(loadout_name)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False
    
    def load_from_file(self, filename: str) -> bool:
        """Load modules and loadouts from a JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load modules
            self.modules = {}
            for module_id, module_data in data.get("modules", {}).items():
                module = Module(
                    module_id=module_data["module_id"],
                    module_type=module_data["module_type"],
                    slot_position=module_data["slot_position"],
                    level=module_data["level"],
                    main_stat=module_data["main_stat"],
                    main_stat_value=module_data["main_stat_value"],
                    set_tag=module_data.get("set_tag", "")
                )
                
                # Load substats
                for substat_data in module_data.get("substats", []):
                    substat = Substat(
                        stat_name=substat_data["stat_name"],
                        current_value=substat_data["current_value"],
                        rolls_used=substat_data["rolls_used"],
                        max_rolls=substat_data["max_rolls"]
                    )
                    module.substats.append(substat)
                
                self.modules[module_id] = module
            
            # Load loadouts
            self.mathic_loadouts = {}
            for loadout_name, loadout_data in data.get("loadouts", {}).items():
                self.mathic_loadouts[loadout_name] = {}
                
                for slot_id_str, module_data in loadout_data.get("slots", {}).items():
                    slot_id = int(slot_id_str)
                    if module_data:
                        self.mathic_loadouts[loadout_name][slot_id] = module_data["module_id"]
                    else:
                        self.mathic_loadouts[loadout_name][slot_id] = None
            
            return True
            
        except Exception as e:
            print(f"Error loading from file: {e}")
            return False


def main():
    """Test the mathic system"""
    mathic = MathicSystem()
    
    print("="*60)
    print("MATHIC SYSTEM TEST")
    print("="*60)
    
    # Create a test loadout
    loadout_name = "Test Loadout"
    mathic.create_mathic_loadout(loadout_name)
    
    # Create modules for each slot
    print("\nCreating modules...")
    
    # Slot 1: Mask (ATK main stat)
    mask = mathic.create_module("mask", 1, "ATK")
    if mask:
        mathic.generate_random_substats(mask, 4)
        mathic.assign_module_to_loadout(loadout_name, 1, mask.module_id)
        print(f"Created Mask: {mask.module_id}")
    
    # Slot 2: Transistor (HP main stat)
    transistor = mathic.create_module("transistor", 2, "HP")
    if transistor:
        mathic.generate_random_substats(transistor, 4)
        mathic.assign_module_to_loadout(loadout_name, 2, transistor.module_id)
        print(f"Created Transistor: {transistor.module_id}")
    
    # Slot 3: Wristwheel (DEF main stat)
    wristwheel = mathic.create_module("wristwheel", 3, "DEF")
    if wristwheel:
        mathic.generate_random_substats(wristwheel, 4)
        mathic.assign_module_to_loadout(loadout_name, 3, wristwheel.module_id)
        print(f"Created Wristwheel: {wristwheel.module_id}")
    
    # Slots 4-6: Cores with different main stats
    core_main_stats = ["CRIT Rate", "CRIT DMG", "ATK%"]
    for i, main_stat in enumerate(core_main_stats):
        slot_id = 4 + i
        core = mathic.create_module("core", slot_id, main_stat)
        if core:
            mathic.generate_random_substats(core, 4)
            mathic.assign_module_to_loadout(loadout_name, slot_id, core.module_id)
            print(f"Created Core {i+1}: {core.module_id} (Main: {main_stat})")
    
    # Enhance some modules
    print("\nEnhancing modules...")
    for module in mathic.modules.values():
        for _ in range(random.randint(1, 3)):  # Random 1-3 enhancements
            enhanced_stat = mathic.enhance_module_random_substat(module)
            if enhanced_stat:
                print(f"Enhanced {module.module_id} - {enhanced_stat} (Level: {module.level})")
    
    # Display loadout stats
    print("\n" + "="*60)
    print("LOADOUT SUMMARY")
    print("="*60)
    
    total_stats = mathic.calculate_loadout_stats(loadout_name)
    for stat_name, value in sorted(total_stats.items()):
        if "%" in stat_name:
            print(f"{stat_name}: {value:.1f}%")
        else:
            print(f"{stat_name}: {value:.0f}")
    
    # Display individual modules
    print("\n" + "="*60)
    print("MODULE DETAILS")
    print("="*60)
    
    loadout_modules = mathic.get_loadout_modules(loadout_name)
    for slot_id in sorted(loadout_modules.keys()):
        module = loadout_modules[slot_id]
        if module:
            print(f"\nSlot {slot_id}: {module.module_type.upper()} (Level {module.level})")
            print(f"  Main Stat: {module.main_stat} = {module.main_stat_value}")
            print(f"  Substats:")
            for substat in module.substats:
                efficiency = substat.get_efficiency_percentage(
                    mathic.config["substats"][substat.stat_name]["max_value"]
                )
                print(f"    {substat.stat_name}: {substat.current_value:.1f} "
                      f"({substat.rolls_used}/{substat.max_rolls} rolls, {efficiency:.1f}% eff)")
    
    # Test save/load
    print(f"\nSaving mathic data...")
    save_path = "./mathic/test_mathic_data.json"
    if mathic.save_to_file(save_path):
        print(f"Saved to {save_path}")
    else:
        print("Save failed")


if __name__ == "__main__":
    main()
