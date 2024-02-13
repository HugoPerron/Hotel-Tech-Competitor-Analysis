from bs4 import BeautifulSoup 
import requests
import pandas as pd

headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

search_query = 'site:https://secure.webrez.com' # Can replace with what ever you would like to search
results_per_page = 100 #Any number between 10-100 - maximum is 100
total_results = 1000 #In theory this can be larger than 300 but Google doesn't seem to show any more results past 300
current_results = 0
all_data = []

base_url = f'https://www.google.com/search?q={search_query}&num={results_per_page}'


def scrape_data(url):
    try:
        html = requests.get(url)
        html.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(html.text, 'html.parser')

        # Extract details below hotel name
        div_elements = soup.find_all('div', class_='p-t-3')
        details_1 = div_elements[0].text.strip() if div_elements else 'No details found'
        details_2 = div_elements[1].text.strip() if len(div_elements) > 1 else 'No details found'

        # Extract features & amenities
        label_elements = soup.find_all('label', class_='checkContainer m-b-0')
        features_amenities = [label.get_text(strip=True) for label in label_elements]

        return details_1, details_2, features_amenities

    except requests.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
        return 'Error', 'Error', []
    
    
while current_results < total_results:
    url = f"{base_url}&start={current_results}"
    html = requests.get(url, headers=headers)
    html.raise_for_status()  
    soup = BeautifulSoup(html.text, 'html.parser')
    allData = soup.find_all("div", {"class": "g"})

    for i in range(0, min(len(allData), results_per_page, total_results - current_results)):
        link = allData[i].find('a').get('href')

        if link is not None and (link.find('https') != -1 and link.find('http') == 0 and link.find('aclk') == -1):
            details_1, details_2, features_amenities = scrape_data(link)

            entry = {
                "link": link,
                "title": allData[i].find('h3', {"class": "DKV0Md"}).text if allData[i].find('h3', {"class": "DKV0Md"}) else None,
                "description": allData[i].find("div", {"class": "Hdw6tb"}).text if allData[i].find("div", {"class": "Hdw6tb"}) else None,
                "details_1": details_1,
                "details_2": details_2,
                "features_amenities": features_amenities
            }

            all_data.append(entry)

    current_results += results_per_page

df = pd.DataFrame(all_data)
df.to_excel("WebRezPro_hotels.xlsx", index=False)