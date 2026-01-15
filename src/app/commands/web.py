"""
Web command module for FIB Manager.
Handles the web server command-line interface.
"""

from argparse import ArgumentParser, Namespace


def add_web_arguments(parser: ArgumentParser) -> None:
    """
    Add arguments for the web command.
    
    Args:
        parser: ArgumentParser object
    """
    parser.add_argument(
        "-p", "--port", 
        type=int, 
        default=5000,
        help="port number to listen on (default: 5000)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="host address to bind to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="enable debug mode"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="don't open browser automatically"
    )


def handle_web_command(args: Namespace) -> None:
    """
    Handle the web command.
    
    Args:
        args: ArgumentParser arguments
    """
    try:
        from app.web.server import run_server
        
        run_server(
            host=args.host,
            port=args.port,
            debug=args.debug,
            open_browser_flag=not args.no_browser
        )
    except ImportError as e:
        print(f"Error: Flask is required for the web interface.")
        print(f"Install it with: pip install flask")
        print(f"\nDetails: {e}")
    except Exception as e:
        print(f"Error starting web server: {e}")
        import traceback
        traceback.print_exc()
