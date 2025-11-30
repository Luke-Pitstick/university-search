def add_university_name(config, base_url):
    university_name = base_url.replace("https://", "")
    university_name = university_name.replace("www.", "")
    university_name = university_name.replace("/", "")
    university_name = university_name.replace(".edu", "")
    
    config["settings"]["UNIVERSITY_NAME"] = university_name