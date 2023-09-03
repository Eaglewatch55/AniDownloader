import custom_library.scrap_algorithm as scrap
from custom_library.db_query import Save_path, Updater
from platform import system
from pathlib import Path

#* SCAN AND DOWNLOAD SCRIPT
save_path = Save_path("Shows")
print(f"Descargando en {save_path.get_alias()}")
updater = Updater()
link_dict = {}
manager = scrap.Jd_manager()
emiting_shows = {s: True for s in updater.all_emiting_shows()}

for show in emiting_shows.keys():
    
    #* ADD EPISODE_LINK INSTANCE
    # GETS THE LATEST EPISODE NUMBER AND CALCULATES THE URL OF IT
    ep_url = show.get_list_url()
    
    episode_page = scrap.Episode_page(show, 300, 3)
    show.increase_episode()
    
    # VALIDATES THE WEBPAGE´S NEW EPISODE IS ONLINE
    if episode_page.ok():
        print(f"{show.get_alias()} episode {show.get_episode()} available")
        
    else:
        print(f"{show.get_alias()} episode {show.get_episode()} not available")
        emiting_shows[show] = False
        continue
    
  # SET SHOW´S SAVE PATH
    episode_save_path = f"{save_path.get_directory()}/{show.get_folder()}"     
    
    #* AWARE OF SERVER´S FOLDER AND JDOWNLOADER PATHS
    # CHECK OS AND FOLDER EXISTANCE
    if system() == "Linux":
        host_save_path = f"{save_path.get_host_directory()}/{show.get_folder()}"
        temp_path = Path(host_save_path)
        if not temp_path.exists():
            temp_path.mkdir()
    
    
    # Create each episode_page instance
    show = updater.get_show(show.get_alias())
    try:
        web_page = scrap.Episode_page(show)
    except ConnectionRefusedError as ex:
        print(f"{show.get_alias()} episode {show.get_episode()} not available")
        continue
    
    # Execute manager.download_episodes()
    manager.add_links(web_page, episode_save_path)

if not any(emiting_shows.values()) is True:
    print("No episodes available")
    exit()
    
try:
    # Add to downloads in JDownloader
    episdoes_ids = manager.download_episodes(episode_save_path)
except NameError as ex:
    print(ex)
    exit()
    
# Wait and validate download
episodes_ids = manager.download_validation(episdoes_ids, 20)

try:
    manager.disconnect()
except:
    print("Disconnection Failure")
    
#* Update show_db
for show in emiting_shows.keys():
    
    if emiting_shows[show]:
        print(show.get_alias())
        
        if episdoes_ids[show.get_alias()][2] == "Finished":
            updater.update_chapters(show)
            print(f"Download of {show.get_alias()} completed")
        
