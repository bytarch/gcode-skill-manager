#!/usr/bin/env python3
"""
G-Code Skill Manager - Main CLI
A tool to manage the .gcode/skills folder for the G-Code agent.
"""

import os
import sys
import argparse
import shutil
from github_provider import GitHubProvider, BLUE, GREEN, YELLOW, RED, BOLD, RESET, DIM
from huggingface_provider import HuggingFaceProvider

def get_skills_dir():
    """Determine the skills directory relative to the current working directory."""
    return os.path.join(os.getcwd(), ".gcode", "skills")

def ensure_skills_dir():
    """Creates the skills directory if it doesn't exist."""
    skills_dir = get_skills_dir()
    if not os.path.exists(skills_dir):
        os.makedirs(skills_dir, exist_ok=True)
        print(f"{GREEN}✔ Created skills directory at: {skills_dir}{RESET}")
    return skills_dir

def update_structure_md():
    """Generates a structure.md file for the G-Code agent to navigate skills."""
    skills_dir = get_skills_dir()
    if not os.path.exists(skills_dir):
        return

    structure_file = os.path.join(skills_dir, "structure.md")
    content = [
        "# G-Code Skills Structure\n",
        "This file is used by the G-Code agent to navigate installed skills.",
        "It provides a map of all available skill directories and their contents.\n"
    ]

    # Get all subdirectories (each is a skill)
    items = sorted([d for d in os.listdir(skills_dir) 
                   if os.path.isdir(os.path.join(skills_dir, d)) and not d.startswith('.')])
    
    if not items:
        content.append("No skills currently installed.")
    else:
        for skill in items:
            content.append(f"## 📁 {skill}")
            content.append(f"Root Path: `.gcode/skills/{skill}/`")
            content.append("### File Tree:")
            
            skill_path = os.path.join(skills_dir, skill)
            for root, dirs, files in os.walk(skill_path):
                # Indentation based on folder depth
                level = root.replace(skill_path, '').count(os.sep)
                indent = '  ' * level
                
                sub_dir = os.path.basename(root)
                if sub_dir != skill:
                    content.append(f"{indent}  📁 {sub_dir}/")
                
                file_indent = '  ' * (level + 1)
                for f in sorted(files):
                    content.append(f"{file_indent}📄 {f}")
            content.append("\n---\n")

    with open(structure_file, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    print(f"{DIM}⚙ Updated structure.md{RESET}")

def add_local_skill(source_path):
    """Copies a local file or directory into the skills directory."""
    skills_dir = ensure_skills_dir()
    if not os.path.exists(source_path):
        print(f"{RED}✘ Error: Source '{source_path}' not found.{RESET}")
        return False

    name = os.path.basename(source_path.rstrip(os.sep))
    dest_path = os.path.join(skills_dir, name)

    try:
        if os.path.isdir(source_path):
            if os.path.exists(dest_path): shutil.rmtree(dest_path)
            shutil.copytree(source_path, dest_path)
        else:
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(source_path, dest_path)
        print(f"{GREEN}✔ Added local skill: {BOLD}{name}{RESET}")
        return True
    except Exception as e:
        print(f"{RED}✘ Error: {e}{RESET}")
        return False

def list_skills():
    """Lists installed skills."""
    path = get_skills_dir()
    if not os.path.exists(path):
        print(f"{YELLOW}No skills directory found.{RESET}")
        return

    print(f"{BLUE}{BOLD}Current G-Code Skills:{RESET}")
    items = sorted(os.listdir(path))
    for item in items:
        if item.startswith('.') or item == "structure.md":
            continue
        print(f"  📁 {item}")

def remove_skill(name):
    """Removes a skill."""
    target = os.path.join(get_skills_dir(), name)
    if os.path.exists(target):
        try:
            if os.path.isdir(target): 
                shutil.rmtree(target)
            else: 
                os.remove(target)
            print(f"{GREEN}✔ Removed skill: {name}{RESET}")
            return True
        except Exception as e:
            print(f"{RED}✘ Error removing skill: {e}{RESET}")
            return False
    else:
        print(f"{RED}✘ Error: Skill '{name}' not found.{RESET}")
        return False

def main():
    # Handle prefixes like 'npx skills'
    argv = sys.argv[1:]
    while argv and argv[0] in ['npx', 'skills', 'gs', 'gskill']:
        # If the first arg is the command name itself (from some shells), skip it
        # but keep it if it's actually an action like 'ls' or 'add'
        if argv[0] in ['add', 'ls', 'rm']:
            break
        argv = argv[1:]

    parser = argparse.ArgumentParser(description="G-Code Skill Manager")
    subparsers = parser.add_subparsers(dest="command")

    # Add command
    add_p = subparsers.add_parser("add", help="Add skill (Local Path, GitHub URL, or HF Space URL)")
    add_p.add_argument("source", help="Path or URL")
    add_p.add_argument("--skill", help="Specific skill name/path within the repository")

    # List command
    subparsers.add_parser("ls", help="List all installed skills")
    
    # Remove command
    rm_p = subparsers.add_parser("rm", help="Remove an installed skill")
    rm_p.add_argument("name", help="Skill folder name")

    args = parser.parse_args(argv)

    success = False
    skills_dir = ensure_skills_dir()

    if args.command == "add":
        source = args.source
        if source.startswith(("http://", "https://")):
            if "huggingface.co" in source:
                success = HuggingFaceProvider().install_skill(source, skills_dir)
            elif "github.com" in source:
                # If --skill is provided, let the provider handle the sub-path logic
                success = GitHubProvider().install_skill(source, skills_dir)
            else:
                print(f"{RED}✘ Unsupported URL provider.{RESET}")
        else:
            success = add_local_skill(source)
            
    elif args.command == "ls":
        list_skills()
        return
    elif args.command == "rm":
        success = remove_skill(args.name)
    else:
        parser.print_help()
        return

    if success:
        update_structure_md()

if __name__ == "__main__":
    main()