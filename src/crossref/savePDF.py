from urllib.request import urlopen

def main():
    download_file("https://onlinelibrary.wiley.com/doi/pdf/10.1002/asi.24226")

def download_file(download_url):
    response = urlopen(download_url)
    file = open("document.pdf", 'wb')
    file.write(response.read())
    file.close()
    print("Completed")

if __name__ == "__main__":
    main()