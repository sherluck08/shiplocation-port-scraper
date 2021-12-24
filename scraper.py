from bs4 import BeautifulSoup as BS
import requests
import pandas as pd
import pprint


def get_page_source_code(url):

    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Safari/537.3"
    }
    response = requests.get(url, headers=header)
    return BS(response.content, "html.parser")


def get_port_urls():
    page_num = 1
    port_urls = []
    while True:
        url = f"https://www.shiplocation.com/ports?page={page_num}&port=none&country=none"
        soup = get_page_source_code(url)
        print(url)
        if "Whoops, looks like something went wrong." not in soup.text:
            port_url = [url.get("href") for url in soup.select(".vessel_td a")]
            port_urls.extend(port_url)
            page_num += 1
        else:
            break
    return port_urls


def get_port_details():

    port_urls = get_port_urls()
    # port_urls = [
    #     "https://www.shiplocation.com/ports/LANSHAN/INFO/cn/type-Port",
    #     "https://www.shiplocation.com/ports/SHANGHAI/INFO/cn/type-Port",
    # ]
    results = []
    for url in port_urls:
        soup = get_page_source_code(url)
        name = soup.select_one("li:nth-of-type(1)").get_text(strip=True).split(":")[-1]
        country = soup.select_one("li:nth-of-type(2)").get_text(strip=True).split(":")[-1]
        location_type = soup.select_one("li:nth-of-type(3)").get_text(strip=True).split(":")[-1]
        un_locode = soup.select_one("li:nth-of-type(4)").get_text(strip=True).split(":")[-1]
        mmsi_mid_codes = soup.select_one("li:nth-of-type(5)").get_text(strip=True).split(":")[-1]
        latitude = soup.select_one("li:nth-of-type(8)").get_text(strip=True).split(":")[-1]
        longitude = soup.select_one("li:nth-of-type(8)").get_text(strip=True).split(":")[-1]

        columns = soup.select(".col-l-4")
        extended_info = " ".join([col.get_text(strip=True) for col in columns])
        headers = [c.text for col in columns for c in col.select("b")]

        for header in headers:
            extended_info = extended_info.replace(header, "@")

        splited_extended_info = [ext for ext in extended_info.split("@") if ext]
        extended_info_data = {header: ext_info for header, ext_info in zip(headers, splited_extended_info)}

        data = {
            "Name": name,
            "Country": country,
            "Location Type": location_type,
            "Un Locode": un_locode,
            "MMSI MID Codes": mmsi_mid_codes,
            "Latitude": latitude,
            "longitude": longitude,
        }

        data.update(extended_info_data)

        pprint.pprint(data)

        results.append(data)
    return results


def main():

    port_details = get_port_details()
    df = pd.DataFrame(port_details)
    filename = "ports.xlsx"
    df.to_excel(filename)


main()
