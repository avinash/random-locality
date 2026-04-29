import requests
from bs4 import BeautifulSoup
import json
import time


def scrape_mauritius_postcodes():
    url = "https://www.mauritiuspost.mu/find-your-post-code/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    session = requests.Session()

    try:
        # Step 1: GET the initial page to extract locality options and form field names
        print("Accessing main page...")
        response = session.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the dropdown select element
        select_element = soup.find("select")
        if not select_element:
            print("Error: Could not find the locality dropdown.")
            return

        select_name = select_element.get("name")
        options = select_element.find_all("option")

        all_data = {}

        # Step 2: Iterate through each main locality
        for option in options:
            locality_val = option.get("value")
            locality_text = option.text.strip()

            # Skip placeholder options (e.g., "Select Main Town")
            if not locality_val or "Main Town / Village" in locality_text:
                continue

            print(f"Processing: {locality_text}...")

            # Prepare the POST payload
            # Most forms also require the submit button value to trigger the logic
            payload = {select_name: locality_val, "submit": "Submit"}

            # Step 3: POST to get sub-localities
            post_response = session.post(url, data=payload, headers=headers)
            if post_response.status_code == 200:
                sub_soup = BeautifulSoup(post_response.text, "html.parser")

                # Step 4: Parse the results table
                # The site typically renders sub-localities in a table structure
                sub_localities = []
                results_table = sub_soup.find("table")

                if results_table:
                    rows = results_table.find_all("tr")
                    # Iterate through rows, skipping the header if it exists
                    for row in rows:
                        cells = row.find_all("td")
                        if len(cells) >= 2:
                            postcode = cells[0].text.strip()
                            sub_name = cells[1].text.strip()

                            # Filter out header text if caught in cells
                            if sub_name.lower() != "sub locality":
                                sub_localities.append(
                                    {"sub_locality": sub_name, "postcode": postcode}
                                )

                all_data[locality_text] = sub_localities

                # Respectful delay between requests
                time.sleep(0.5)
            else:
                print(f"Failed to fetch data for {locality_text}")

        # Step 5: Save the results to a JSON file
        with open("mauritius_localities.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)

        print("\nSuccess! Data saved to 'mauritius_localities.json'.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    scrape_mauritius_postcodes()
