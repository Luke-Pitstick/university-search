def add_university_name(config, base_url):
    university_name = base_url.replace("https://", "")
    university_name = university_name.replace("www.", "")
    university_name = university_name.replace("http://", "")
    university_name = university_name.replace("https://", "")
    university_name = university_name.replace("/", "")
    university_name = university_name.replace(".edu", "")
    university_name = university_name.replace(".com", "")
    university_name = university_name.replace(".org", "")
    university_name = university_name.replace(".net", "")
    university_name = university_name.replace(".gov", "")
    university_name = university_name.replace(".io", "")
    university_name = university_name.replace(".uk", "")
    university_name = university_name.replace(".ca", "")
    university_name = university_name.replace(".au", "")
    university_name = university_name.replace(".nz", "")
    university_name = university_name.replace("web.", "")
    config["UNIVERSITY_NAME"] = university_name
    return config