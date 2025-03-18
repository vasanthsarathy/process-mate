#!/usr/bin/env python3
"""
Launcher script for the Chess Thought Process Analyzer
Ensures all dependencies are installed before running the application
"""

import sys
import subprocess
import os
import platform
import tkinter as tk
from tkinter import messagebox

# Required packages
REQUIRED_PACKAGES = [
    "python-chess",  # Chess library
    "cairosvg",      # SVG to PNG conversion
    "pillow",        # Image handling
]

def check_dependencies():
    """Check if all required packages are installed."""
    missing_packages = []
    
    for package in REQUIRED_PACKAGES:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(packages):
    """Install missing dependencies."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        return True
    except subprocess.CalledProcessError:
        return False

def check_engine():
    """Check if Stockfish is installed and accessible."""
    # Common Stockfish paths by OS
    if platform.system() == "Windows":
        paths = [
            os.path.join(os.getcwd(), "stockfish", "stockfish.exe"),
            "C:/Program Files/Stockfish/stockfish.exe"
        ]
    elif platform.system() == "Darwin":  # macOS
        paths = [
            os.path.join(os.getcwd(), "stockfish", "stockfish-mac-x64"),
            "/usr/local/bin/stockfish"
        ]
    else:  # Linux and others
        paths = [
            os.path.join(os.getcwd(), "stockfish", "stockfish-ubuntu-x64"),
            "/usr/games/stockfish",
            "/usr/bin/stockfish"
        ]
    
    for path in paths:
        if os.path.exists(path):
            return True, path
    
    return False, None

def main():
    """Main launcher function."""
    print("Chess Thought Process Analyzer - Launcher")
    print("=========================================")
    
    # Create a hidden root window for messagebox
    root = tk.Tk()
    root.withdraw()
    
    # Check for dependencies
    print("Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        
        # Ask user if they want to install missing packages
        if messagebox.askyesno(
            "Missing Dependencies",
            f"The following packages need to be installed:\n\n{', '.join(missing_packages)}\n\nInstall now?"
        ):
            print("Installing missing packages...")
            if install_dependencies(missing_packages):
                print("Dependencies installed successfully.")
            else:
                messagebox.showerror(
                    "Installation Failed",
                    "Failed to install dependencies. Please install them manually."
                )
                return
    
    # Check for Stockfish
    print("Checking for chess engine...")
    engine_found, engine_path = check_engine()
    
    if not engine_found:
        messagebox.showwarning(
            "Chess Engine Not Found",
            "Stockfish chess engine was not found. The application will start, but engine analysis will not be available."
            "\n\nYou can download Stockfish from: https://stockfishchess.org/download/"
            "\n\nAfter installation, configure the engine path in the application."
        )
    
    # Launch the main application
    print("Starting Chess Thought Process Analyzer...")
    try:
        # Import and run the application
        from chess_thought_analyzer import ChessThoughtAnalyzer
        
        # Create a new root window (since we hid the previous one)
        app_root = tk.Tk()
        app = ChessThoughtAnalyzer(app_root)
        app_root.mainloop()
        
        # Ensure engine is properly closed
        if hasattr(app, 'engine') and app.engine:
            app.stop_engine()
            
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start the application: {str(e)}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
