# Testing Directory

This directory contains all test scripts for the Etheria simulation system.

## Main Test Files

### Integrated Test Suite
- `testing_integrated_suite.py` - **Main test file**: Complete system functionality testing
- `testing_infinite_loop_fix.py` - Specialized infinite loop fix verification testing
- `testing_final_verification.py` - Module Editor functionality fix final verification

### Shells Parser Testing Suite
- `testing_shells_parser_suite.py` - **Complete shells parser test**: Full HTML parsing functionality testing
- `testing_shell_structure.py` - Shell HTML structure analysis and validation
- `testing_skills_extraction.py` - Awakened/Non-Awakened skills parsing logic testing
- `testing_matrix_sets.py` - Matrix sets extraction and image source parsing testing

### Other Files
- `demo_mathic.py` - Mathic system demonstration script
- `demo_matrix_db.py` - Matrix database demonstration script
- `demo_matrix_parser.py` - Matrix parser demonstration script
- `mathic_config.json` - Test configuration file
- `db/` - Test database files

## How to Run Tests

1. Activate virtual environment:
   ```bash
   source rt-sandbox/bin/activate
   ```

2. Switch to testing directory:
   ```bash
   cd testing
   ```

3. Execute test files:
   ```bash
   # Run complete system test (recommended)
   python3 testing_integrated_suite.py
   
   # Run infinite loop specialized test
   python3 testing_infinite_loop_fix.py
   
   # Run final verification test
   python3 testing_final_verification.py
   
   # Run complete shells parser test suite
   python3 testing_shells_parser_suite.py ../var/shells.html ../shells_parsed.json
   
   # Run individual shells parser tests
   python3 testing_shell_structure.py ../var/shells.html
   python3 testing_skills_extraction.py ../var/shells.html
   python3 testing_matrix_sets.py ../var/shells.html
   ```

## Test Content

### testing_integrated_suite.py (Main Test)
- ✅ Mathic system core functionality
- ✅ UI Module Editor functionality
- ✅ Infinite loop protection mechanism
- ✅ Loadout system testing
- ✅ Complete English test reporting

### testing_infinite_loop_fix.py (Specialized Test)
- 🛡️ Original reported scenario testing
- 🛡️ Rapid consecutive violation testing
- 🛡️ Protection mechanism state cleanup testing
- 🛡️ Quick protection mechanism checking

### testing_shells_parser_suite.py (Complete Shells Parser Test)
- 🔍 Shell HTML structure validation
- 🔍 Skills extraction (awakened/non-awakened) testing
- 🔍 Matrix sets parsing and validation
- 🔍 Complete parser execution and output validation
- 🔍 Comprehensive test reporting with PASS/FAIL status

### Individual Shells Parser Tests
- **testing_shell_structure.py**: Basic shell element structure analysis
- **testing_skills_extraction.py**: Skill detection logic and extraction testing
- **testing_matrix_sets.py**: Matrix sets image source parsing and name extraction

## Important Notes

- All test files have been updated with correct path references
- Tests use English output and comments
- Removed duplicate and outdated test content
- Integrated tests are more comprehensive and efficient
- Supports both automated testing and manual verification
- Shells parser tests require HTML input file: `../var/shells.html`
- Expected parser output file: `../shells_parsed.json`
- All shells parser tests validate complete data extraction (name, rarity, class, cooldown, skills, stats, matrix sets)
