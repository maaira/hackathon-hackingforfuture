from octorest import OctoRest
def make_client(url, apikey):
     """Creates and returns an instance of the OctoRest client.

     Args:
         url - the url to the OctoPrint server
         apikey - the apikey from the OctoPrint server found in settings
     """
     try:
         client = OctoRest(url=url, apikey=apikey)
         return client
     except ConnectionError as ex:
         # Handle exception as you wish
         print(ex)