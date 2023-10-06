import json
import os


class Searches:

    @staticmethod
    def get_all_search_names() -> list[str]:
        return [
            filename.split('.')[0]
            for filename in os.listdir('backend/searches')
            if filename.endswith('.json')
        ]

    @staticmethod
    def get_search(name: str) -> dict:
        try:
            with open(f'backend/searches/{name}.json') as file:
                return json.load(file)
        except FileNotFoundError:
            return None

    @staticmethod
    def save_search(name: str, search: dict):
        with open(f'backend/searches/{name}.json', 'w') as file:
            json.dump(search, file)

    @staticmethod
    def delete_search(name: str):
        try:
            os.remove(f'backend/searches/{name}.json')
        except FileNotFoundError:
            pass
