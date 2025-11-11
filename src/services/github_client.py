from github import Github
import os
import sys
from utils.logger import setup_logger

class GitHubClient:
    """
    Handles all GitHub API operations
    """
    
    def __init__(self):
        self.logger = setup_logger("GitHubClient")
        self.token = os.getenv("GITHUB_TOKEN")
        
        if not self.token:
            self.logger.error("GITHUB_TOKEN not found in environment")
            sys.exit(1)
        
        self.client = Github(self.token)
        self.user = self.client.get_user()
        self.logger.info(f"Connected to GitHub as: {self.user.login}")
    
    def get_repo(self, repo_name):
        """Get repository object"""
        try:
            repo = self.client.get_repo(repo_name)
            self.logger.info(f"Accessed repo: {repo_name}")
            return repo
        except Exception as e:
            self.logger.error(f"Failed to access repo {repo_name}: {e}")
            return None
    
    def create_branch(self, repo_name, branch_name, base_branch):
        """Create new branch from base"""
        try:
            repo = self.get_repo(repo_name)
            if not repo:
                return False
            
            base_ref = repo.get_branch(base_branch)
            repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=base_ref.commit.sha
            )
            
            self.logger.info(f"Created branch '{branch_name}' from '{base_branch}' in {repo_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create branch in {repo_name}: {e}")
            return False
    
    def get_file_content(self, repo_name, file_path, branch):
        """Get file content from repo"""
        try:
            repo = self.get_repo(repo_name)
            if not repo:
                return None, None
            
            content = repo.get_contents(file_path, ref=branch)
            file_content = content.decoded_content.decode('utf-8')
            
            self.logger.info(f"Retrieved {file_path} from {repo_name}:{branch}")
            return file_content, content.sha
            
        except Exception as e:
            self.logger.warning(f"File {file_path} not found in {repo_name}:{branch}")
            return None, None
    
    def update_file(self, repo_name, file_path, content, branch, message, sha=None):
        """Update or create file in repo"""
        try:
            repo = self.get_repo(repo_name)
            if not repo:
                return False
            
            if sha:
                repo.update_file(
                    path=file_path,
                    message=message,
                    content=content,
                    sha=sha,
                    branch=branch
                )
                self.logger.info(f"Updated {file_path} in {repo_name}:{branch}")
            else:
                repo.create_file(
                    path=file_path,
                    message=message,
                    content=content,
                    branch=branch
                )
                self.logger.info(f"Created {file_path} in {repo_name}:{branch}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update {file_path} in {repo_name}: {e}")
            return False
    
    def get_workflow(self, repo_name, workflow_file):
        """Get workflow object"""
        try:
            repo = self.get_repo(repo_name)
            if not repo:
                return None
            
            workflow = repo.get_workflow(workflow_file)
            self.logger.info(f"Retrieved workflow {workflow_file} from {repo_name}")
            return workflow
            
        except Exception as e:
            self.logger.error(f"Failed to get workflow {workflow_file} in {repo_name}: {e}")
            return None
    
    def trigger_workflow(self, repo_name, workflow_file, branch):
        """Trigger GitHub Actions workflow"""
        try:
            workflow = self.get_workflow(repo_name, workflow_file)
            if not workflow:
                return None
            
            workflow.create_dispatch(ref=branch)
            self.logger.info(f"Triggered workflow {workflow_file} on {repo_name}:{branch}")
            
            runs = workflow.get_runs(branch=branch)
            if runs.totalCount > 0:
                return runs[0]
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to trigger workflow in {repo_name}: {e}")
            return None
    
    def get_workflow_logs(self, repo_name, run_id):
        """Get workflow run logs"""
        try:
            repo = self.get_repo(repo_name)
            if not repo:
                return None
            
            run = repo.get_workflow_run(run_id)
            jobs = list(run.jobs())
            
            logs = {
                'run_id': run_id,
                'status': run.status,
                'conclusion': run.conclusion,
                'url': run.html_url,
                'jobs': []
            }
            
            for job in jobs:
                job_data = {
                    'name': job.name,
                    'status': job.status,
                    'conclusion': job.conclusion,
                    'steps': []
                }
                
                for step in job.steps:
                    job_data['steps'].append({
                        'name': step.name,
                        'status': step.status,
                        'conclusion': step.conclusion
                    })
                
                logs['jobs'].append(job_data)
            
            self.logger.info(f"Retrieved logs for run {run_id} in {repo_name}")
            return logs
            
        except Exception as e:
            self.logger.error(f"Failed to get logs for run {run_id}: {e}")
            return None
