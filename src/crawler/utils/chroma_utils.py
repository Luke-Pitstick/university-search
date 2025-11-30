import os
import shutil

def clear_chroma_db(db_location):
    if os.path.exists(db_location):
        shutil.rmtree(db_location)
    