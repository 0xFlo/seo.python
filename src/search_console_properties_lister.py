# src/search_console_properties_lister.py
import logging
from googleapiclient.discovery import build
from src.api.google_oauth2 import google_api_authentication
from src.config_handler import ConfigReader, ConfigWriter
from abc import ABC, abstractmethod

class GoogleAPIInterface(ABC):
    @abstractmethod
    def fetch_sites(self):
        pass

class GoogleAPIHandler(GoogleAPIInterface):
    def __init__(self, service):
        self.service = service

    def fetch_sites(self):
        try:
            return self.service.sites().list().execute().get('siteEntry', [])
        except Exception as e:
            logging.error("API request error: %s", e, exc_info=True)
            return []
        
class SiteListFormatter:
    @staticmethod
    def sort_sites(sites):
        return sorted(sites, key=lambda site: (not site["siteUrl"].startswith("sc-domain:"), site["siteUrl"].lower()))

class PropertyManager:
    def __init__(self, site_list, config_reader, config_writer):
        self.site_list = site_list
        self.config_reader = config_reader
        self.config_writer = config_writer

    def display_properties(self):
        selected_property = self.config_reader.get_selected_property() 
        for i, site in enumerate(self.site_list):
            site_url = site.get('siteUrl')
            prefix = "[Selected]" if site_url == selected_property else ""
            print(f"[{i}] {prefix} Site URL: {site_url}")

    def select_property(self):
        self.display_properties()
        choice = self.prompt_for_valid_choice()
        if choice is not None:
            self.config_writer.save_selected_property(self.site_list[choice].get('siteUrl'))

    def prompt_for_valid_choice(self):
        while True:
            choice = input("Select a property number: ")
            if choice.isdigit() and 0 <= int(choice) < len(self.site_list):
                return int(choice)
            print("Invalid selection. Please enter a valid number.")


def select_search_console_property():
    creds = google_api_authentication()
    if creds:
        service = build('webmasters', 'v3', credentials=creds, cache_discovery=False)
        api_handler = GoogleAPIHandler(service)
        sites = api_handler.fetch_sites()
        formatter = SiteListFormatter()
        sorted_sites = formatter.sort_sites(sites)
        config_reader = ConfigReader()
        config_writer = ConfigWriter()
        property_manager = PropertyManager(sorted_sites, config_reader, config_writer)
        return property_manager.get_formatted_sites()
    else:
        logging.error("Failed to authenticate with Google API.")
        return []

if __name__ == "__main__":
    select_search_console_property()