import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os


class SheetAPI:

    def __init__(self, key_tb: str):
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        current_dir = os.path.dirname(__file__)
        credentials_path = os.path.join(current_dir, 'credentials.json')
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
        gc = gspread.authorize(credentials)
        self.spreadsheet = gc.open_by_key(key_tb)

    def read(self, list_name: str, range_tb: str) -> list:
        worksheet = self.spreadsheet.worksheet(list_name)
        cell_range = worksheet.range(range_tb)
        result = [item.value for item in cell_range]
        return result

    def write(self, list_name: str, range_tb: str, data: list) -> (bool, str):
        try:
            worksheet = self.spreadsheet.worksheet(list_name)
            worksheet.update(range_name=range_tb, values=data)
            return True, "Successfully"
        except Exception as e:
            return False, e


if __name__ == '__main__':
    print("Sheet repository api!")
