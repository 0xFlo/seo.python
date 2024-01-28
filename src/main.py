# src/main.py:
from src.config_handler import ConfigReader, ConfigWriter
from src.api.google_api_service import GoogleAPIService

class ConsoleInterface:
    def __init__(self, api_service: GoogleAPIService, config_reader: ConfigReader, config_writer: ConfigWriter):
        self.api_service = api_service
        self.config_reader = config_reader
        self.config_writer = config_writer
        self.current_property = self.config_reader.get_selected_property()
        self.current_start_date = '2024-01-01'
        self.current_end_date = '2024-01-31'
        self.current_dimensions = ['query', 'page']
  
    def display_menu(self):
        menu = [
            "\033[1;32m1: Fetch GSC Data\033[0m",
            f"\033[1;32m2: Select and Update Property\033[0m (Current: \033[1;36m{self.current_property}\033[0m)",
            f"\033[1;32m3: Change Extraction Month\033[0m (Current: \033[1;36m{self.current_start_date} to {self.current_end_date}\033[0m)",
            f"\033[1;32m4: Toggle Dimensions\033[0m (Current: \033[1;36m{self.current_dimensions}\033[0m)",
            "\033[1;31mX: Exit\033[0m",
        ]
        print('\n'.join(menu))

    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your choice: ").strip().upper()

            if choice == '1':
                self.fetch_gsc_data()
            elif choice == '2':
                self.list_and_select_property()
            elif choice == '3':
                self.change_extraction_month()
            elif choice == '4':
                self.toggle_dimensions()
            elif choice == 'X':
                break
            else:
                print("\033[1;31mInvalid option! Try again.\033[0m")

    # Define methods here to handle each option
    # E.g., fetch_gsc_data, update_property, etc.
    
    def refresh_current_property(self):
        self.current_property = self.config_reader.get_selected_property()

    def list_and_select_property(self):
        sites = self.api_service.fetch_sites()
        sorted_sites = self.api_service.sort_sites(sites)
        self.api_service.select_and_save_property(sorted_sites, self.config_reader, self.config_writer)
        self.refresh_current_property()
        # Removed the redundant print statement here.

if __name__ == "__main__":
    config_reader = ConfigReader()
    config_writer = ConfigWriter()
    google_api_service = GoogleAPIService()

    interface = ConsoleInterface(google_api_service, config_reader, config_writer)
    interface.run()