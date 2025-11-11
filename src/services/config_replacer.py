import yaml
from pathlib import Path
from utils.logger import setup_logger

class ConfigReplacer:
    """
    Handles configuration file replacement
    """
    
    def __init__(self, github_client, service_manager):
        self.logger = setup_logger("ConfigReplacer")
        self.gh = github_client
        self.sm = service_manager
        self.templates_dir = Path("config/connection_templates")
    
    def load_template(self, template_name):
        """Load configuration template"""
        try:
            template_path = self.templates_dir / f"{template_name}.yml"
            
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            self.logger.info(f"Loaded template: {template_name}")
            return template_content
            
        except Exception as e:
            self.logger.error(f"Failed to load template {template_name}: {e}")
            return None
    
    def replace_config_file(self, repo_name, branch, file_path, new_content, commit_message):
        """Replace configuration file in repository"""
        try:
            existing_content, sha = self.gh.get_file_content(repo_name, file_path, branch)
            
            success = self.gh.update_file(
                repo_name,
                file_path,
                new_content,
                branch,
                commit_message,
                sha
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to replace config in {repo_name}: {e}")
            return False
    
    def apply_config_to_service(self, service, branch, config_type):
        """Apply specific configuration to a service"""
        try:
            template_content = self.load_template(config_type)
            if not template_content:
                return False
            
            config_files = self.sm.config['config_files']
            file_path = config_files['application']
            
            commit_message = f"Update configuration to {config_type} on {branch}"
            
            success = self.replace_config_file(
                service['repo_name'],
                branch,
                file_path,
                template_content,
                commit_message
            )
            
            if success:
                self.logger.info(f"Applied {config_type} config to {service['name']}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to apply config to {service['name']}: {e}")
            return False
    
    def apply_config_to_group(self, group_name, branch, config_type):
        """Apply configuration to entire service group"""
        services = self.sm.get_services_by_group(group_name)
        
        results = []
        
        for service in services:
            self.logger.info(f"Applying {config_type} to {service['name']}")
            
            success = self.apply_config_to_service(service, branch, config_type)
            
            results.append({
                'service': service['name'],
                'success': success
            })
        
        return results
