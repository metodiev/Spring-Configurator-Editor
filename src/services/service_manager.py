import json
import os
from pathlib import Path
from utils.logger import setup_logger

class ServiceManager:
    """
    Manages service organization and operations
    """
    
    def __init__(self, github_client, config_path="config/services_config.json"):
        self.logger = setup_logger("ServiceManager")
        self.gh = github_client
        self.config = self.load_config(config_path)
        self.base_dir = Path("workspace")
    
    def load_config(self, config_path):
        """Load services configuration"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self.logger.info(f"Loaded configuration from {config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return None
    
    def create_service_folders(self):
        """Create folder structure for service groups"""
        try:
            self.base_dir.mkdir(exist_ok=True)
            
            for group_name, group_data in self.config['service_groups'].items():
                folder_path = self.base_dir / group_data['folder']
                folder_path.mkdir(exist_ok=True)
                self.logger.info(f"Created folder: {folder_path}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create folders: {e}")
            return False
    
    def get_all_services(self):
        """Get all services from all groups"""
        all_services = []
        
        for group_name, group_data in self.config['service_groups'].items():
            for service in group_data['services']:
                all_services.append({
                    'name': service,
                    'group': group_name,
                    'folder': group_data['folder'],
                    'repo_name': f"{self.config['organization']}/{service}"
                })
        
        return all_services
    
    def create_branches_for_all(self, branch_name):
        """Create new branch for all services"""
        services = self.get_all_services()
        base_branch = self.config['branches']['base_branch']
        
        results = []
        
        for service in services:
            self.logger.info(f"Creating branch '{branch_name}' for {service['name']}")
            
            success = self.gh.create_branch(
                service['repo_name'],
                branch_name,
                base_branch
            )
            
            results.append({
                'service': service['name'],
                'success': success
            })
        
        return results
    
    def get_services_by_group(self, group_name):
        """Get services for specific group"""
        if group_name not in self.config['service_groups']:
            self.logger.error(f"Group '{group_name}' not found in config")
            return []
        
        group_data = self.config['service_groups'][group_name]
        services = []
        
        for service in group_data['services']:
            services.append({
                'name': service,
                'group': group_name,
                'folder': group_data['folder'],
                'repo_name': f"{self.config['organization']}/{service}"
            })
        
        return services
