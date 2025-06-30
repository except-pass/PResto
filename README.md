# Presto: GitHub PR Comment Workflow Tool

A systematic, professional approach to handling PR review comments with complete thread organization, automatic skip logic, and systematic response posting.

## 🚀 Quick Start

### Installation

```bash
pip install presto-pr
```

### Prerequisites

- **Python 3.7+**
- **GitHub CLI**: Install from [cli.github.com](https://cli.github.com/)
- **Authenticated GitHub CLI**: Run `gh auth login`

### Basic Usage

```bash
# Show all available commands
presto --help

# Analyze PR comments and organize into threads
presto analyze --repo owner/repo --pr 123

# Draft a response to thread 1
presto append --session-dir pr_123_review_20240101_120000 --thread 1 --content "Thanks for the feedback!"

# Post the response to GitHub
presto post --session-dir pr_123_review_20240101_120000 --thread 1
```

## 📋 Features

- **🔄 Thread Organization**: Automatically groups related comments into conversation threads
- **⏭️ Smart Skip Logic**: Filters out resolved threads and prevents over-commenting
- **📝 Draft Management**: Build and review responses before posting
- **📤 Systematic Posting**: Post responses individually or in batches
- **🔒 Double-Post Protection**: Prevents accidentally posting the same response twice
- **📊 Actionable Analytics**: Thread-level statistics and guidance
- **🎯 Context-Specific Help**: AWS CLI-style subcommands with targeted help

## 🛠️ Commands

### Core Workflow

```bash
# Phase 1: Analyze and organize PR comments
presto analyze --repo owner/repo --pr 123

# Phase 5: Draft responses
presto append --session-dir <session-dir> --thread <N> --content "<response>"

# Phase 6: Post responses
presto post --session-dir <session-dir> --thread <N>
presto post --session-dir <session-dir> --all  # Batch mode
```

### Utilities

```bash
# Search comments for specific text
presto search --repo owner/repo --pr 123 --query "validation"

# Direct reply to specific comment ID
presto reply --repo owner/repo --pr 123 --comment-id 456 --message "Response"
```

### Command Help

Each command has detailed help:

```bash
presto analyze --help
presto append --help
presto post --help
presto search --help
presto reply --help
```

## 📖 Workflow

1. **Analyze**: `presto analyze` creates organized thread files in a session directory
2. **Review**: Examine threads marked `[NEEDS RESPONSE]`, skip `SKIP_*` files
3. **Draft**: Use `presto append` to add responses to thread files
4. **Edit**: Manually refine responses in the thread files
5. **Post**: Use `presto post` to systematically submit responses to GitHub

## 📁 File Organization

```
pr_123_review_20240101_120000/
├── session_summary.md           # Overview and statistics
├── thread_01_alice_validation.md    # Thread requiring response
├── thread_02_SKIP_bob_typo.md       # Auto-skipped thread
└── thread_03_charlie_performance.md # Another thread
```

## 🔧 Development

### Local Installation

```bash
git clone https://github.com/your-username/presto
cd presto
pip install -e .
```

### Run Tests

```bash
pip install -e ".[dev]"
pytest
```

## 📜 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/presto/issues)
- **Documentation**: This README and `presto --help`
- **Source**: [GitHub Repository](https://github.com/your-username/presto)