import requests
import json
import re
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get Canvas API token from environment variable
API_TOKEN = os.getenv("CANVAS_API_TOKEN")
if not API_TOKEN:
    print("Error: API token not found in .env file.")
    exit(1)

BASE_URL = "https://mylearn.torrens.edu.au/api/v1/"
COURSE_ID = 334  # Replace with the actual course ID

# Set up headers
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}"
}


def get_module_items_with_completion_requirements(module_id):
    url = f"{BASE_URL}courses/{COURSE_ID}/modules/{module_id}/items"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        items = json.loads(response.text)
        for item in items:
            if "completion_requirement" in item:
                completion_requirement = item["completion_requirement"]
                if completion_requirement:
                    print(f"  - Item: {item['title']}")
                    print(
                        f"    - Completion Requirement: {completion_requirement['type']}")


def set_must_view_requirements(module_id, module_number):
    url = f"{BASE_URL}courses/{COURSE_ID}/modules/{module_id}/items"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        items = json.loads(response.text)

        for suffix in ['Introduction', 'Resources', 'Activities']:
            item_name = f"Module {module_number} {suffix}"
            found = False

            for item in items:
                if item['title'] == item_name:
                    found = True
                    item_id = item['id']

                    update_url = f"{BASE_URL}courses/{COURSE_ID}/modules/{module_id}/items/{item_id}"

                    payload = {
                        'module_item[completion_requirement][type]': 'must_view'
                    }

                    update_response = requests.put(
                        update_url, headers=HEADERS, data=payload)

                    if update_response.status_code == 200:
                        print(
                            f"Successfully updated completion requirement for {item_name}.")
                    else:
                        print(
                            f"Failed to update {item_name}. Status code: {update_response.status_code}")
                        print(update_response.text)

            if not found:
                print(f"Error: Item named {item_name} not found in module.")


def get_modules():
    per_page = 100  # You can set this to be as large as the API allows
    page = 1
    while True:
        url = f"{BASE_URL}courses/{COURSE_ID}/modules?page={page}&per_page={per_page}"
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            modules = json.loads(response.text)

            if not modules:
                break  # Exit the loop if no more modules are returned

            for module in modules:
                if "Module" in module["name"]:
                    print(f"Module: {module['name']}")
                    get_module_items_with_completion_requirements(module['id'])

                    # Extract module number from the title
                    match = re.search(r'Module (\d+)', module['name'])
                    if match:
                        module_number = match.group(1)
                        set_must_view_requirements(module['id'], module_number)
                    else:
                        print("Couldn't extract module number from title.")

            page += 1  # Go to the next page
        else:
            print(
                f"Failed to get modules. Status code: {response.status_code}")
            print(response.text)
            break


if __name__ == "__main__":
    get_modules()
