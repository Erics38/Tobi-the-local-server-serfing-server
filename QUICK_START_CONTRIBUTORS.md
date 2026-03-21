# Quick Start for Contributors - 5 Minutes

This is the fastest way to start contributing. For detailed docs, see [CONTRIBUTING.md](.github/CONTRIBUTING.md).

## 1. Fork and Clone (30 seconds)

```bash
# Fork on GitHub, then:
git clone https://github.com/YOUR_USERNAME/restaurant-ai-chatbot.git
cd restaurant-ai-chatbot
```

## 2. Setup Environment (2 minutes)

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install everything
pip install -r requirements.txt
pip install pytest pytest-asyncio black flake8 mypy
```

## 3. Verify Everything Works (1 minute)

```bash
# Run the verification script
./scripts/verify-ci-locally.sh  # Linux/macOS
# OR
scripts\verify-ci-locally.bat   # Windows
```

If all checks pass ✅, you're ready to code!

## 4. Development Workflow

```bash
# Create branch
git checkout -b feature/your-feature

# Make changes, then verify before committing
./scripts/verify-ci-locally.sh

# Commit and push
git add .
git commit -m "Add your feature"
git push origin feature/your-feature
```

## 5. Create Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Wait for CI checks to pass (they run automatically)
4. Done!

## Common Commands

```bash
# Run tests only
pytest tests/ -v

# Format code
black app/ tests/ --line-length=120

# Check linting
flake8 app/ tests/ --max-line-length=120 --extend-ignore=E203,W503

# Run app locally
python -m app.main
# Visit: http://localhost:8000/api/docs
```

## CI/CD Status

Your fork will automatically run these checks on every push:
- ✅ Code formatting (Black)
- ✅ Linting (Flake8)
- ✅ Type checking (MyPy)
- ✅ Tests (Pytest)
- ✅ Security (CodeQL, Bandit)

View status: `https://github.com/YOUR_USERNAME/restaurant-ai-chatbot/actions`

## Getting Help

- 📖 [Full Contributing Guide](.github/CONTRIBUTING.md)
- 🔧 [CI/CD Setup Guide](CICD_SETUP.md)
- 📝 [Main README](README.md)
- 🐛 [Open an Issue](https://github.com/Erics38/restaurant-ai-chatbot/issues)

## Pro Tips

1. **Enable Actions in your fork** - Go to Actions tab and click "I understand..."
2. **Run verify script before pushing** - Catches issues locally
3. **Check CI status in PR** - Scroll to bottom of PR page
4. **Use virtual environment** - Keeps dependencies isolated

That's it! You're ready to contribute. 🚀
