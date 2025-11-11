import time
from datetime import datetime
from pathlib import Path
from utils.logger import setup_logger

class WorkflowManager:
    """
    Trigger and monitor GitHub Actions workflows
    """
    
    def __init__(self, github_client, service_manager):
        self.logger = setup_logger("WorkflowManager")
        self.gh = github_client
        self.sm = service_manager
        self.logs_dir = Path("logs/workflows")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def trigger_workflow(self, repo_name, workflow_file, branch):
        """Trigger workflow for a service"""
        try:
            self.logger.info(f"Triggering workflow {workflow_file} on {repo_name}:{branch}")
            
            run = self.gh.trigger_workflow(repo_name, workflow_file, branch)
            
            if run:
                self.logger.info(f"Workflow triggered successfully. Run ID: {run.id}")
                return run
            else:
                self.logger.warning(f"Could not get run information for {repo_name}")
                return None
            
        except Exception as e:
            self.logger.error(f"Failed to trigger workflow for {repo_name}: {e}")
            return None
    
    def trigger_all_workflows(self, branch):
        """Trigger workflows for all services"""
        services = self.sm.get_all_services()
        workflow_file = self.sm.config['workflow']['workflow_file']
        
        results = []
        
        for service in services:
            self.logger.info(f"Triggering workflow for {service['name']}")
            
            run = self.trigger_workflow(
                service['repo_name'],
                workflow_file,
                branch
            )
            
            results.append({
                'service': service['name'],
                'repo_name': service['repo_name'],
                'run': run,
                'run_id': run.id if run else None,
                'success': run is not None
            })
            
            time.sleep(2)
        
        return results
    
    def wait_for_completion(self, repo_name, run_id, timeout=600):
        """Wait for workflow run to complete"""
        try:
            self.logger.info(f"Waiting for run {run_id} to complete (timeout: {timeout}s)")
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                logs = self.gh.get_workflow_logs(repo_name, run_id)
                
                if not logs:
                    time.sleep(10)
                    continue
                
                status = logs['status']
                
                self.logger.info(f"Run {run_id} status: {status}")
                
                if status == 'completed':
                    self.logger.info(f"Run {run_id} completed with conclusion: {logs['conclusion']}")
                    return logs
                
                time.sleep(10)
            
            self.logger.warning(f"Run {run_id} did not complete within timeout")
            return None
            
        except Exception as e:
            self.logger.error(f"Error waiting for run {run_id}: {e}")
            return None
    
    def extract_logs_to_file(self, repo_name, run_id, service_name):
        """Extract workflow logs to file"""
        try:
            logs = self.gh.get_workflow_logs(repo_name, run_id)
            
            if not logs:
                self.logger.error(f"Could not retrieve logs for run {run_id}")
                return None
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = self.logs_dir / f"{service_name}_{run_id}_{timestamp}.log"
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"Workflow Logs for {service_name}\n")
                f.write(f"{'=' * 80}\n")
                f.write(f"Repository: {repo_name}\n")
                f.write(f"Run ID: {run_id}\n")
                f.write(f"Status: {logs['status']}\n")
                f.write(f"Conclusion: {logs['conclusion']}\n")
                f.write(f"URL: {logs['url']}\n")
                f.write(f"{'=' * 80}\n\n")
                
                for job in logs['jobs']:
                    f.write(f"\n{'=' * 80}\n")
                    f.write(f"Job: {job['name']}\n")
                    f.write(f"{'=' * 80}\n")
                    f.write(f"Status: {job['status']}\n")
                    f.write(f"Conclusion: {job['conclusion']}\n\n")
                    
                    f.write(f"Steps:\n")
                    f.write(f"{'-' * 80}\n")
                    
                    for i, step in enumerate(job['steps'], 1):
                        f.write(f"\n{i}. {step['name']}\n")
                        f.write(f"   Status: {step['status']}\n")
                        f.write(f"   Conclusion: {step['conclusion']}\n")
            
            self.logger.info(f"Logs saved to: {log_file}")
            return str(log_file)
            
        except Exception as e:
            self.logger.error(f"Failed to extract logs for run {run_id}: {e}")
            return None
    
    def extract_all_logs(self, workflow_results):
        """Extract logs for all triggered workflows"""
        log_files = []
        
        for result in workflow_results:
            if result['success'] and result['run_id']:
                self.logger.info(f"Extracting logs for {result['service']}")
                
                log_file = self.extract_logs_to_file(
                    result['repo_name'],
                    result['run_id'],
                    result['service']
                )
                
                if log_file:
                    log_files.append({
                        'service': result['service'],
                        'log_file': log_file
                    })
        
        return log_files
