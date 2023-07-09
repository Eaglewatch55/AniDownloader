from custom_library.db_query import Jd_config
from custom_library.db_query import Show
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import myjdapi
from pathlib import PosixPath
from time import sleep

#* WEB PAGE SCRAPPER        
class Scrap():
    def __init__(self, url: str, timeout: int = 5000, attempts: int = 3):
        """
        Parameters:
        ----------
            url: str 
                URL to scrap.
            timeout: int 
                Time to wait for connection.
            attempts: int 
                Number of connection attempts.
        """
        self.time = timeout
        self.link = url
        self.retrys = attempts
        
    def __str__(self) -> str:
        return f"URL: {self.get_url()}\n"
    
    def get_url(self):
        return self.link
    
    def get_timeout(self):
        return self.time
    
    def get_attempts(self):
        return self.retrys
    
    def ok(self):
        """
         Returns:
        --------
            Bool
                True if a web page is available, attempting to connect acording the attempt parameters.
                False otherwise.
        """
        for i in range(self.get_attempts()):
            try:
                with HTMLSession() as session:
                    r = session.get(self.get_url(),timeout=self.get_timeout())
                return r.ok
            except:
                if i == self.get_attempts():
                    raise ConnectionError("Connection Failed")

#! REVISAR 
class Episode_page(Scrap):
    def __init__(self, show: Show, timeout: int = 5000, attempts: int = 3) -> None:
        super().__init__(show.get_list_url(), timeout, attempts)
        self.name = show.get_alias()
        self.next_ep = show.get_episode() + 1
        self.ep_link = self.get_url().replace("/anime/","/ver/")+ "-" + str(show.get_episode() + 1)
        self.list_downloads = self.scrap_links()
        self.broadcast_status = self.get_emision_status()
        
    def __str__(self) -> str:
        return (super().__str__() + 
                f"Status: {self.get_emision_status()}\nEpisode link: {self.get_episode_link()}\nDownload links: {self.get_download_links()}")
    
    def get_alias(self):
        return self.name
    
    def get_episode_num(self):
        return self.next_ep
    
    def get_episode_link(self):
        return self.ep_link
    
    def get_download_links(self):
        return self.list_downloads
        
    def scrap_links(self) -> list:
        """
        Parameters:
        ----------
            anime_episode_url: str 
                URL to locate download links avaliable.
        
        Returns:
        --------
            list
                Returns a list of downloadable links in case of locating it succesfully.
                Returns an empty list otherwise.
        """
        
        for i in range(self.get_attempts()):
            try:
                with HTMLSession() as session:
                    r = session.get(self.get_episode_link(), timeout = self.get_timeout())
                    #Busca tabla de descargas
                    download_table = r.html.find("#DwsldCn",first = True)
                    # El .links regresa variable tipo "set"
                    down_list = list(download_table.links)
                    if len(down_list) == 0:
                        raise ConnectionRefusedError("Episode not available")
                    return down_list
            except:
                if i == self.get_attempts():
                    raise ConnectionError("Connection Failed")
        return []
    
    #! REVISAR
    def get_emision_status(self):
        """
        Parameters:
        ----------
            list_url: str 
                URL to the episode's list
        
        Returns:
        --------
            bool
                True if still on emision.
                False otherwise.
        """
        for i in range(self.get_attempts()):
            try:
                with HTMLSession() as session:
                    r = session.get(self.get_url(), timeout=self.get_timeout())
                    r.html.render()
                    soup = BeautifulSoup(r.content, "lxml")
                    text = soup.find(class_="AnmStts").get_text()
                    
                    if text == "En emision":
                        return True
                    else:
                        return False
            except:
                if i == self.get_attempts():
                    raise ConnectionError("Connection Failed")
        
         
#* JDOWNLOAD MANAGMENT    
class Jd_manager():
    def __init__(self, attempt_number = 3) -> None:
        self.config = Jd_config()
        self.links = []
        self.attempts = attempt_number
        
        self.jd = myjdapi.Myjdapi()
        self.jd.set_app_key("my_key")  
        
        if self.attempt(self.jd.connect,"Connecting to JDownloader API", self.config.get_mail(), self.config.get_pass()):
            self.device = self.jd.get_device(self.config.get_device_name())
        else:
            raise ConnectionError("Connection not available")
        
        # STARTUP CLEANING SEQUENCE
        self.attempt(self.clear_downloads, "Startup cleanning sequence")
    
    def __str__(self) -> str:
        to_print = ""
        for episode in self.get_links():
            to_print += "-----------------------------\n"
            
            for link in episode.get_download_links():
                to_print += " - " + link + "\n"
            
        return to_print

    def disconnect(self):
        self.jd.disconnect()
    
    def reconnect(self):
        self.jd = myjdapi.Myjdapi()
        self.jd.set_app_key("my_key")  
        
        if self.attempt(self.jd.connect,"Connecting to JDownloader API", self.config.get_mail(), self.config.get_pass()):
            self.device = self.jd.get_device(self.config.get_device_name())
        else:
            raise ConnectionError("Connection not available")                
        
    def get_attempt_number(self):
        return self.attempts
    
    
    def attempt(self, main_func, message: str, *args, except_func = False, **kwargs):
        """
        Attemps to execute the given function 'n' times according to the creation of 
        the class
        
        Parameters:
            main_func: function
                The function to execute
            message: str
                The message to display when attempting execution
            args
                Arguments for the function
            except_func: function
                Function to execute in case of an exception of main_func
            except_args
                Arguments of except_func
        """
        
        print(message)
        for i in range(self.get_attempt_number()):
            try:
                to_return = main_func(*args)
                sleep(1)
                return to_return
            except:
                if except_func is not False:
                    self.attempt(except_func, "Exception handling", kwargs.values())
                    sleep(1)
                print(f"Attempt {i + 1} failed")
        return False
    
    
    def add_links(self, episode: Episode_page) -> None:
        self.links.append(episode)
    
    
    def get_links(self) -> list[Episode_page]:
        return self.links
    
    
    def get_download_links(self) -> list:
        downloads = myjdapi.myjdapi.Downloads(self.device)            
        return  downloads.query_links()
    
    
    def clear_downloads(self, delete_type = "DELETE_FINISHED"):
        downloads = myjdapi.myjdapi.Downloads(self.device)
        downloads.cleanup(action=delete_type, mode="REMOVE_LINKS_ONLY", selection_type="ALL")
        
        
    def clear_link_list(self, delete_type = "DELETE_OFFLINE"):
        linkgrabber = myjdapi.myjdapi.Linkgrabber(self.device)
        linkgrabber.cleanup(action=delete_type, mode="REMOVE_LINKS_ONLY", selection_type="ALL")


    def add_url(self, link, ep_name, folder) -> bool:
        linkgrab = myjdapi.myjdapi.Linkgrabber(self.device)
        
        linkgrab.add_links([{"autostart": True,
                      "links": link,
                      "packageName": ep_name,
                      "extractPassword": None,
                      "priority": "HIGHEST",
                      "downloadPassword": None,
                      "destinationFolder": folder,
                      "overwritePackagizerRules": True
                          }])
        
        grabber_links = linkgrab.query_links()
        
        while len(grabber_links) == 0:
            sleep(1)
            grabber_links = linkgrab.query_links()
            
        # print(grabber_links)
        
        if grabber_links[0]["availability"] == "ONLINE":
            
            linkgrab.rename_link(grabber_links[0]["uuid"], f"{ep_name}.mp4")
            link_id = grabber_links[0]["uuid"]
            package_id = grabber_links[0]["packageUUID"]
            linkgrab.move_to_downloadlist(link_ids = [link_id], package_ids = [package_id]) 
            return True, link_id, package_id
        
        else:
            print(f"Offline link: {link}")
            while linkgrab.get_package_count() > 0:
                # sleep(2)
                linkgrab.remove_links([grabber_links[0]["uuid"]] )
            return False, False, False


    def clear_jd(self,
                 cleartype_donwloads = False,
                 cleartype_links = False):
        """
        Clears the Linkcollector and/or the Downloads section of JDownloader.
        
        Parameters
            device: str
                Name of the device.
            cleartype_donwloads: str
                Status of the links to delete in the Downloads section
                DELETE_ALL, DELETE_DISABLED, DELETE_FAILED, DELETE_FINISHED, DELETE_OFFLINE, DELETE_DUPE, DELETE_MODE
            cleartype_links: str
                Status of the links to delete in the Linkcollector section
                DELETE_ALL, DELETE_DISABLED, DELETE_FAILED, DELETE_FINISHED, DELETE_OFFLINE, DELETE_DUPE, DELETE_MODE
        """
        
        if cleartype_donwloads is not False:
            self.clear_downloads(self.device, cleartype_donwloads)
        
        if cleartype_links is not False:
            self.clear_link_list(self.device, cleartype_links)  
      
      
    def download_episodes(self, directory_path) -> dict[list]:
        """
        Downloads all the videos from the Episode_links instances saved, checks the 
        status of the links within each instance and adds the first available to JDownloader.
        """

        episodes_id = {}
        
        # ADDED TO GUARANTEE FIRST PRIORITY DOWNLOADS
        down_manager = myjdapi.myjdapi.DownloadController(self.device)
        self.attempt(down_manager.stop_downloads, "Stopping Downloads")
        
        # EPISODE´S DOWNLOAD SEQUENCE
        for episode in self.get_links():
            
            downloaded_flag = False                    
            # print(episode)
            
            # CHECKS IF THE FILE IS ALREADY IN JDOWNLOADER´S DOWNLOAD SECTION
            packages = self.attempt(self.get_download_links, "Checking download packages")
            
            for package in packages:
                if f"E{episode.get_episode_num()}.mp4" == package["name"]:
                    print("Already in downloads")
                    downloaded_flag = True
                break
                    
            # EXITS ATTEMPT LOOP IF ALREADY ADDED
            if downloaded_flag is not True:
                
                #ADDS AND CHECKS ONLINE STATUS OF EACH LINK AVAILABLE
                for url in episode.get_download_links():
                    status = False
                    
                    status, link_id, package_id = self.attempt(self.add_url, 
                                    f"Adding {episode.get_alias()}",
                                    url, 
                                    f"E{episode.get_episode_num()}",
                                    directory_path,
                                    except_func=self.clear_jd,
                                    cleartype_links="DELETE_ALL")
                    
                    if status:
                        print(f"Download added: {url}")
                        episodes_id[episode.get_alias()] = [link_id, episode.get_episode_num(), "Downloading"]
                        sleep(1)
                        break   #ADDS ONLY THE FIRST AVAILABLE LINK TO DOWNLOAD
 
                    sleep(1)
        
        return episodes_id
        
    def download_validation(self, episode_dict: dict[list], default_time) -> dict[list]:
        
        down_manager = myjdapi.myjdapi.DownloadController(self.device)
        self.attempt(down_manager.start_downloads, "Starting Downloads")
            
        def get_dict_index(dict_list:dict[list], index:int) -> list:
            """
                Takes a dictionary with a list as value and returns a list 
                of the given index of each list
            """
            
            return_list = []
            for key in dict_list.keys():
                return_list.append(dict_list[key][index])
            return return_list
        
                
        print(f"Initiating {len(episode_dict)} downloads")
        episodes_status = get_dict_index(episode_dict, 2)
        
        while any([True for i in episodes_status if i == "Downloading"]):
            # Gets JDownloader´s Donwload tab URLs
            down_list = self.attempt(self.get_download_links, "Getting download status")
            max_eta = 0
            
            if down_list is False:
                self.attempt(self.reconnect, "Attempting to reconnect")
                sleep(default_time)
                continue
            
            for package in down_list:
                # Checks each package for status finished
                uuid = package.get("uuid")
                
                print(uuid)
                print(f"Runing: {package.get('running')}")
                print(f"Status: {package.get('status')}")
                
                #Creates a tuple with status and name for validation of the current uuid.
                for episode in episode_dict.keys():
                    if episode_dict[episode][0] == uuid:
                        cond_uuid = (episode, True)
                        break
                    else:
                        cond_uuid = (episode, False)
                
                # package.get("bytesLoaded") == package.get("bytesTotal") and
                if cond_uuid[1] and package.get('status') == "Finished":
                    episode_dict[episode][2] = "Finished"
                
                # SET WAITING TIME GIVEN THE ESTIMATED TIME OF COMPLETION    
                elif package.get('speed') == 0:
                    print(f"Donwload {uuid} paused")
                    max_eta = max(default_time, max_eta)
                else:
                    max_eta = max(package.get("eta"), max_eta)

                episodes_status = get_dict_index(episode_dict, 2)
                
            if max_eta > 0:
                print(f"ETA: {max_eta}")
                sleep(max_eta)        
                    
        return episode_dict