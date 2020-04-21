import os
from configparser import ConfigParser

import gspread
from oauth2client.service_account import ServiceAccountCredentials


class StringsDowser:

    def __init__(self):
        # Configure ConfigParser
        self.config = ConfigParser()
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        self.conf_path = os.path.join(curr_dir, 'conf')
        self.config.read(self.conf_path + os.path.sep + 'configuration.ini')

        # Read from local_ground section
        self.strings_sheet_url = self.config.get('local_ground', 'strings-sheet-url')
        self.api_key_file = self.config.get('local_ground', 'api-key-file')
        self.strings_sheet_index = self.config.get('local_ground', 'strings-sheet-index')
        self.strings_column_index = self.config.get('local_ground', 'strings-column-index')
        self.ground_directory = self.config.get('local_ground', 'ground-directory')
        self.water_extensions = self.config.get('local_ground', 'water-extensions')
        self.local_ground_scope = ['https://spreadsheets.google.com/feeds',
                                   'https://www.googleapis.com/auth/drive']
        self.local_ground_gs_credentials = ServiceAccountCredentials.from_json_keyfile_name(self.api_key_file,
                                                                                            self.local_ground_scope)

    '''Given a list of strings read from an input Google Spreadsheet, looks for these in a local directory with 
    respect to water_extensions. '''

    def divining_ground_water(self):
        gc = gspread.authorize(self.local_ground_gs_credentials)

        if self.local_ground_gs_credentials.access_token_expired:
            # refreshes the token
            gc.login()

        source_sheet = gc.open_by_url(self.strings_sheet_url)
        worksheet = source_sheet.get_worksheet(int(self.strings_sheet_index))
        strings_list = worksheet.col_values(int(self.strings_column_index) + 1)  # column index is 1-based
        extensions = [ext.strip() for ext in self.water_extensions.split(',')]

        # Get the list of all files in directory tree at given path
        list_of_files = self.get_list_of_files(self.ground_directory)

        tmp_occurrences = {}
        occurrences = set(tmp_occurrences)

        for file in list_of_files:
            name, ext = os.path.splitext(file)
            if ext in extensions:
                with open(file) as curr_file:
                    try:
                        content = curr_file.read()
                        for key in strings_list:
                            if key in content:
                                occurrences.add(key)
                    except UnicodeDecodeError as e:
                        print("Error in reading file {} - ".format(curr_file, str(e)))
            else:
                continue

        # TODO lambda
        for not_found in strings_list:
            if not_found not in occurrences:
                print(not_found)

    '''
        For the given path, get the list of all files in the directory tree
    '''

    def get_list_of_files(self, dir_name):
        # create a list of file and sub directories
        # names in the given directory
        list_of_file = os.listdir(dir_name)
        all_files = list()
        # Iterate over all the entries
        for entry in list_of_file:
            # Create full path
            full_path = os.path.join(dir_name, entry)
            # If entry is a directory then get the list of files in this directory
            if os.path.isdir(full_path):
                all_files = all_files + self.get_list_of_files(full_path)
            else:
                all_files.append(full_path)
        return all_files

    """ B-plan?
        
        for root, dirs, files in os.walk("/mydir"):
        for file in files:
        if file.endswith(".txt"):
             print(os.path.join(root, file))
    """


dowser = StringsDowser()
dowser.divining_ground_water()
