import requests, os
def make_request(url,headers={}, params={}, json={}, request_type=requests.get):
    headers = {
        "Authorization": "Bearer " + os.getenv("CANVAS_TOKEN")
    }

    results = []  # To store all the data from paginated requests

    while url:
        response = request_type(url, headers=headers, params=params)
        
        # Check for a successful response
        if response.status_code == 200:
            data = response.json()
            # Append the data to results
            if isinstance(data, list):
                results.extend(data)
            else:
                results.append(data)

            # Parse the 'Link' header to find the next page URL
            link_header = response.headers.get('Link', '')
            next_url = None
            for part in link_header.split(','):
                if 'rel="next"' in part:
                    next_url = part[part.find('<') + 1:part.find('>')]
                    break
            url = next_url  # Update the URL for the next request
            params = {}  # Clear params for subsequent requests
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    return results
