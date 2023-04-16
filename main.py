import custom_library.scrap_algorithm as scrap
from custom_library.db_query import Save_path
from custom_library.db_query import Updater
from pathlib import Path

#! REVISAR LA FUNCIONALIDAD DE ESTATUS EMISION
#* SCAN AND DOWNLOAD SCRIPT
save_path = Save_path("Temp Descargas")
print(f"Descargando en {save_path.get_alias()}")

for show in Updater.all_emiting_shows():
    
    # GETS THE LATEST EPISODE NUMBER AND CALCULATES THE URL OF IT
    next_episode = show.get_episode() + 1
    ep_url = show.get_list_url().replace("/anime/","/ver/")+ "-" + str(next_episode)
    
    episode_page = scrap.Episode_page(ep_url, 300, 3)
    
    # VALIDATES THE WEBPAGE´S NEW EPISODE IS ONLINE
    if not episode_page.ok():
        print(f"{show.get_alias()} episodio {next_episode} no disponible")
        continue
    
    print(f"{show.get_alias()} episodio {next_episode} diponible")
    
    episode_save_path = Path(save_path.get_directory() + "/" + show.get_folder())
    
    if not episode_save_path.is_dir():
        episode_save_path.mkdir()
    
    episode_save_path = Path(str(episode_save_path) + f"/E{next_episode}.mp4")
    
    #! TERMINAR - AÑADIR LO DE TEST
    # for link in episode_page.get_links():
        
    #     try:
            
        
    #     except:
            

    #     if episode_save_path.is_file():
    #         print("Download completed")
    
        
    
    
    
    
    