import xml.etree.ElementTree as ET
from deepdiff import DeepDiff
from utils.logger import setup_logger

class PomComparator:
    """
    Compare and update pom.xml files
    """
    
    def __init__(self, github_client, service_manager):
        self.logger = setup_logger("PomComparator")
        self.gh = github_client
        self.sm = service_manager
    
    def get_pom(self, repo_name, branch):
        """Get pom.xml content"""
        try:
            pom_path = self.sm.config['config_files']['pom']
            content, sha = self.gh.get_file_content(repo_name, pom_path, branch)
            
            if content:
                self.logger.info(f"Retrieved pom.xml from {repo_name}:{branch}")
                return content, sha
            
            return None, None
            
        except Exception as e:
            self.logger.error(f"Failed to get pom.xml from {repo_name}: {e}")
            return None, None
    
    def parse_pom(self, pom_content):
        """Parse pom.xml and extract key information"""
        try:
            root = ET.fromstring(pom_content)
            
            namespace = {'maven': 'http://maven.apache.org/POM/4.0.0'}
            
            dependencies = []
            deps_element = root.find('.//maven:dependencies', namespace)
            
            if deps_element is not None:
                for dep in deps_element.findall('maven:dependency', namespace):
                    group_id = dep.find('maven:groupId', namespace)
                    artifact_id = dep.find('maven:artifactId', namespace)
                    version = dep.find('maven:version', namespace)
                    
                    dep_info = {
                        'groupId': group_id.text if group_id is not None else '',
                        'artifactId': artifact_id.text if artifact_id is not None else '',
                        'version': version.text if version is not None else ''
                    }
                    dependencies.append(dep_info)
            
            properties = {}
            props_element = root.find('.//maven:properties', namespace)
            
            if props_element is not None:
                for prop in props_element:
                    prop_name = prop.tag.replace('{http://maven.apache.org/POM/4.0.0}', '')
                    properties[prop_name] = prop.text
            
            self.logger.info(f"Parsed pom.xml: {len(dependencies)} dependencies, {len(properties)} properties")
            
            return {
                'dependencies': dependencies,
                'properties': properties
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse pom.xml: {e}")
            return None
    
    def compare_poms(self, repo_name, branch1, branch2):
        """Compare pom.xml between two branches"""
        try:
            self.logger.info(f"Comparing pom.xml in {repo_name}: {branch1} vs {branch2}")
            
            pom1_content, _ = self.get_pom(repo_name, branch1)
            pom2_content, _ = self.get_pom(repo_name, branch2)
            
            if not pom1_content or not pom2_content:
                self.logger.error("Could not retrieve both pom.xml files")
                return None
            
            pom1_data = self.parse_pom(pom1_content)
            pom2_data = self.parse_pom(pom2_content)
            
            if not pom1_data or not pom2_data:
                return None
            
            diff = DeepDiff(pom1_data, pom2_data, ignore_order=True)
            
            comparison = {
                'has_differences': len(diff) > 0,
                'differences': dict(diff),
                'branch1': branch1,
                'branch2': branch2,
                'branch1_deps_count': len(pom1_data['dependencies']),
                'branch2_deps_count': len(pom2_data['dependencies'])
            }
            
            if comparison['has_differences']:
                self.logger.info(f"Found differences between {branch1} and {branch2}")
            else:
                self.logger.info(f"No differences found between {branch1} and {branch2}")
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Failed to compare pom.xml files: {e}")
            return None
    
    def compare_all_services(self, branch1, branch2):
        """Compare pom.xml for all services"""
        services = self.sm.get_all_services()
        
        results = []
        
        for service in services:
            self.logger.info(f"Comparing pom.xml for {service['name']}")
            
            comparison = self.compare_poms(
                service['repo_name'],
                branch1,
                branch2
            )
            
            if comparison:
                results.append({
                    'service': service['name'],
                    'comparison': comparison
                })
        
        return results
    
    def update_pom(self, repo_name, branch, new_pom_content, commit_message):
        """Update pom.xml in repository"""
        try:
            pom_path = self.sm.config['config_files']['pom']
            _, sha = self.get_pom(repo_name, branch)
            
            if not sha:
                self.logger.error(f"Cannot update pom.xml - file not found in {repo_name}:{branch}")
                return False
            
            success = self.gh.update_file(
                repo_name,
                pom_path,
                new_pom_content,
                branch,
                commit_message,
                sha
            )
            
            if success:
                self.logger.info(f"Updated pom.xml in {repo_name}:{branch}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update pom.xml: {e}")
            return False
