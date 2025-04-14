import requests
import re
import json
import argparse

URL = "http://localhost:11434/api/generate"
MODEL = "gamebook"
context = []  # Na początku pusty, tablica liczb całkowitych.


# Funkcja wysyłająca zapytanie do API
def send_request(prompt, context):
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "context": context  # Przekazujemy kontekst jako tablicę
    }
    response = requests.post(URL, json=data)
    
    if response.status_code == 200:
        response_data = response.json()

        # Zaktualizuj kontekst z odpowiedzi
        return response_data["response"], response_data["context"]
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


# Funkcja parsująca tekst odpowiedzi
def parse_text(text):
    """
    Parsuje podany tekst w formacie opisu i opcji.
    
    Args:
        text (str): Tekst do parsowania.
        
    Returns:
        dict: Słownik zawierający opis ('description') oraz listę opcji ('options').
    """
    # Extract description
    description_match = re.search(r"(?=.*?)DESCRIPTION:\s*(.*?)(?=\nOPTIONS:|$)", text, re.DOTALL)
    description = description_match.group(1).strip() if description_match else "No description available"

    # Extract options
    options = re.findall(r"(\d+)\.\s(.+?)\s\[(\d+)[^0-9]+(\d+)[^\]]*\]", text)
    options_parsed = [
        {"option": int(opt[0]), "text": opt[1], "win": int(opt[2]), "lose": int(opt[3])}
        for opt in options
    ] if options else []

    return {
        "description": description,
        "options": options_parsed
    }


# Funkcja obsługująca rekurencję
def get_recursive_response(prompt, context=[], depth=1, max_depth=5, win_threshold=80, lose_threshold=80, leaf=False):
    # Pobierz odpowiedź od API
    response_text, context = send_request(prompt, context)
    result = parse_text(response_text)
    
    print(f"Depth: {depth}, Prompt: {prompt}")
    print(f"Response: {response_text}")
    
    result["context"] = context
    
    # Sprawdź warunek stopu
        # print(f"Stopping recursion at depth {depth}")
    if leaf:  # Jeśli flaga leaf jest ustawiona, przerywamy przetwarzanie
        return result # Przerwij pętlę, aby nie generować więcej zapytań

    for option in result["options"]:
        # Przygotuj prompt dla kolejnej iteracji
        option_prompt = f"{option['option']}"  # ": {option['text']}"
        
        # Sprawdź warunki zakończenia gry
        if option["win"] >= win_threshold:
            print(f"Option {option['option']} - Win condition met!")
            option_prompt = f"Select {option_prompt} and FINISH the game with just the DESCRIPTION of good ending"
            leaf = True
        elif option["lose"] >= lose_threshold or depth >= max_depth:
            print(f"Option {option['option']} - Lose condition met!")
            option_prompt = f"Select {option_prompt} and FINISH the game with just the DESCRIPTION of bad ending"
            leaf = True
        
        # Wywołanie rekurencyjne
        option["response"] = get_recursive_response(
            option_prompt,
            context,
            depth + 1,
            max_depth,
            win_threshold,
            lose_threshold,
            leaf
        )
    
    return result


# Obsługa argumentów z linii poleceń
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recursive Gamebook Generator")
    parser.add_argument("--prompt", required=True, help="Initial prompt to start the game")
    parser.add_argument("--max_depth", type=int, default=5, help="Maximum recursion depth")
    parser.add_argument("--win_threshold", type=int, default=80, help="Win condition threshold")
    parser.add_argument("--lose_threshold", type=int, default=80, help="Lose condition threshold")
    parser.add_argument("--output", type=str, default="output.json", help="Output file for the game tree")

    args = parser.parse_args()

    try:
        # Uruchomienie funkcji rekurencyjnej
        tree = get_recursive_response(
            prompt=args.prompt,
            max_depth=args.max_depth,
            win_threshold=args.win_threshold,
            lose_threshold=args.lose_threshold
        )

        # Zapisanie wyniku do pliku JSON
        with open(args.output, "w") as outfile:
            json.dump(tree, outfile, indent=4)

        print(f"Game tree saved to {args.output}")
    except Exception as e:
        print(f"Error: {e}")
