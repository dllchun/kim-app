# 🔋 Battery Electrolyte Synergy Analyzer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

A comprehensive web application for analyzing synergistic effects between additives in battery electrolyte formulations.

## ✨ Features

- **Statistical Analysis**: ANOVA, t-tests, confidence intervals
- **Synergy Models**: Combination Index, Loewe Additivity, Bliss Independence  
- **Interactive GUI**: User-friendly Streamlit interface
- **Data Management**: Import/export JSON, CSV formats
- **Visualizations**: Real-time charts and plots
- **Report Generation**: Markdown and JSON exports

## 🚀 Quick Start

### Local Development
```bash
git clone <your-repo-url>
cd for-kim
pip install -r requirements.txt
streamlit run main_app.py
```

### Live Demo
Visit: [https://your-app-name.streamlit.app](https://your-app-name.streamlit.app)

## 📊 Usage

1. **Setup**: Configure additive names and measurement parameters
2. **Input Data**: Add base, individual additives, and combination data
3. **Analyze**: Calculate synergy metrics with statistical validation
4. **Visualize**: View interactive charts and response surfaces
5. **Export**: Download results in multiple formats

## 🏗️ Project Structure

```
├── main_app.py              # Streamlit app entry point
├── requirements.txt         # Python dependencies
├── synergy_app/            # Modular application package
│   ├── models/             # Data models and analysis engine
│   ├── views/              # UI components
│   ├── components/         # Reusable components
│   ├── utils/              # Utilities and helpers
│   └── config/             # Configuration settings
└── @documents/             # Documentation
```

## 🔬 Scientific Background

This tool implements established synergy analysis methods used in battery research:

- **Combination Index (CI)**: Quantifies synergistic vs antagonistic effects
- **Statistical Validation**: Ensures results are scientifically sound
- **Response Surface Modeling**: Predicts optimal formulations

## 📚 Documentation

- [User Guide](@documents/USER_GUIDE.md)
- [API Reference](@documents/API_REFERENCE.md)
- [Development Guide](@documents/CLAUDE.md)

## 🤝 Contributing

This is a research tool for battery electrolyte analysis. Contributions welcome for:
- Additional synergy models
- Enhanced visualizations
- Export formats
- Performance optimizations

## 📄 License

Open source for research and educational purposes.