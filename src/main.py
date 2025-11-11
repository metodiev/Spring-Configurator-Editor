import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.github_client import GitHubClient
from src.services.service_manager import ServiceManager
from src.services.config_replacer import ConfigReplacer
from src.services.pom_comparator import PomComparator
from src.services.workflow_manager import WorkflowManager
from src.utils.logger import setup_logger

class SpringConfigurator:
    """
    Main application for Spring configuration management
    """
    
    def __init__(self):
        self.logger = setup_logger("SpringConfigurator")
        
        try:
            self.gh_client = GitHubClient()
            self.service_mgr = ServiceManager(self.gh_client)
            self.config_replacer = ConfigReplacer(self.gh_client, self.service_mgr)
            self.pom_comparator = PomComparator(self.gh_client, self.service_mgr)
            self.workflow_mgr = WorkflowManager(self.gh_client, self.service_mgr)
            
            self.logger.info("Spring Configurator initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            sys.exit(1)
    
    def show_menu(self):
        """Display main menu"""
        print("\n" + "=" * 70)
        print(" " * 20 + "SPRING CONFIGURATOR EDITOR")
        print("=" * 70)
        print("\n Setup & Preparation:")
        print("  1. Create service folders structure")
        print("  2. Create branches for all services")
        print("\n Configuration Management:")
        print("  3. Replace configurations - Config Services Group")
        print("  4. Replace configurations - Client Services Group")
        print("  5. Replace configurations - All Services")
        print("\n POM Management:")
        print("  6. Compare pom.xml files (between branches)")
        print("  7. Compare pom.xml for all services")
        print("\n Workflow Management:")
        print("  8. Trigger workflows for all services")
        print("  9. Extract workflow logs")
        print("\n Automation:")
        print("  10. Run full automation (All steps)")
        print("\n Other:")
        print("  11. View configuration")
        print("  12. View logs directory")
        print("  0. Exit")
        print("=" * 70)
    
    def create_folders(self):
        """Step 1: Create folder structure"""
        print("\n[Step 1] Creating service folders...")
        print("-" * 70)
        
        success = self.service_mgr.create_service_folders()
        
        if success:
            print("\nFolders created successfully!")
            services = self.service_mgr.get_all_services()
            print(f"\nTotal services: {len(services)}")
            
            for group_name, group_data in self.service_mgr.config['service_groups'].items():
                print(f"\n{group_name}:")
                print(f"  Folder: {group_data['folder']}")
                print(f"  Services: {len(group_data['services'])}")
        else:
            print("\nFailed to create folders!")
    
    def create_branches(self):
        """Step 2: Create branches"""
        print("\n[Step 2] Creating branches for all services...")
        print("-" * 70)
        
        base_branch = self.service_mgr.config['branches']['base_branch']
        prefix = self.service_mgr.config['branches']['new_branch_prefix']
        
        print(f"\nBase branch: {base_branch}")
        
        branch_name = input(f"\nEnter new branch name (or press Enter for '{prefix}-{datetime.now().strftime('%Y%m%d')}'): ").strip()
        
        if not branch_name:
            branch_name = f"{prefix}-{datetime.now().strftime('%Y%m%d')}"
        
        print(f"\nCreating branch: {branch_name}")
        confirm = input("Proceed? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Cancelled")
            return
        
        results = self.service_mgr.create_branches_for_all(branch_name)
        
        success_count = sum(1 for r in results if r['success'])
        
        print(f"\nResults: {success_count}/{len(results)} branches created successfully")
        
        for result in results:
            status = "OK" if result['success'] else "FAILED"
            print(f"  [{status}] {result['service']}")
    
    def replace_config_group(self, group_name):
        """Replace configurations for a specific group"""
        print(f"\n[Config Replacement] {group_name}")
        print("-" * 70)
        
        services = self.service_mgr.get_services_by_group(group_name)
        
        if not services:
            print(f"No services found in group '{group_name}'")
            return
        
        print(f"\nServices in {group_name}: {len(services)}")
        for service in services:
            print(f"  - {service['name']}")
        
        print("\nAvailable configuration types:")
        print("  1. oracle")
        print("  2. snowflake")
        print("  3. postgres")
        print("  4. azure")
        
        config_type = input("\nEnter configuration type: ").strip().lower()
        
        if config_type not in ['oracle', 'snowflake', 'postgres', 'azure']:
            print("Invalid configuration type")
            return
        
        branch = input("Enter target branch: ").strip()
        
        if not branch:
            print("Branch name required")
            return
        
        print(f"\nApplying {config_type} configuration to {len(services)} services on branch '{branch}'")
        confirm = input("Proceed? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Cancelled")
            return
        
        results = self.config_replacer.apply_config_to_group(group_name, branch, config_type)
        
        success_count = sum(1 for r in results if r['success'])
        
        print(f"\nResults: {success_count}/{len(results)} configurations applied successfully")
        
        for result in results:
            status = "OK" if result['success'] else "FAILED"
            print(f"  [{status}] {result['service']}")
    
    def compare_poms(self):
        """Compare pom.xml files"""
        print("\n[POM Comparison]")
        print("-" * 70)
        
        branch1 = input("Enter first branch: ").strip()
        branch2 = input("Enter second branch: ").strip()
        
        if not branch1 or not branch2:
            print("Both branch names required")
            return
        
        print(f"\nComparing pom.xml files: {branch1} vs {branch2}")
        
        results = self.pom_comparator.compare_all_services(branch1, branch2)
        
        print(f"\nComparison complete: {len(results)} services")
        
        for result in results:
            comparison = result['comparison']
            
            if comparison['has_differences']:
                print(f"\n  {result['service']}: DIFFERENCES FOUND")
                print(f"    {branch1}: {comparison['branch1_deps_count']} dependencies")
                print(f"    {branch2}: {comparison['branch2_deps_count']} dependencies")
            else:
                print(f"\n  {result['service']}: No differences")
    
    def trigger_workflows(self):
        """Trigger workflows for all services"""
        print("\n[Workflow Trigger]")
        print("-" * 70)
        
        branch = input("Enter branch to trigger workflows on: ").strip()
        
        if not branch:
            print("Branch name required")
            return
        
        workflow_file = self.service_mgr.config['workflow']['workflow_file']
        
        print(f"\nWorkflow: {workflow_file}")
        print(f"Branch: {branch}")
        
        confirm = input("\nTrigger workflows for all services? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Cancelled")
            return
        
        results = self.workflow_mgr.trigger_all_workflows(branch)
        
        success_count = sum(1 for r in results if r['success'])
        
        print(f"\nResults: {success_count}/{len(results)} workflows triggered successfully")
        
        for result in results:
            if result['success']:
                print(f"  [OK] {result['service']} - Run ID: {result['run_id']}")
            else:
                print(f"  [FAILED] {result['service']}")
        
        self.last_workflow_results = results
    
    def extract_logs(self):
        """Extract workflow logs"""
        print("\n[Extract Logs]")
        print("-" * 70)
        
        if not hasattr(self, 'last_workflow_results'):
            print("\nNo recent workflow runs found. Trigger workflows first (option 8)")
            return
        
        print(f"\nExtracting logs for {len(self.last_workflow_results)} workflow runs...")
        
        log_files = self.workflow_mgr.extract_all_logs(self.last_workflow_results)
        
        print(f"\nExtracted {len(log_files)} log files:")
        
        for log_file_info in log_files:
            print(f"  {log_file_info['service']}: {log_file_info['log_file']}")
    
    def run_full_automation(self):
        """Run all steps in sequence"""
        print("\n[FULL AUTOMATION]")
        print("=" * 70)
        print("\nThis will execute all steps:")
        print("  1. Create folders")
        print("  2. Create branches")
        print("  3. Replace configs (Config services)")
        print("  4. Replace configs (Client services)")
        print("  5. Compare pom.xml files")
        print("  6. Trigger workflows")
        print("  7. Extract logs")
        print("\n" + "=" * 70)
        
        confirm = input("\nProceed with full automation? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Cancelled")
            return
        
        branch_name = input("\nEnter branch name: ").strip()
        config_type = input("Enter configuration type (oracle/snowflake/postgres/azure): ").strip().lower()
        
        if not branch_name or config_type not in ['oracle', 'snowflake', 'postgres', 'azure']:
            print("Invalid input")
            return
        
        print("\n" + "=" * 70)
        print("Starting full automation...")
        print("=" * 70)
        
        self.create_folders()
        
        input("\nPress Enter to continue to next step...")
        
        results = self.service_mgr.create_branches_for_all(branch_name)
        print(f"\nBranches created: {sum(1 for r in results if r['success'])}/{len(results)}")
        
        input("\nPress Enter to continue to next step...")
        
        for group_name in self.service_mgr.config['service_groups'].keys():
            print(f"\nApplying {config_type} to {group_name}...")
            results = self.config_replacer.apply_config_to_group(group_name, branch_name, config_type)
            print(f"Configs applied: {sum(1 for r in results if r['success'])}/{len(results)}")
        
        input("\nPress Enter to continue to next step...")
        
        base_branch = self.service_mgr.config['branches']['base_branch']
        results = self.pom_comparator.compare_all_services(base_branch, branch_name)
        print(f"\nPOM comparisons: {len(results)} services")
        
        input("\nPress Enter to continue to next step...")
        
        workflow_results = self.workflow_mgr.trigger_all_workflows(branch_name)
        print(f"\nWorkflows triggered: {sum(1 for r in workflow_results if r['success'])}/{len(workflow_results)}")
        
        self.last_workflow_results = workflow_results
        
        input("\nPress Enter to extract logs...")
        
        log_files = self.workflow_mgr.extract_all_logs(workflow_results)
        print(f"\nLogs extracted: {len(log_files)} files")
        
        print("\n" + "=" * 70)
        print("Full automation completed!")
        print("=" * 70)
    
    def view_configuration(self):
        """View current configuration"""
        print("\n[Configuration]")
        print("-" * 70)
        
        config = self.service_mgr.config
        
        print(f"\nOrganization: {config['organization']}")
        print(f"\nBranches:")
        print(f"  Base: {config['branches']['base_branch']}")
        print(f"  Compare: {config['branches']['compare_branch']}")
        print(f"  Prefix: {config['branches']['new_branch_prefix']}")
        
        print(f"\nService Groups:")
        for group_name, group_data in config['service_groups'].items():
            print(f"\n  {group_name}:")
            print(f"    Folder: {group_data['folder']}")
            print(f"    Services ({len(group_data['services'])}):")
            for service in group_data['services']:
                print(f"      - {service}")
    
    def view_logs(self):
        """View logs directory"""
        logs_dir = Path("logs")
        
        if not logs_dir.exists():
            print("\nNo logs directory found")
            return
        
        print("\n[Logs Directory]")
        print("-" * 70)
        
        log_files = list(logs_dir.rglob("*.log"))
        
        print(f"\nTotal log files: {len(log_files)}")
        
        for log_file in sorted(log_files, reverse=True)[:10]:
            size = log_file.stat().st_size
            print(f"  {log_file.name} ({size} bytes)")
        
        if len(log_files) > 10:
            print(f"\n  ... and {len(log_files) - 10} more")
    
    def run(self):
        """Main application loop"""
        while True:
            self.show_menu()
            
            try:
                choice = input("\nEnter your choice: ").strip()
                
                if choice == '0':
                    print("\nExiting Spring Configurator...")
                    break
                elif choice == '1':
                    self.create_folders()
                elif choice == '2':
                    self.create_branches()
                elif choice == '3':
                    self.replace_config_group('config_services')
                elif choice == '4':
                    self.replace_config_group('client_services')
                elif choice == '5':
                    for group_name in self.service_mgr.config['service_groups'].keys():
                        self.replace_config_group(group_name)
                elif choice == '6':
                    repo_name = input("Enter repo name (org/service): ").strip()
                    branch1 = input("Enter first branch: ").strip()
                    branch2 = input("Enter second branch: ").strip()
                    if repo_name and branch1 and branch2:
                        result = self.pom_comparator.compare_poms(repo_name, branch1, branch2)
                        if result:
                            print(f"\nHas differences: {result['has_differences']}")
                elif choice == '7':
                    self.compare_poms()
                elif choice == '8':
                    self.trigger_workflows()
                elif choice == '9':
                    self.extract_logs()
                elif choice == '10':
                    self.run_full_automation()
                elif choice == '11':
                    self.view_configuration()
                elif choice == '12':
                    self.view_logs()
                else:
                    print("\nInvalid choice. Please try again.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                self.logger.error(f"Error: {e}")
                print(f"\nError: {e}")
                input("\nPress Enter to continue...")

def main():
    """Entry point"""
    
    if not os.getenv("GITHUB_TOKEN"):
        print("ERROR: GITHUB_TOKEN not set")
        print("Run: setx GITHUB_TOKEN \"your_token\"")
        print("Then restart terminal")
        sys.exit(1)
    
    configurator = SpringConfigurator()
    configurator.run()

if __name__ == "__main__":
    main()
