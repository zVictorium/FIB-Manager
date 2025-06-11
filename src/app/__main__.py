import sys
import traceback
import os

# Add the src directory to the Python path for proper imports
if hasattr(sys, '_MEIPASS'):
    # Running as compiled executable
    sys.path.insert(0, os.path.join(sys._MEIPASS, 'src'))
else:
    # Running as script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)
    sys.path.insert(0, src_dir)

try:
    from app.commands.command_line import main
    main()
except Exception as e:
    print(f"Error in FIB Manager: {e}")
    traceback.print_exc()
    sys.exit(1)