from custom_library.db_query import Jd_config
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import myjdapi
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

                
class Episode_page(Scrap):
    def __init__(self, url: str, timeout: int = 5000, attempts: int = 3) -> None:
        super().__init__(url, timeout, attempts)
        
    def get_links(self) -> list:
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
                    r = session.get(self.get_url(), timeout = self.get_timeout())
                    #Busca tabla de descargas
                    download_table = r.html.find("#DwsldCn",first = True)
                    # El .links regresa variable tipo "set"
                    return list(download_table.links)
            except:
                if i == self.get_attempts():
                    raise ConnectionError("Connection Failed")
        return []
    
    
    def on_emision_status(self, list_url : str):
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
                    r = session.get(list_url, timeout=self.get_timeout())
                    r.html.render()
                    soup = BeautifulSoup(r.content, "lxml")
                    text = soup.find(class_="fa-tv").get_text()
                    
                    if text == "En emision":
                        return True
                    else:
                        return False
            except:
                if i == self.get_attempts():
                    raise ConnectionError("Connection Failed")
         
#* JDOWNLOAD MANAGMENT    
class Episode_links():
    def __init__(self, episode_name: str, show_path: str) -> None:
        self.ep_links = []
        self.ep_name = episode_name
        self.ep_path = show_path
        
    
    def __str__(self) -> str:
        return (f"URL: {self.get_urls()}\n"
                f"EP_NAME: {self.get_episode_name()}\n"
                f"PATH: {self.get_show_path()}")
    
    def add_url(self, url: str):
        self.ep_links.append(url)
    
    def get_urls(self):
        return self.ep_links

    def get_episode_name(self):
        return self.ep_name
    
    def get_show_path(self):
        return self.ep_path


class Jd_manager():
    def __init__(self, attempt_number = 3) -> None:
        self.config = Jd_config()
        self.links = []
        self.attempts = attempt_number
    
    def __str__(self) -> str:
        to_print = ""
        for episode in self.get_links():
            to_print += "-----------------------------\n"
            to_print += episode.__str__() + "\n"
        return to_print

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
                return to_return
            except:
                if except_func is not False:
                    self.attempt(except_func, "Exception handling", kwargs.values())
                    sleep(1)
                print(f"Attempt {i + 1} failed")
                pass
        return False
    
    def add_links(self, episode: Episode_links) -> None:
        self.links.append(episode)
    
    def get_links(self) -> Episode_links:
        return self.links
    
    def get_download_links(self, device) -> list:
        downloads = myjdapi.myjdapi.Downloads(device)
        return  downloads.query_links()
        
    def clear_downloads(self, device, delete_type = "DELETE_FINISHED"):
        downloads = myjdapi.myjdapi.Downloads(device)
        downloads.cleanup(action=delete_type, mode="REMOVE_LINKS_ONLY", selection_type="ALL")
        
    def clear_link_list(self, device, delete_type = "DELETE_OFFLINE"):
        linkgrabber = myjdapi.myjdapi.Linkgrabber(device)
        linkgrabber.cleanup(action=delete_type, mode="REMOVE_LINKS_ONLY", selection_type="ALL")

    def add_url(self, link, ep_name, folder, device) -> bool:
        linkgrab = myjdapi.myjdapi.Linkgrabber(device)
        linkgrab.add_links([{"autostart": False,
                      "links": link,
                      "packageName": ep_name,
                      "extractPassword": None,
                      "priority": "DEFAULT",
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
            linkgrab.move_to_downloadlist(link_ids = [grabber_links[0]["uuid"]], package_ids = [grabber_links[0]["packageUUID"]]) 
            return True
        
        else:
            
            print(f"Offline link: {link}")
            while linkgrab.get_package_count() > 0:
                # sleep(2)
                linkgrab.remove_links([grabber_links[0]["uuid"]] )
            return False

    def clear_jd(self, 
                 device = None,
                 cleartype_donwloads = False,
                 cleartype_links = False):
        """
        Clears the Linkcollector and/or the Downloads section of JDownloader.
        Creates an instance of Myjdapi if no device argument is recieved
        
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
        
        jd_temp = None
        if device is None:
            jd_temp = myjdapi.Myjdapi()
            jd_temp.set_app_key("EXAMPLE")
            jd_temp.connect(self.config.get_mail(), self.config.get_pass())
            device = jd_temp.get_device(self.config.get_device_name())
        
        if cleartype_donwloads is not False:
            self.clear_downloads(device, cleartype_donwloads)
        
        if cleartype_links is not False:
            self.clear_link_list(device, cleartype_links)
        
        if jd_temp is not None:
            jd_temp.disconnect()       
      
    def download_episodes(self):
        """
        Downloads all the videos from the Episode_links instances saved, checks the 
        status of the links within each instance and adds the first available to JDownloader.
        """
        # INITIALIZE JDOWNLOADER
        jd = myjdapi.Myjdapi()
        jd.set_app_key("EXAMPLE")
        if self.attempt(jd.connect,"Connecting to JDownloader API", self.config.get_mail(), self.config.get_pass()):
            device = jd.get_device(self.config.get_device_name())
            
            # STARTUP CLEANING SEQUENCE
            
            self.attempt(self.clear_downloads, "Startup cleanning sequence", device)
                    
            # EPISODE´S DOWNLOAD SEQUENCE
            for episode in self.get_links():
                
                downloaded_flag = False                    
                print(episode)
                
                # CHECKS IF THE FILE IS ALREADY IN JDOWNLOADER´S DOWNLOAD SECTION
                packages = self.attempt(self.get_download_links, "Checking download packages", device)
                
                for package in packages:
                    if f"{episode.get_episode_name()}.mp4" == package["name"]:
                        print("Already in downloads")
                        downloaded_flag = True
                    break
                        
                # EXITS ATTEMPT LOOP IF ALREADY ADDED
                if downloaded_flag is not True:
                    
                    #ADDS AND CHECKS ONLINE STATUS OF EACH LINK AVAILABLE
                    for url in episode.get_urls():
                        if self.attempt(self.add_url, 
                                        f"Adding {episode.get_episode_name()}",
                                        url, 
                                        episode.get_episode_name(),
                                        episode.get_show_path(),
                                        device,
                                        except_func=self.clear_jd,
                                        cleartype_links="DELETE_ALL", 
                                        device=device):
                            
                            print(f"Download added: {url}")
                            sleep(1)
                            break   #ADDS ONLY THE FIRST AVAILABLE LINK TO DOWNLOAD
                        
                        sleep(1)
            
            jd.disconnect()
            

        
        