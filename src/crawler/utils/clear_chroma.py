import sys
from chroma_utils import clear_chroma_db

def main():
    if len(sys.argv) < 2:
        print("Usage: python clear_chroma.py <db_location> <university_name>")
        return
    db_location = sys.argv[1]
    university_name = sys.argv[2]
    clear_chroma_db(db_location, university_name)

if __name__ == "__main__":
    main()