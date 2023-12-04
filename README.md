# BulkAssistantFileTool
 Upload files and create assistants based on an input file.

# Local Build
1. Create local environment:
    ´python3 -m venv venv´
2. Enter local environment:
    ´source venv/bin/activate´
3. Install Requirements.
    ´pip install -r requirements.txt´
4. Run main script (assumes user has provided files and config details):
    ´python3 main.py´




# Files & Directory:

- instructions.py - This is the general bot instructions that will be populated with the client/target instructions. 
- assistant_files/ - This directory holds all of the information the bots will use for retrival of information when operating. 
- DELETE_ALL_FILES_ASSISTANTS.py - CAUTION! Deletes everything from the org (assistants and files) 
- Assistant_config.csv - Provides names, file names, records output success of creation. 
