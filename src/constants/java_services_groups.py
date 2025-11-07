from enum import Enum

class JavaServicesGroups(Enum):
    JavaServicesGroups = "folder1"
    JavaServicesGroups1 = "folder2"
    JavaServicesGroups2 = "folder3"
    JavaServicesGroups3 = "folder4"

    @classmethod
    def java_list_values(cls):
        return [s.value for s in cls]