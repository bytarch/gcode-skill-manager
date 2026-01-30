# G-Code Skill Manager 🛠️

A lightweight, high-performance CLI tool designed to manage skills for the **G-Code AI agent**. Created by **BytArch**, this tool is compatible with [https://skills.sh/](https://skills.sh/) and enhances the [G-Code AI CLI](https://github.com/bytarch/g_code) by allowing you to quickly pull specialized prompt engineering skills, coding best practices, and utility tools from GitHub repositories or local directories directly into your project.

**Repository**: [https://github.com/bytarch/gcode-skill-manager](https://github.com/bytarch/gcode-skill-manager)

## Features

- **Double-W Commands**: Supports both `gskill` and the ultra-short `gs` for rapid workflow.
- **Skills.sh Compatible**: Works with https://skills.sh/ commands and format
- **Smart GitHub Fetching**: Recursively downloads specific subdirectories from GitHub repos without needing the full repository.
- **Agent-Ready Navigation**: Automatically maintains a `structure.md` file in your skills folder so the G-Code agent can understand its own capabilities.
- **Local Integration**: Easily link local development folders as skills.

## Installation

You can install the gcode-skill-manager package using pip directly from the GitHub repository:

```bash
pip install git+https://github.com/bytarch/gcode-skill-manager.git
```

### Alternative Installation Methods

**Option 1: Clone the Repository**
Clone the gcode-skill-manager repository and install locally:

```bash
git clone https://github.com/bytarch/gcode-skill-manager.git
cd gcode-skill-manager
pip install .
```

**Option 2: Install from Local Directory**
If you already have the project files locally, install directly via pip from your project directory:

```bash
pip install .
```

After installation, the `gskill` and `gs` commands will be available in your terminal.

## Usage

The manager creates a `.gcode/skills` directory in your current working directory.

### Adding Skills

#### From a GitHub Repository:
You can point to a specific subfolder using the `--skill` flag.

```bash
# Add a specific skill from a repository
gs npx skills add https://github.com/coreyhaines31/marketingskills --skill seo-audit

# Alternative syntax
gs add https://github.com/coreyhaines31/marketingskills --skill seo-audit

# Add from a specific skills directory
gs add https://github.com/coreyhaines31/marketingskills/tree/main/skills

# Add a specific skill from a subdirectory
gs add https://github.com/coreyhaines31/marketingskills/tree/main/skills/copywriting
```

#### From a Local Directory:

```bash
gs add ./path/to/my-custom-skill
```

### Listing Skills

View all currently installed skills and their folder structures.

```bash
gs ls
```

### Removing Skills

```bash
gs rm seo-audit
```

## How it works for G-Code

When you add or remove a skill, `gskill` automatically generates a `.gcode/skills/structure.md` file. This file contains:

- A list of all installed skill names.
- The exact file paths for every file within those skills.
- Instructions for the G-Code agent on how to reference these tools.

When the G-Code agent starts, it reads this structure to know which coding standards or "skills" it has available to assist you better.

## Project Structure

- `main.py`: The core CLI logic and entry point.
- `github_provider.py`: Handles recursive tree downloads from GitHub.
- `huggingface_provider.py`: Handles SKILL.md extraction from Hugging Face Spaces.
- `.gcode/skills/`: The destination for all your agent's abilities.

## License

MIT - Created by [BytArch](https://github.com/bytarch) for the [G-Code AI Agent](https://github.com/bytarch/g_code)