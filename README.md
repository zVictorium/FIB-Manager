<div align="center">
  <img src="docs/logo/logo.png" alt="FIB Manager Logo" width="200">
</div>

# FIB Manager

A powerful command-line and interactive console application for FIB (Facultat d'Informàtica de Barcelona - UPC) students to search, generate, and manage class schedules and academic grade calculations using the official UPC public API.

## 🚀 Features

- **Smart Schedule Generation**: Automatically finds all valid combinations of classes that fit your constraints
- **Interactive Schedule Viewer**: Beautiful visual interface to browse and compare different schedule options  
- **Grade Calculator (Beta)**: Advanced formula-based calculator for academic grade planning and analysis
- **Subject Browser**: Comprehensive database of all available subjects per quadrimester

## 🛠️ Installation

### Option 1: Pre-built Executables (Easiest)

Download ready-to-use executable files from the [Releases Page](https://github.com/zvictorium/fib-manager/releases):

- **App Version**: Download `FIB Manager.exe` (Interactive console application)
- **CLI Version**: Download `fib-manager.exe` (Command-line interface)

Simply download and run - no Python installation required!

### Option 2: Quick Setup (For Developers)

```bat
# Clone or download the project
cd fib-manager

# Run the automated setup script
.\scripts\setup.bat
```

## 🎯 Usage

### Interactive Mode (Recommended)

```bash
fib-manager app
```

### Command Line Interface

```bash
# Generate schedules
fib-manager schedules -s IES XC --start 9 --end 18

# List subjects  
fib-manager subjects -q 2024Q1 -l en

# Calculate grades (Beta)
fib-manager marks --formula "EX1*0.6+EX2*0.4" --target 7.0
```

## 📸 Screenshots

### Interactive App Main Menu
![Main Menu](docs/screenshots/main-menu.png)

### Schedule Browser
![Schedule Viewer](docs/screenshots/schedule-viewer.png)

### Subject Explorer
![Subject Browser](docs/screenshots/subject-browser.png)

### Grade Calculator (Beta)
![Grade Calculator](docs/screenshots/grade-calculator.png)

## 📚 Documentation

For detailed technical documentation, command references, and API information, please visit our [Wiki](../../wiki).

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**.

## 🙋 Support

- **🐙 Repository**: [https://github.com/zvictorium/fib-manager](https://github.com/zvictorium/fib-manager)
- **📋 Issues**: [Report bugs or request features](https://github.com/zvictorium/fib-manager/issues)
- **📚 Documentation**: [Visit our Wiki](../../wiki)
- **📦 Releases**: [Download latest version](https://github.com/zvictorium/fib-manager/releases)

---

**Made with ❤️ for FIB students at UPC**
