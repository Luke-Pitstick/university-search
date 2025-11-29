# https://www.stanford.edu/ -> stanford

base_url = "https://stanford.edu/"

university_name = base_url.replace("https://", "")
university_name = university_name.replace("www.", "")
university_name = university_name.replace("/", "")
university_name = university_name.replace(".edu", "")

print(university_name)
    
    
