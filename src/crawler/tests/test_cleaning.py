from trafilatura import fetch_url, extract, html2txt, extract_metadata

# grab a HTML file to extract data from
downloaded = fetch_url('https://www.stanford.edu')
metadata = extract_metadata(downloaded)
# output main content and comments as plain text
result1 = extract(downloaded)
result2 = html2txt(downloaded)
print("--------------------------------")
print("result1")
print(result1)
print("--------------------------------")
print("result2")
print(result2)
print("--------------------------------")
print("metadata")
print(metadata)
print("--------------------------------")