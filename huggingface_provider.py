#!/usr/bin/env python3
"""
HuggingFace Provider for G-Code Skill Manager
Handles downloading SKILL.md files from Hugging Face Spaces.
"""

import os
import json
import re
import urllib.request

# Terminal coloring constants
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"

class HuggingFaceProvider:
    def __init__(self, user_agent="G-Code-Skill-Manager"):
        self.headers = {'User-Agent': user_agent}
        self.host = 'huggingface.co'

    def parse_url(self, url):
        """
        Parses a Hugging Face Spaces URL to extract owner and repo.
        Matches: /spaces/{owner}/{repo}/
        """
        # Logic mirroring the TypeScript implementation
        if not url.startswith(('http://', 'https://')):
            return None

        try:
            # Check hostname
            if self.host not in url:
                return None
            
            # Must be a spaces URL and end with skill.md
            if '/spaces/' not in url or not url.lower().endswith('/skill.md'):
                return None

            # Match: /spaces/{owner}/{repo}/
            match = re.search(r"/spaces/([^/]+)/([^/]+)", url)
            if match:
                return {
                    "owner": match.group(1),
                    "repo": match.group(2)
                }
        except Exception:
            pass
            
        return None

    def to_raw_url(self, url):
        """
        Convert blob URL to raw URL.
        https://huggingface.co/spaces/owner/repo/blob/main/SKILL.md
        -> https://huggingface.co/spaces/owner/repo/raw/main/SKILL.md
        """
        return url.replace('/blob/', '/raw/')

    def download_file(self, url):
        """Fetches the content of the SKILL.md file."""
        raw_url = self.to_raw_url(url)
        req = urllib.request.Request(raw_url, headers=self.headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status != 200:
                return None
            return response.read().decode('utf-8')

    def install_skill(self, url, target_base_dir):
        """Downloads the SKILL.md and installs it based on repo metadata."""
        parsed = self.parse_url(url)
        if not parsed:
            print(f"{RED}✘ Invalid Hugging Face Spaces SKILL URL.{RESET}")
            return False

        print(f"{BLUE}🔍 Fetching skill from Hugging Face Spaces: {BOLD}{parsed['owner']}/{parsed['repo']}{RESET}...")

        try:
            content = self.download_file(url)
            if not content:
                print(f"{RED}✘ Failed to fetch content from {url}{RESET}")
                return False

            # Basic YAML frontmatter extraction (simulating 'matter' library)
            install_name = parsed['repo']
            fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if fm_match:
                import yaml # Assuming yaml is available or use simple regex
                try:
                    # Simple regex fallback if yaml isn't installed for metadata parsing
                    name_match = re.search(r"install-name:\s*['\"]?([^'\"\n]+)['\"]?", fm_match.group(1))
                    if name_match:
                        install_name = name_match.group(1)
                except Exception:
                    pass

            target_root = os.path.join(target_base_dir, install_name)
            
            if os.path.exists(target_root):
                import shutil
                shutil.rmtree(target_root)
            os.makedirs(target_root, exist_ok=True)

            dest_path = os.path.join(target_root, "SKILL.md")
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            print(f"{GREEN}✔ Successfully installed skill: {BOLD}{install_name}{RESET}")
            return True

        except Exception as e:
            print(f"{RED}✘ Failed to install skill: {e}{RESET}")
            return False