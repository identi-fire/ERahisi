import requests

def fetch_random_questions():
    api_url = "https://api.example.com/questions"  # Replace with the actual API endpoint
    response = requests.get(api_url)

    if response.status_code == 200:
        questions = response.json()  # Assuming the API returns JSON data
        return questions
    else:
        return None
