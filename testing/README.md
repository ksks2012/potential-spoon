# Testing Directory

This directory contains all test scripts for the Etheria simulation system.

## Main Test Files

### Integrated Test Suite
- `testing_integrated_suite.py` - **Main test file**: Complete system functionality testing
- `testing_infinite_loop_fix.py` - Specialized infinite loop fix verification testing
- `testing_final_verification.py` - Module Editor functionality fix final verification

### Other Files
- `demo_mathic.py` - Mathic system demonstration script
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

## Important Notes

- All test files have been updated with correct path references
- Tests use English output and comments
- Removed duplicate and outdated test content
- Integrated tests are more comprehensive and efficient
- Supports both automated testing and manual verification
