"""Strings Dowser module"""
import os
from configparser import ConfigParser, NoOptionError
from pathlib import Path
import gspread
from oauth2client.service_account import ServiceAccountCredentials


class StringsDowser:
    """Strings dowser app logic"""

    def __init__(self):
        # Configure ConfigParser
        self.config = ConfigParser()
        self.curr_dir = Path(__file__).parent.resolve()
        # this is enough to tells how to define water and divine it
        self.config.read((self.curr_dir / 'test/conf' / 'configuration.ini').resolve())
        water_extensions = self.config.get('water_definition', 'water-extensions')
        self.extensions = [ext.strip() for ext in water_extensions.split(',')]

    def define_water(self):
        """Tries to define which kind of water needs to be divined. Two types of water available at
            the moment: Google Spreadsheet listing input strings or local txt file."""
        # Read from local_ground section
        ground_directory = self.config.get('local_ground', 'ground-directory')

        input_strings = []
        try:
            input_strings = self.gs_water_definition(input_strings)

        except NoOptionError:
            input_strings = self.local_water_definition(input_strings)
        # Get the list of all files in directory tree at given path
        input_files = self.get_list_of_files(ground_directory)
        return input_strings, input_files

    def gs_water_definition(self, input_strings):
        """Tries toread from Google Sheet water definition file."""
        strings_sheet_url = self.config.get('water_definition', 'strings-sheet-url')
        if strings_sheet_url:
            # Read from water_definition section
            api_key_file = self.config.get('water_definition', 'api-key-file')
            local_ground_scope = ['https://spreadsheets.google.com/feeds',
                                  'https://www.googleapis.com/auth/drive']
            local_ground_gs_credentials = ServiceAccountCredentials.from_json_keyfile_name(
                api_key_file,
                local_ground_scope)

            gsheet_credentials = gspread.authorize(local_ground_gs_credentials)
            if local_ground_gs_credentials.access_token_expired:
                # refreshes the token
                gsheet_credentials.login()

            strings_sheet_index = self.config.get('water_definition', 'strings-sheet-index')
            strings_column_index = self.config.get('water_definition', 'strings-column-index')
            source_sheet = gsheet_credentials.open_by_url(strings_sheet_url)
            worksheet = source_sheet.get_worksheet(int(strings_sheet_index))
            input_strings = worksheet.col_values(
                int(strings_column_index) + 1)  # column index is 1-based
        return input_strings

    def local_water_definition(self, input_strings):
        """Tries to read from local water definition file"""
        water_file_conf = self.config.get('water_definition', 'water-file')
        base_path = Path(__file__).parent
        water_file_path = (base_path / water_file_conf).resolve()
        with open(water_file_path) as water_file:
            try:
                input_strings = water_file.read().splitlines()
            except UnicodeDecodeError as ude:
                print("Error in reading file {} - ".format(water_file_path), str(ude))
            except BaseException as bae:
                raise Exception(
                    "Unable to understand what to divine. Caused by {}".format(str(bae)))
        return input_strings

    def divining_ground_water(self, input_strings, input_files):
        """Given a list of strings, looks for these in a local directory with respect to water
            definition and return not divined."""
        tmp_occurrences = {}
        occurrences = set(tmp_occurrences)

        for file in input_files:
            ext = os.path.splitext(file)
            if ext[1] in self.extensions:
                with open(file) as curr_file:
                    try:
                        content = curr_file.read()
                        for key in input_strings:
                            if key in content:
                                occurrences.add(key)
                    except UnicodeDecodeError as ude:
                        print("Error in reading file {} - ".format(curr_file), str(ude))
            else:
                continue

        not_found_list = []
        for not_found in input_strings:
            if not_found not in occurrences:
                not_found_list.append(not_found)
        print('\n'.join(map(str, not_found_list)))
        return not_found_list

    def get_list_of_files(self, dir_name):
        """" For the given path, get the list of all files in the directory tree """
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


DOWSER = StringsDowser()
STRINGS_LIST, LIST_OF_FILES = DOWSER.define_water()
DOWSER.divining_ground_water(STRINGS_LIST, LIST_OF_FILES)
