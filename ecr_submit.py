#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
import yaml

class ECRSubmitter:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = Path(plugin_dir)
        self.github_token = os.environ.get('GITHUB_TOKEN')
        if not self.github_token:
            raise ValueError("GITHUB_TOKEN environment variable not set")
            
    def validate_plugin(self) -> bool:
        """Validate plugin structure and required files"""
        required_files = [
            'main.py',
            'requirements.txt',
            'Dockerfile',
            'sage.yaml',
            'README.md',
            'ecr-meta/ecr-science-description.md'
        ]
        
        for file in required_files:
            if not (self.plugin_dir / file).exists():
                print(f"❌ Missing required file: {file}")
                return False
                
        print("✅ All required files present")
        return True
        
    def create_github_repo(self) -> str:
        """Create a new GitHub repository for the plugin"""
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Read plugin name from sage.yaml
        with open(self.plugin_dir / 'sage.yaml') as f:
            sage_config = yaml.safe_load(f)
            repo_name = sage_config['name']
            
        # Create repo
        data = {
            'name': repo_name,
            'description': sage_config.get('description', ''),
            'private': False,
            'auto_init': False
        }
        
        response = requests.post(
            'https://api.github.com/user/repos',
            headers=headers,
            json=data
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to create repo: {response.text}")
            
        repo_url = response.json()['clone_url']
        print(f"✅ Created GitHub repo: {repo_url}")
        return repo_url
        
    def setup_git(self, repo_url: str):
        """Initialize git and push to GitHub"""
        os.chdir(self.plugin_dir)
        
        # Initialize git if needed
        if not (self.plugin_dir / '.git').exists():
            subprocess.run(['git', 'init'], check=True)
            
        # Configure git
        subprocess.run(['git', 'config', 'user.name', 'SAGE Plugin Submitter'], check=True)
        subprocess.run(['git', 'config', 'user.email', 'noreply@sagecontinuum.org'], check=True)
        
        # Add and commit files
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Initial plugin commit'], check=True)
        
        # Add remote and push
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
        subprocess.run(['git', 'push', '-u', 'origin', 'main'], check=True)
        print("✅ Pushed code to GitHub")
        
    def update_version(self):
        """Update version in sage.yaml using date-based versioning"""
        sage_yaml_path = self.plugin_dir / 'sage.yaml'
        with open(sage_yaml_path) as f:
            config = yaml.safe_load(f)
            
        # Generate version: v{year}.{month}.{day}.{counter}
        now = datetime.now()
        version = f"v{now.year}.{now.month}.{now.day}.1"
        config['version'] = version
        
        with open(sage_yaml_path, 'w') as f:
            yaml.dump(config, f)
            
        print(f"✅ Updated version to {version}")
        
    def submit_to_ecr(self):
        """Print instructions for ECR submission"""
        print("\n📋 ECR Submission Instructions:")
        print("1. Visit https://portal.sagecontinuum.org/apps/")
        print("2. Click 'Sign In' and authenticate")
        print("3. Go to 'My Apps'")
        print("4. Click 'Create App' and enter your GitHub repo URL")
        print("5. Click 'Register and Build App'")
        print("6. After build completes, make the plugin public")
        print("\nNote: The build process may take 15-30 minutes.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python ecr_submit.py <plugin_directory>")
        sys.exit(1)
        
    plugin_dir = sys.argv[1]
    submitter = ECRSubmitter(plugin_dir)
    
    try:
        # Validate plugin structure
        if not submitter.validate_plugin():
            sys.exit(1)
            
        # Create GitHub repo and push code
        repo_url = submitter.create_github_repo()
        submitter.update_version()
        submitter.setup_git(repo_url)
        
        # Show ECR submission instructions
        submitter.submit_to_ecr()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 