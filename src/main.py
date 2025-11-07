import sys
from pathlib import Path
from utils.logger import setup_logger

def main():
    logger = setup_logger("MainApp")
    logger.info("Starting the application")
    print("Starting the application")
    

if __name__ == "__main__":
    main()