from models.npcverse_model import save_story_entry

def narrate_and_log(sender, receiver, message, response):
    entry = f"{sender} falou com {receiver}: \"{message}\".\n{receiver} respondeu: \"{response}\""
    save_story_entry(entry)
    return entry
