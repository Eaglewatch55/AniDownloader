import custom_library.scrap_algorithm as scrap
from custom_library.db_query import Save_path, Updater

#* SCAN AND DOWNLOAD SCRIPT
save_path = Save_path("Shows")
print(f"Descargando en {save_path.get_alias()}")
updater = Updater()
link_dict = {}
manager = scrap.Jd_manager()
emiting_shows = updater.all_emiting_shows()

for show in emiting_shows:
    
    #* ADD EPISODE_LINK INSTANCE
    # GETS THE LATEST EPISODE NUMBER AND CALCULATES THE URL OF IT
    show.increase_episode()
    ep_url = show.get_list_url()
    
    episode_page = scrap.Episode_page(show , 300, 3)
    
    # VALIDATES THE WEBPAGE´S NEW EPISODE IS ONLINE
    if not episode_page.ok():
        print(f"{show.get_alias()} episode {show.get_episode()} not available")
        continue
    
    print(f"{show.get_alias()} episode {show.get_episode()} available")
    
    # SET SHOW´S SAVE PATH
    episode_save_path = f"{save_path.get_directory()}/{show.get_folder()}"
    
    #! UNCOMMENT WHEN PASSED TO LINUX SERVER
    #* AWARE OF SERVER´S FOLDER AND JDOWNLOADER PATHS
    
    # if not episode_save_path.is_dir():
    #     episode_save_path.mkdir()
    
    
    # Create each episode_page instance
    show = updater.get_show(show.get_alias())
    try:
        web_page = scrap.Episode_page(show)
    except ConnectionRefusedError as ex:
        print(f"{show.get_alias()} episode {show.get_episode()} not available")
        continue
    
    # Execute manager.download_episodes()
    manager.add_links(web_page)

# Add to downloads in JDownloader
episdoes_ids = manager.download_episodes(episode_save_path)

# Wait and validate download
episodes_ids = manager.download_validation(episdoes_ids, 20)

manager.disconnect()

#* Update show_db
for show in emiting_shows:
    print(show.get_alias())
    if episdoes_ids[show.get_alias()][2] == "Finished":
        updater.update_chapters(show)
        print(f"Download of {show.get_alias()} completed")
        
