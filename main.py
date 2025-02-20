import re
import argparse
import json
from collections import defaultdict
from langdetect import detect, DetectorFactory

# Pour éviter que langdetect retourne des résultats non reproductibles
DetectorFactory.seed = 0


def hex_to_ascii(hex_string):
    """
    Convertit une chaîne hexadécimale en texte ASCII.
    """
    return bytes.fromhex(hex_string).decode('ascii', errors='ignore')


def extract_and_convert(bytecode, search_code="0033"):
    """
    Extrait la partie du bytecode après le code donné et la convertit en ASCII.
    """
    start_index = bytecode.find(search_code)
    if start_index == -1:
        print(f"Code '{search_code}' not found in the bytecode.")
        return None
    extracted_hex = bytecode[start_index + len(search_code):]
    return hex_to_ascii(extracted_hex)


def is_valid_language(text):
    """
    Vérifie si la chaîne détectée correspond à une langue valide.
    """
    text = text.strip("\x00")
    try:
        lang = detect(text)
        return lang in ["fr", "en", "it", "es", "de"]  # Ajoute d'autres langues si besoin
    except:
        return False


def analyze_solidity_bytecode(bytecode, search_terms, terms_def, filter_language=False):
    """
    Analyse du bytecode Solidity pour détecter l'instruction PUSH32 et vérifier si le contenu est une string.
    Si filter_language est True, on filtre les chaînes détectées avec langdetect.
    """
    bytecode = bytecode.lower().replace("0x", "")
    pattern = re.compile(r'7f([a-f0-9]{64})')  # PUSH32 a pour opcode 0x7f suivi de 32 octets
    matches = pattern.findall(bytecode)

    for match in matches:
        ascii_str = hex_to_ascii(match).strip("\x00")
        for term in search_terms:
            if ascii_str.startswith(term):  # Vérifie si la chaîne commence par un terme recherché
                if not filter_language or is_valid_language(ascii_str):
                    #print(f"\033[33mPolicy term found:\033[0m '{ascii_str}'")
                    terms_def[term].append(ascii_str)


if __name__ == "__main__":

    terms_def = defaultdict(list)  # Permet de stocker plusieurs occurrences d'un même terme

    parser = argparse.ArgumentParser(description="Extract and convert ASCII from Solidity bytecode")
    parser.add_argument("file_bytecode", help="The file containing the Solidity bytecode")
    parser.add_argument("file_json", help="The file containing the policy that must be respected")
    parser.add_argument("--filter-lang", action="store_true", help="Filter strings using langdetect")
    args = parser.parse_args()

    # Charger les termes depuis le fichier JSON
    with open(args.file_json, "r") as json_file:
        print(f"\033[33mPolicy loaded from {args.file_json}:\033[0m")
        json_data = json.load(json_file)
        search_terms = json_data.get("terms", [])

    # Ouvrir le fichier bytecode
    with open(args.file_bytecode, "r") as file:
        bytecode = file.read()

    # Analyse du bytecode pour trouver les chaînes correspondant aux termes du fichier JSON
    analyze_solidity_bytecode(bytecode, search_terms, terms_def, filter_language=args.filter_lang)

    # Extraction et conversion du bytecode
    ascii_result = extract_and_convert(bytecode, "0033")

    if ascii_result:
        #print()
        #print("\033[33mContent extract and convert into ASCII (>=32 characters):\033[0m")
        #print(ascii_result)
        array_splited = ascii_result.split("--")
        for elem in array_splited:
            for term in search_terms:
                if elem.startswith(term):
                    #print(f"\033[33mPolicy term found:\033[0m '{elem}'")
                    terms_def[term].append(elem)

    # Vérifier si tous les termes sont trouvés
    missing_terms = [term for term in search_terms if term not in terms_def]
    if missing_terms:
        print("\033[31mWarning: Not all terms were found in the bytecode.\033[0m")

    # Écriture des résultats dans un fichier JSON
    output_filename = f'output_{args.file_json}'
    with open(output_filename, 'w') as json_file:
        json.dump(terms_def, json_file, indent=4)
    print(f"\033[32mResults saved in {output_filename}\033[0m")
