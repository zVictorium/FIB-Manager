import sys
import traceback

try:
    print("Starting FIB Manager...")
    from .commands.command_line import main
    main()
except Exception as e:
    print(f"Error in FIB Manager: {e}")
    traceback.print_exc()
    sys.exit(1)