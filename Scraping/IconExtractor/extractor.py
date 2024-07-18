import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_favicon_url(url):
    try:
        # Fetch HTML content of the webpage
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the favicon link tag
        favicon_tag = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')

        if favicon_tag:
            # Construct absolute URL if the favicon URL is relative
            favicon_url = favicon_tag['href']
            if not favicon_url.startswith('http'):
                favicon_url = urljoin(url, favicon_url)

            return favicon_url
        else:
            return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# Example usage
if __name__ == "__main__":
    website_url = "https://static-web-server.net/"  # Replace with the website URL you want to extract the favicon from
    favicon_url = extract_favicon_url(website_url)
    if favicon_url:
        print(f"The favicon URL of {website_url} is: {favicon_url}")
    else:
        print(f"Favicon not found on {website_url}")
