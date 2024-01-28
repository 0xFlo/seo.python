#src/api/google_api_service.py:
import logging
from googleapiclient.discovery import build
from src.api.google_oauth2 import google_api_authentication
from src.config_handler import ConfigReader, ConfigWriter

class GoogleAPIService:
    def __init__(self):
        self.creds = google_api_authentication()
        self.service = None
        if self.creds:
            self.service = build('webmasters', 'v3', credentials=self.creds, cache_discovery=False)

    def fetch_sites(self):
        if not self.service:
            logging.error("Google API Service is not initialized properly.")
            return []

        try:
            return self.service.sites().list().execute().get('siteEntry', [])
        except Exception as e:
            logging.error("API request error: %s", e, exc_info=True)
            return []

    def sort_sites(self, sites):
        return sorted(sites, key=lambda site: (not site["siteUrl"].startswith("sc-domain:"), site["siteUrl"].lower()))

    def select_and_save_property(self, site_list, config_reader: ConfigReader, config_writer: ConfigWriter):
        current_property = config_reader.get_selected_property()
        
        # Display the properties with color coding
        print("\033[1;34mHere are your sites:\033[0m")  # Blue color for the prompt
        # Add an option to go back to the main menu
        print("\033[1;31m0. Go back to the main menu\033[0m")  # Red color for '0: Go back'

        for i, site in enumerate(site_list, start=1):  # Start counting from 1
            site_url = site.get('siteUrl')
            # Apply color for the selected property, no color for others
            highlight = "\033[1;32m" if site_url == current_property else ""
            reset_highlight = "\033[0m" if site_url == current_property else ""
            print(f"{highlight}{i}. {site_url}{reset_highlight}")

        # Adjust the prompt for a valid choice to include the new '0' option
        choice = self.prompt_for_valid_choice(len(site_list) + 1)  # Include '0' in the count
        if choice == 0:
            return  # Returning None will go back to the main menu
        elif choice:
            selected_site_url = site_list[choice - 1].get('siteUrl')  # Adjust for the new indexing
            config_writer.save_selected_property(selected_site_url)
            print(f"\033[1;31mProperty updated to: {selected_site_url}\033[0m")  # Red color for confirmation

    @staticmethod
    def prompt_for_valid_choice(list_length):
        while True:
            choice = input("Select a property number: ")
            if choice.isdigit() and 0 <= int(choice) < list_length:
                return int(choice)
            print("\033[1;31mInvalid selection. Please enter a valid number.\033[0m")  # Red color for invalid input