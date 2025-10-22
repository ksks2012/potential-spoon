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
    matrix: str = ""  # Matrix type (e.g., "Brainfoam", "Evolguard")
    matrix_count: int = 3  # Number of matrices (1-3, default 3)
    total_enhancement_rolls: int = 0  # Track total rolls across all substats
    max_total_rolls: int = 5  # Maximum total rolls for the entire module
    
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
    
    def can_be_enhanced(self) -> bool:
        """Check if this module can be enhanced further (total rolls limit)"""
        return self.total_enhancement_rolls < self.max_total_rolls
    
    def get_enhanceable_substats(self) -> List[Substat]:
        """Get substats that can be enhanced based on module's total roll limit"""
        if not self.can_be_enhanced():
            return []
        return [s for s in self.substats if s.can_enhance()]
    
    def enhance_substat_with_roll_tracking(self, stat_name: str, roll_value: float) -> bool:
        """Enhance a specific substat with roll tracking"""
        if not self.can_be_enhanced():
            return False
            
        for substat in self.substats:
            if substat.stat_name == stat_name:
                success = substat.enhance(roll_value)
                if success:
                    self.total_enhancement_rolls += 1
                    self.level += 1
                return success
        return False
    
    def sync_enhancement_tracking(self):
        """Synchronize total_enhancement_rolls and level based on actual substat rolls used"""
        # Calculate actual enhancement operations based on substat rolls
        # Each roll on any substat counts as one enhancement operation
        actual_enhancement_operations = sum(substat.rolls_used for substat in self.substats)
        
        # Cap at max_total_rolls to maintain game balance
        self.total_enhancement_rolls = min(actual_enhancement_operations, self.max_total_rolls)
        self.level = self.total_enhancement_rolls
    
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
    
    def __init__(self, config_path: str = None, db_path: str = None):
        """Initialize the mathic system with configuration and database"""
        if config_path is None:
            # Get absolute path to the mathic directory
            mathic_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(mathic_dir, "mathic_config.json")
        
        self.config_path = config_path
        self.config = self.load_config()
        
        # Initialize database
        from mathic.mathic_database import MathicDatabase
        self.db = MathicDatabase(db_path)
        
        # Load data from database
        self._modules_cache = {}  # Cache for frequently accessed modules
        self._loadouts_cache = {}  # Cache for loadouts
    
    @property
    def modules(self) -> Dict[str, Module]:
        """Get all modules (loaded from database on access)"""
        return self.db.load_all_modules()
    
    @property
    def mathic_loadouts(self) -> Dict[str, Dict[int, str]]:
        """Get all loadouts (loaded from database on access)"""
        return self.db.load_all_loadouts()
    
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
        
        # Generate unique module ID based on current database count
        current_count = self.db.get_module_count()
        module_id = f"{module_type}_{slot_position}_{current_count}"
        
        # Get max main stat value
        max_main_stat_value = module_config["max_main_stats"][main_stat]
        
        module = Module(
            module_id=module_id,
            module_type=module_type,
            slot_position=slot_position,
            level=0,
            main_stat=main_stat,
            main_stat_value=max_main_stat_value,
            matrix="",  # Default empty matrix
            matrix_count=3,  # Default matrix count
            set_tag=set_tag
        )
        
        # Save to database
        if self.db.save_module(module):
            return module
        else:
            print(f"Failed to save module {module_id} to database")
            return None
    
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
        
        # Save changes to database
        if not self.db.save_module(module):
            print(f"Failed to save module {module.module_id} after generating substats")
            return False
        
        return True
    
    def enhance_module_random_substat(self, module: Module) -> Optional[str]:
        """Randomly enhance one substat of a module"""
        if not module:
            return None
        
        # Check if module can be enhanced
        if not module.can_be_enhanced():
            return None
        
        result = None
        
        # Check if we need to add a new substat first
        if len(module.substats) < 4:
            # Add a new random substat
            available_stats = self.get_available_substats_for_module(module)
            if available_stats:
                stat_name = random.choice(available_stats)
                stat_config = self.config["substats"][stat_name]
                roll_range = stat_config["roll_range"]
                initial_value = random.randint(roll_range[0], roll_range[1])
                
                module.add_substat(stat_name, float(initial_value))
                module.total_enhancement_rolls += 1
                module.level += 1
                result = f"New substat: {stat_name}"
        else:
            # Get substats that can be enhanced (considering total roll limit)
            enhanceable_substats = module.get_enhanceable_substats()
            
            if not enhanceable_substats:
                return None
            
            # Randomly select a substat to enhance
            selected_substat = random.choice(enhanceable_substats)
            
            # Get roll value
            stat_config = self.config["substats"][selected_substat.stat_name]
            roll_range = stat_config["roll_range"]
            roll_value = random.randint(roll_range[0], roll_range[1])
            
            # Enhance the substat with roll tracking
            success = module.enhance_substat_with_roll_tracking(selected_substat.stat_name, float(roll_value))
            
            if success:
                result = selected_substat.stat_name
        
        # Save changes to database
        if result:
            if not self.db.save_module(module):
                print(f"Failed to save module {module.module_id} after enhancement")
        
        return result
    
    def enhance_module_specific_substat(self, module: Module, stat_name: str, roll_count: int = 1) -> bool:
        """Enhance a specific substat by a given number of rolls"""
        if not module or stat_name not in [s.stat_name for s in module.substats]:
            return False
        
        # Check if module can be enhanced enough times
        if module.total_enhancement_rolls + roll_count > module.max_total_rolls:
            return False
        
        # Get the substat
        target_substat = module.get_substat(stat_name)
        if not target_substat:
            return False
        
        # Check if substat can handle the rolls
        if target_substat.rolls_used + roll_count > target_substat.max_rolls:
            return False
        
        # Apply enhancements one by one to correctly track rolls
        stat_config = self.config["substats"][stat_name]
        roll_range = stat_config["roll_range"]
        
        for i in range(roll_count):
            roll_value = random.randint(roll_range[0], roll_range[1])
            success = module.enhance_substat_with_roll_tracking(stat_name, float(roll_value))
            if not success:
                return False
        
        return True
    
    def get_available_substats_for_module(self, module: Module) -> List[str]:
        """Get available substats that can be added to a module"""
        available_stats = list(self.config.get("substats", {}).keys())
        
        # Remove restricted substats for this module type
        module_type_config = self.config.get("module_types", {}).get(module.module_type, {})
        restricted_substats = module_type_config.get("restricted_substats", [])
        for restricted_stat in restricted_substats:
            if restricted_stat in available_stats:
                available_stats.remove(restricted_stat)
        
        # Remove main stat
        if module.main_stat in available_stats:
            available_stats.remove(module.main_stat)
        
        # Remove percentage version if flat version is main stat (and vice versa)
        main_stat_base = module.main_stat.replace('%', '')
        for stat in available_stats[:]:
            stat_base = stat.replace('%', '')
            if stat_base == main_stat_base and stat != module.main_stat:
                available_stats.remove(stat)
        
        # Remove already existing substats
        existing_stats = [substat.stat_name for substat in module.substats]
        for stat in existing_stats:
            if stat in available_stats:
                available_stats.remove(stat)
        
        return available_stats
    
    def get_module_by_id(self, module_id: str) -> Optional[Module]:
        """Get module by its ID"""
        # Always load fresh from database to ensure consistency
        module = self.db.load_module(module_id)
        if module:
            self._modules_cache[module_id] = module
        
        return module
    
    def get_all_modules(self) -> Dict[str, Module]:
        """Get all modules"""
        return self.db.load_all_modules()
    
    def get_available_matrices_for_module(self, module_or_type) -> List[str]:
        """Get available matrices that can be assigned to a module"""
        available_matrices = []
        
        # Handle both string module_type and Module object
        if isinstance(module_or_type, str):
            module_type = module_or_type
        else:
            module_type = module_or_type.module_type
        
        # Get common matrices (available for all module types)
        common_matrices = self.config.get("matrices", {}).get("common", [])
        available_matrices.extend(common_matrices)
        
        # Add core-exclusive matrices only if module is a core
        if module_type == "core":
            core_exclusive = self.config.get("matrices", {}).get("core_exclusive", [])
            available_matrices.extend(core_exclusive)
        
        return available_matrices
    
    def set_module_matrix(self, module_id: str, matrix_name: str, matrix_count: int = 3) -> tuple[bool, str]:
        """Set matrix for a module"""
        module = self.get_module_by_id(module_id)
        if not module:
            return False, f"Module with ID '{module_id}' not found"
        
        # Validate matrix count (1-3)
        if matrix_count < 1 or matrix_count > 3:
            return False, f"Invalid matrix count: {matrix_count}. Must be between 1 and 3."
        
        # Validate matrix name
        available_matrices = self.get_available_matrices_for_module(module)
        if matrix_name and matrix_name not in available_matrices:
            return False, f"Matrix '{matrix_name}' is not available for module type '{module.module_type}'"
        
        # Set matrix
        module.matrix = matrix_name
        module.matrix_count = matrix_count
        
        # Save to database
        if self.db.save_module(module):
            # Update cache
            self._modules_cache[module_id] = module
            return True, f"Matrix '{matrix_name}' set successfully with count {matrix_count}"
        else:
            return False, f"Failed to save matrix changes to database"
    
    def clear_module_matrix(self, module_id: str) -> bool:
        """Clear matrix from a module"""
        module = self.get_module_by_id(module_id)
        if not module:
            return False
        
        module.matrix = ""
        module.matrix_count = 3  # Reset to default
        
        # Save to database
        if self.db.save_module(module):
            # Update cache
            self._modules_cache[module_id] = module
            return True
        else:
            print(f"Failed to save matrix changes to database for module {module_id}")
            return False
    
    def calculate_substat_probabilities(self, module: Module) -> Dict[str, float]:
        """Calculate probability of getting each substat when enhancing"""
        probabilities = {}
        
        # First check if module can be enhanced at all (total rolls limit)
        if not module.can_be_enhanced():
            probabilities["No enhancement possible"] = 1.0
            return probabilities
        
        # If module has less than 4 substats, only add new substats (no enhancement of existing ones)
        if len(module.substats) < 4:
            available_stats = self.get_available_substats_for_module(module)
            
            if available_stats:
                # Only new substats can be added, each with equal probability
                prob_per_new_stat = 1.0 / len(available_stats)
                for stat in available_stats:
                    probabilities[f"New: {stat}"] = prob_per_new_stat
            else:
                # No available new substats
                probabilities["No enhancement possible"] = 1.0
        else:
            # Use the module's get_enhanceable_substats method which considers both 
            # individual substat limits and module's total roll limit
            enhanceable_substats = module.get_enhanceable_substats()
            
            if enhanceable_substats:
                prob_per_stat = 1.0 / len(enhanceable_substats)
                for substat in enhanceable_substats:
                    probabilities[substat.stat_name] = prob_per_stat
            else:
                # No substats can be enhanced (either all at max rolls or total limit reached)
                probabilities["No enhancement possible"] = 1.0
        
        return probabilities
    
    def calculate_module_value(self, module: Module) -> Dict[str, Any]:
        """Calculate module value based on substats and rolls with categorized scoring"""
        if not module or not module.substats:
            return {
                "total_value": 0.0, 
                "efficiency": 0.0, 
                "details": {},
                "defense_score": 0.0,
                "support_score": 0.0,
                "offense_score": 0.0
            }
        
        # Define stat categories and their weights (% stats have higher weight)
        stat_categories = {
            # Defense stats: HP, HP%, DEF, DEF%, Effect RES
            "defense": {
                "HP": 1.0, "HP%": 1.5, "DEF": 1.0, "DEF%": 1.5, "Effect RES": 1.2
            },
            # Support stats: SPD, Effect ACC, Effect RES  
            "support": {
                "SPD": 1.3, "Effect ACC": 1.2, "Effect RES": 1.2
            },
            # Offense stats: ATK, ATK%, CRIT Rate, CRIT DMG, SPD
            "offense": {
                "ATK": 1.0, "ATK%": 1.5, "CRIT Rate": 1.4, "CRIT DMG": 1.4, "SPD": 1.3
            }
        }
        
        total_value = 0.0
        total_max_value = 0.0
        details = {}
        
        # Category scores
        defense_score = 0.0
        support_score = 0.0
        offense_score = 0.0
        
        for substat in module.substats:
            if substat.stat_name in self.config["substats"]:
                stat_config = self.config["substats"][substat.stat_name]
                max_possible = stat_config["max_value"]
                current_efficiency = substat.get_efficiency_percentage(max_possible)
                
                # Determine category and weight for this stat
                category_weight = 1.0
                category_type = "general"
                
                for category, stats_dict in stat_categories.items():
                    if substat.stat_name in stats_dict:
                        category_weight = stats_dict[substat.stat_name]
                        category_type = category
                        break
                
                # Value calculation: efficiency * category weight * roll utilization
                roll_utilization = substat.rolls_used / substat.max_rolls if substat.max_rolls > 0 else 0
                
                substat_value = (current_efficiency / 100) * category_weight * (1 + roll_utilization * 0.5)
                
                total_value += substat_value
                total_max_value += category_weight * 1.5  # Max possible value per substat
                
                # Add to appropriate category score
                category_score = (current_efficiency / 100) * category_weight
                if category_type == "defense":
                    defense_score += category_score
                elif category_type == "support":
                    support_score += category_score
                elif category_type == "offense":
                    offense_score += category_score
                
                details[substat.stat_name] = {
                    "current_value": substat.current_value,
                    "efficiency": current_efficiency,
                    "rolls_used": substat.rolls_used,
                    "substat_value": substat_value,
                    "category_weight": category_weight,
                    "category_type": category_type
                }
        
        overall_efficiency = (total_value / total_max_value * 100) if total_max_value > 0 else 0
        
        return {
            "total_value": total_value,
            "efficiency": overall_efficiency,
            "roll_efficiency": module.total_enhancement_rolls / module.max_total_rolls * 100,
            "details": details,
            "defense_score": defense_score,
            "support_score": support_score,
            "offense_score": offense_score
        }
    
    def create_mathic_loadout(self, loadout_name: str) -> Dict[int, Optional[str]]:
        """Create a new mathic loadout with 6 slots"""
        loadout = {}
        for slot_info in self.config.get("mathic_slots", []):
            slot_id = slot_info["slot_id"]
            loadout[slot_id] = None
        
        # Save to database
        if self.db.save_loadout(loadout_name, loadout):
            # Update cache
            self._loadouts_cache[loadout_name] = loadout
            return loadout
        else:
            print(f"Failed to save loadout {loadout_name} to database")
            return {}
    
    def assign_module_to_loadout(self, loadout_name: str, slot_id: int, module_id: str) -> bool:
        """Assign a module to a specific slot in a loadout"""
        # Load loadout from database
        loadout_data = self.db.load_loadout(loadout_name)
        if loadout_data is None:
            print(f"Loadout '{loadout_name}' not found")
            return False
        
        # Validate module if provided
        if module_id:
            module = self.get_module_by_id(module_id)
            if not module:
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
            if module.module_type not in slot_info["allowed_types"]:
                print(f"Module type '{module.module_type}' not allowed in slot {slot_id}")
                return False
        
        # Update loadout data
        loadout_data[slot_id] = module_id
        
        # Save to database
        if self.db.save_loadout(loadout_name, loadout_data):
            # Update cache
            self._loadouts_cache[loadout_name] = loadout_data
            return True
        else:
            print(f"Failed to save loadout changes to database")
            return False
    
    def calculate_loadout_stats(self, loadout_name: str) -> Dict[str, float]:
        """Calculate total stats for a mathic loadout"""
        loadout_data = self.db.load_loadout(loadout_name)
        if not loadout_data:
            return {}
        
        total_stats = {}
        
        for slot_id, module_id in loadout_data.items():
            if module_id:
                module = self.get_module_by_id(module_id)
                if module:
                    # Add main stat
                    if module.main_stat in total_stats:
                        total_stats[module.main_stat] += module.main_stat_value
                    else:
                        total_stats[module.main_stat] = module.main_stat_value
                    
                    # Add substats
                    for substat in module.substats:
                        if substat.stat_name in total_stats:
                            total_stats[substat.stat_name] += substat.current_value
                        else:
                            total_stats[substat.stat_name] = substat.current_value
        
        return total_stats
    
    def get_loadout_modules(self, loadout_name: str) -> Dict[int, Optional[Module]]:
        """Get all modules in a loadout"""
        loadout_data = self.db.load_loadout(loadout_name)
        if not loadout_data:
            return {}
        
        result = {}
        
        for slot_id, module_id in loadout_data.items():
            if module_id:
                module = self.get_module_by_id(module_id)
                result[slot_id] = module
            else:
                result[slot_id] = None
        
        return result
    
    def delete_module(self, module_id: str) -> bool:
        """Delete a module from the system"""
        # Remove from cache
        if module_id in self._modules_cache:
            del self._modules_cache[module_id]
        
        # Delete from database
        return self.db.delete_module(module_id)
    
    def delete_loadout(self, loadout_name: str) -> bool:
        """Delete a loadout from the system"""
        # Remove from cache
        if loadout_name in self._loadouts_cache:
            del self._loadouts_cache[loadout_name]
        
        # Delete from database
        return self.db.delete_loadout(loadout_name)
    
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
