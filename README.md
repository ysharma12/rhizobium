# Rhizobium QA Testing Analyzer

Automated QA testing analysis with Google Drive integration, progress tracking, and beautiful visualizations.

## 🚀 Quick Start

```bash
cd agent
./setup.sh
./run_complete_analysis.sh
```

That's it! One command does everything.

## 📊 What It Does

- ☁️ **Auto-downloads** Excel file from Google Drive
- 🔍 **Analyzes** all sheets for pass/fail test results
- 📈 **Tracks** progress over time
- 📊 **Creates** beautiful charts and visualizations
- 📄 **Generates** reports for your team

## 📁 Project Structure

```
rhizobium/
├── agent/              # All scripts and tools
│   ├── 00_START_HERE.md          # Start here!
│   ├── run_complete_analysis.sh  # Main script (run daily)
│   └── ...
└── data/               # Excel files
```

## 📖 Documentation

All documentation is in the `agent/` folder:

- **[00_START_HERE.md](agent/00_START_HERE.md)** - Start here!
- **[QUICK_REFERENCE.md](agent/QUICK_REFERENCE.md)** - Quick commands
- **[GET_STARTED.md](agent/GET_STARTED.md)** - 5-minute guide
- **[README.md](agent/README.md)** - Full documentation
- **[VISUALIZATIONS.md](agent/VISUALIZATIONS.md)** - Charts guide

## 🎯 Daily Workflow

```bash
cd agent
./run_complete_analysis.sh
```

Then:
- Check `qa_summary_*.txt` for text report
- Open `visualizations/visualizations_report.html` for charts
- Share with your team!

## 🆘 Need Help?

See [agent/00_START_HERE.md](agent/00_START_HERE.md) for complete setup instructions.

## ✨ Features

- Smart column detection (handles ad-hoc formats)
- Pattern recognition (Pass, Failed, Success, Error, etc.)
- Google Drive integration
- Progress tracking over time
- 6 types of visualizations
- HTML reports
- CSV exports
- Automation ready

---

**Made with ❤️ for QA teams**


