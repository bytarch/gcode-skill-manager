#!/usr/bin/env python3
"""
GitHub Provider for G-Code Skill Manager
Handles parsing GitHub URLs and recursive tree downloads via the GitHub API.
"""

import os
import json
import re
import urllib.request
import shutil

# Terminal coloring constants
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"

class GitHubProvider:
    def __init__(self, user_agent="G-Code-Skill-Manager"):
        self.headers = {'User-Agent': user_agent}

    def parse_url(self, url):
        """
        Parses a GitHub URL into owner, repo, branch, and path.
        """
        pattern = r"github\.com/([^/]+)/([^/]+)/(tree|blob)/([^/]+)/(.*)"
        match = re.search(pattern, url)
        if match:
            owner, repo, _, branch, path = match.groups()
            return owner, repo, branch, path
        
        pattern_simple = r"github\.com/([^/]+)/([^/]+)$"
        match_simple = re.search(pattern_simple, url)
        if match_simple:
            owner, repo = match_simple.groups()
            return owner, repo, None, ""
            
        return None

    def _get_api_data(self, url):
        """Helper to fetch JSON from GitHub API."""
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())

    def download_file(self, url, dest_path):
        """Downloads a single file from a URL."""
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
            out_file.write(response.read())

    def install_skill(self, url, target_base_dir):
        """Recursively downloads a GitHub directory using the Recursive Tree API."""
        parsed = self.parse_url(url)
        if not parsed:
            print(f"{RED}✘ Invalid GitHub URL format.{RESET}")
            return False

        owner, repo, branch_hint, path_filter = parsed
        owner_repo = f"{owner}/{repo}"
        
        # Clean path filter (remove trailing slashes)
        path_filter = path_filter.strip('/')
        skill_name = path_filter.split('/')[-1] if path_filter else repo
        
        print(f"{BLUE}🔍 Fetching structure from {owner_repo}...{RESET}")
        
        branches_to_try = [branch_hint] if branch_hint else ['main', 'master']
        tree_data = None
        active_branch = None

        for branch in branches_to_try:
            api_url = f"https://api.github.com/repos/{owner_repo}/git/trees/{branch}?recursive=1"
            try:
                tree_data = self._get_api_data(api_url)
                active_branch = branch
                break 
            except Exception:
                continue

        if not tree_data or 'tree' not in tree_data:
            print(f"{RED}✘ Error: Could not fetch repository tree.{RESET}")
            return False

        # Find the actual path in the tree. 
        # Sometimes user provides 'react-best-practices' but it's at 'skills/react-best-practices'
        actual_path = None
        if path_filter:
            # Try exact match first
            if any(item['path'] == path_filter for item in tree_data['tree']):
                actual_path = path_filter
            else:
                # Try fuzzy match (ends with)
                for item in tree_data['tree']:
                    if item['type'] == 'tree' and item['path'].endswith('/' + path_filter):
                        actual_path = item['path']
                        break
        else:
            actual_path = "" # Root

        if actual_path is None:
            print(f"{RED}✘ Path '{path_filter}' not found in the repository.{RESET}")
            return False

        files_to_download = []
        for item in tree_data['tree']:
            # If path is empty (root), we want everything. Otherwise, starts with actual_path/
            if item['type'] == 'blob':
                is_match = False
                if actual_path == "":
                    is_match = True
                elif item['path'] == actual_path or item['path'].startswith(actual_path + '/'):
                    is_match = True
                
                if is_match:
                    rel_path = os.path.relpath(item['path'], actual_path) if actual_path else item['path']
                    raw_url = f"https://raw.githubusercontent.com/{owner_repo}/{active_branch}/{item['path']}"
                    files_to_download.append((raw_url, rel_path))

        if not files_to_download:
            print(f"{YELLOW}⚠ No files found at {actual_path}{RESET}")
            return False

        target_root = os.path.join(target_base_dir, skill_name)
        try:
            if os.path.exists(target_root):
                shutil.rmtree(target_root)
            os.makedirs(target_root, exist_ok=True)

            for raw_url, rel_path in files_to_download:
                dest_path = os.path.join(target_root, rel_path)
                print(f"  {DIM}📄 Downloading: {rel_path}{RESET}")
                self.download_file(raw_url, dest_path)
                
            print(f"{GREEN}✔ Successfully installed: {BOLD}{skill_name}{RESET}")
            return True
        except Exception as e:
            print(f"{RED}✘ Failed to install: {e}{RESET}")
            return False