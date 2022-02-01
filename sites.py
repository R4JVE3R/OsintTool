import os
import json
import operator
import requests
import sys


class SiteInformation():
    def __init__(self, name, url_home, url_username_format, username_claimed,
                 username_unclaimed, information):

        self.name                = name
        self.url_home            = url_home
        self.url_username_format = url_username_format

        self.username_claimed    = username_claimed
        self.username_unclaimed  = username_unclaimed
        self.information         = information

        return

    def __str__(self):
        return f"{self.name} ({self.url_home})"


class SitesInformation():
    def __init__(self, data_file_path=None):
        jsonfile = open('./resources/data.json','r')
        site_data = json.load(jsonfile)
        self.sites = {}

        # Add all of site information from the json file to internal site list.
        for site_name in site_data:
            try:

                self.sites[site_name] = \
                    SiteInformation(site_name,
                                    site_data[site_name]["urlMain"],
                                    site_data[site_name]["url"],
                                    site_data[site_name]["username_claimed"],
                                    site_data[site_name]["username_unclaimed"],
                                    site_data[site_name]
                                   )
            except KeyError as error:
                raise ValueError(f"Problem parsing json contents at "
                                 f"'{data_file_path}':  "
                                 f"Missing attribute {str(error)}."
                                )

        return

    def site_name_list(self):
        site_names = sorted([site.name for site in self], key=str.lower)

        return site_names

    def __iter__(self):
        for site_name in self.sites:
            yield self.sites[site_name]

    def __len__(self):
        return len(self.sites)
