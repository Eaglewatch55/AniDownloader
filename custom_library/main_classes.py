class Show ():
    
    def __init__(self, alias: str, list_url: str, episode_number: int, folder: str, emision: bool) -> None:
        """
        Parameters:
            ----------
                alias: str 
                    alias of the show
                list_url: str
                    URL to episode´s list.
                episode_number: int 
                    Current episode number
                folder: str
                    Name of the folder to store the videos.
        """
        self.name = alias
        self.base_url = list_url
        self.episode = episode_number
        self.folder_name = folder
        self.on_emision = emision
        
    
    def __str__(self) -> str:
        return f"Show: {self.get_alias()}\nList URL: {self.get_list_url()}\nCurrent Episode: {self.get_episode()}\nOn Emision: {self.get_on_emision()}\nFolder Name: {self.get_folder()}"
    
    def get_alias(self) -> str:
        return self.name
    
    def get_list_url(self) -> str:
        return self.base_url
    
    def get_episode(self) -> int:
        return self.episode
    
    def get_folder(self) -> str:
        return self.folder_name
    
    def get_on_emision(self) -> str:
        return self.on_emision
    
    def _set_on_emision(self, emision: bool):
        self.on_emision = emision
