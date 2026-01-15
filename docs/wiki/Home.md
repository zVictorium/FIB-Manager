# FIB Manager Wiki

Welcome to the **FIB Manager** wiki! This documentation provides comprehensive information about using and configuring FIB Manager for your academic scheduling needs at FIB (Facultat d'Informàtica de Barcelona - UPC).

## 📖 Table of Contents

- [Home](Home.md) ← You are here
- [Installation Guide](Installation.md)
- [Commands Reference](Commands.md)
- [Interactive Mode Guide](Interactive-Mode.md)
- [API Reference](API-Reference.md)
- [FAQ & Troubleshooting](FAQ.md)

## 🎯 What is FIB Manager?

FIB Manager is a powerful command-line and interactive console application designed specifically for FIB students. It helps you:

- **Generate Smart Schedules**: Automatically find all valid class combinations that fit your constraints
- **Browse Available Subjects**: Explore all subjects available per quadrimester with detailed information
- **Calculate Grades**: Use advanced formula-based calculations for academic grade planning (Beta)
- **Visualize Schedules**: Beautiful interactive interface to browse and compare different schedule options

## 🚀 Quick Start

### Using Pre-built Executables

1. Download the latest release from [GitHub Releases](https://github.com/zvictorium/fib-manager/releases)
2. Run `FIB Manager.exe` for interactive mode, or `fib-manager.exe` for CLI

### Using Python

```bash
# Clone the repository
git clone https://github.com/zvictorium/fib-manager.git
cd fib-manager

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m app app
```

## 💡 Features Overview

### Schedule Generation

FIB Manager fetches real-time data from the official UPC FIB API and generates all possible schedule combinations based on your preferences:

- Time constraints (start/end hours)
- Language preferences (English, Spanish, Catalan)
- Maximum days with classes
- Group blacklisting
- Dead hours limits

### Interactive Interface

The interactive mode provides a user-friendly experience with:

- Visual schedule browser
- Subject explorer
- Grade calculator
- Easy parameter selection

### Command Line Interface

For power users and automation, the CLI offers:

- JSON output for integration with other tools
- Scripting support
- All features accessible via command arguments

## 📊 Data Source

FIB Manager uses the official UPC FIB Public API:
- **Base URL**: `https://api.fib.upc.edu/v2`
- **Data**: Real-time class schedules, subjects, and groups

## 🔗 Quick Links

- [GitHub Repository](https://github.com/zvictorium/fib-manager)
- [Report Issues](https://github.com/zvictorium/fib-manager/issues)
- [Download Releases](https://github.com/zvictorium/fib-manager/releases)

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.

---

**Next**: [Installation Guide →](Installation.md)
