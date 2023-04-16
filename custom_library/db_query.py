from tinydb import TinyDB, Query

#* DB CONFIG OBJECTS
class Save_path():
    
    def __init__(self, alias: str) -> None:
        self.path_profile = alias
        db_config = TinyDB ("config.json")
        save_path_table = db_config.table("save_path")
        data = Query()
        config = save_path_table.search(data.alias == alias)[0]
        self.directory_path = config["directory"]
        self.location = config["transmission"]
    
    def get_alias(self):
        return self.path_profile
    
    def get_directory(self):
        return self.directory_path
    
    def get_transmission(self):
        return self.location
    
    def __str__(self) -> str:
        return f"Alias: {self.get_alias()}\nDirectory: {self.get_directory()}\nTransmission: {self.get_transmission()}"
 
class Jd_config():
    def __init__(self) -> None:
        db_config = TinyDB ("config.json")
        dict_config = db_config.table("jdownloader").all()[0]
        self.email = dict_config["mail"]
        self.password = dict_config["pass"]
        self.dev_name = dict_config["device_name"]
    
    def get_mail(self):
        return self.email
    
    def get_pass(self):
        return self.password
    
    def get_device_name(self):
        return self.dev_name

#* DB SHOW QUERIES
class Show ():
    
    def __init__(self, alias: str, list_url: str, episode_number: int, folder: str, emission: bool) -> None:
        """
        Parameters:
            ----------
                alias: str 
                    alias of the show
                list_url: str
                    URL to episode´s list.
                episode_number: int 
                    Current episode number.
                folder: str
                    Name of the folder to store the videos.
                emission: bool
                    True if show still on emission.
                    False otherwise.
        """
        
        self.name = alias
        self.base_url = list_url
        self.latest_episode = episode_number
        self.folder_name = folder
        self.on_emission = emission
        
    
    def __str__(self) -> str:
        return f"Show: {self.get_alias()}\nList URL: {self.get_list_url()}\nCurrent Episode: {self.get_episode()}\nOn Emision: {self.get_emision_status()}\nFolder Name: {self.get_folder()}"
    
    def get_alias(self) -> str:
        return self.name
    
    def get_list_url(self) -> str:
        return self.base_url
    
    def get_episode(self) -> int:
        return self.latest_episode
    
    def get_folder(self) -> str:
        return self.folder_name
    
    def get_emision_status(self) -> str:
        return self.on_emission
    
    def set_alias(self, alias: str):
        self.name = alias
    
    def set_list_url(self, url: str):
        self.base_url = url
    
    def set_episode(self, episode: int):
        self.latest_episode = episode
    
    def increase_episode(self, episode: int):
        self.latest_episode += 1
        
    def set_folder(self, folder: str):
        self.folder_name = folder
    
    def set_emision_status(self, emision: bool):
        self.on_emission = emision


class Updater():
    
    def add_show (show: Show) -> None:
        """
            Parameters:
            ----------
            show: Show
                Show instance to add.
        """
        
        db_shows = TinyDB("show_db.json")
        db_shows.insert({"show": show.get_alias(), 
                        "current_episode": show.get_episode(), 
                        "list_url": show.get_list_url(),
                        "folder_name": show.get_folder(),
                        "status": show.get_emision_status()
                        })
    
    def get_show (alias: str) -> Show:
        """
            Parameters:
            ----------
            
            alias: str 
                Alias of the desired show.
            
            Returns:
            --------
                Show
                    A Show instance with the database information.
        """

        db_shows = TinyDB("show_db.json")
        data = Query()
        show_dict = db_shows.search(data.show == alias)[0]
        show = Show(alias = show_dict["show"],
                    list_url = show_dict["list_url"],
                    episode_number = show_dict["current_episode"], 
                    folder = show_dict["folder_name"],
                    emission = show_dict["status"])
        return show
    
    #! TO VALIDATE
    def update_chapter(show: Show):
        db_shows = TinyDB("show_db.json")
        data = Query()
        db_shows.update({"current_episode": show.get_episode()}, data.show == show.get_alias())


    def all_emiting_shows () -> list:
        """ 
            Returns:
            --------
                list
                    a list of Show instances that are on emission.
        """
        
        db_shows = TinyDB("show_db.json")
        list = db_shows.all()
        shows = []
    
        for element in list:
            if element["status"] == "Broadcasting":
                shows.append(Updater.get_show(element["show"]))

        return shows
                    
    