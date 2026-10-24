from pathlib import Path
import json


MEMORY_FILE = Path("memory.json")


def load_memory():
    """Charge la mémoire depuis memory.json."""

    with open(MEMORY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_memory(memory):
    """Sauvegarde la mémoire."""

    with open(MEMORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            memory,
            file,
            ensure_ascii=False,
            indent=4
        )


def add_memory(memory, category, information):
    """Ajoute une information à la mémoire."""

    if category == "name":
        memory["user"]["name"] = information

    elif category == "preference":
        memory["user"]["preferences"].append(information)

    elif category == "interest":
        memory["user"]["interests"].append(information)

    elif category == "project":
        memory["projects"].append(information)

    elif category == "fact":
        memory["facts"].append(information)

    else:
        return False

    save_memory(memory)

    return True


def display_memory(memory):
    """Affiche toute la mémoire."""

    print("\n===== MA MÉMOIRE =====")

    print(f"\nNom : {memory['user']['name']}")

    print("\nPréférences :")
    for item in memory["user"]["preferences"]:
        print(f"- {item}")

    print("\nCentres d'intérêt :")
    for item in memory["user"]["interests"]:
        print(f"- {item}")

    print("\nProjets :")
    for item in memory["projects"]:
        print(f"- {item}")

    print("\nAutres informations :")
    for item in memory["facts"]:
        print(f"- {item}")

    print("\n======================\n")


def memory_to_text(memory):
    """Transforme la mémoire en texte utilisable par l'IA."""

    return f"""
Nom : {memory["user"]["name"]}

Préférences :
{chr(10).join("- " + item for item in memory["user"]["preferences"])}

Centres d'intérêt :
{chr(10).join("- " + item for item in memory["user"]["interests"])}

Projets :
{chr(10).join("- " + item for item in memory["projects"])}

Autres informations :
{chr(10).join("- " + item for item in memory["facts"])}
"""
def update_memory(memory, category, old_information, new_information):
    """Modifie une information existante."""

    if category == "name":

        memory["user"]["name"] = new_information

    elif category == "preference":

        if old_information in memory["user"]["preferences"]:
            index = memory["user"]["preferences"].index(old_information)
            memory["user"]["preferences"][index] = new_information
        else:
            return False

    elif category == "interest":

        if old_information in memory["user"]["interests"]:
            index = memory["user"]["interests"].index(old_information)
            memory["user"]["interests"][index] = new_information
        else:
            return False

    elif category == "project":

        if old_information in memory["projects"]:
            index = memory["projects"].index(old_information)
            memory["projects"][index] = new_information
        else:
            return False

    elif category == "fact":

        if old_information in memory["facts"]:
            index = memory["facts"].index(old_information)
            memory["facts"][index] = new_information
        else:
            return False

    else:
        return False

    save_memory(memory)

    return True


def delete_memory(memory, category, information):
    """Supprime une information de la mémoire."""

    information_lower = information.lower()

    # =========================
    # Nom
    # =========================

    if category == "name":

        if (
            memory["user"]["name"]
            and information_lower in memory["user"]["name"].lower()
        ):

            memory["user"]["name"] = ""

            save_memory(memory)

            return True

        return False


    # =========================
    # Catégories
    # =========================

    categories = {
        "preference": memory["user"]["preferences"],
        "interest": memory["user"]["interests"],
        "project": memory["projects"],
        "fact": memory["facts"]
    }


    # =========================
    # Chercher d'abord
    # dans la catégorie proposée
    # =========================

    if category in categories:

        items = categories[category]

        for item in items:

            if information_lower in item.lower():

                items.remove(item)

                save_memory(memory)

                return True


    # =========================
    # Si rien trouvé :
    # chercher partout
    # =========================

    for items in categories.values():

        for item in items:

            if information_lower in item.lower():

                items.remove(item)

                save_memory(memory)

                return True


    return False

def merge_memory(memory, category, old_informations, new_information):
    """Fusionne plusieurs souvenirs en un seul de manière sécurisée."""

    # Vérifier que le nouveau souvenir existe
    if not new_information or not new_information.strip():
        return False

    # =========================
    # Nom
    # =========================

    if category == "name":

        memory["user"]["name"] = new_information.strip()

        save_memory(memory)

        return True


    # =========================
    # Catégories
    # =========================

    categories = {
        "preference": memory["user"]["preferences"],
        "interest": memory["user"]["interests"],
        "project": memory["projects"],
        "fact": memory["facts"]
    }

    if category not in categories:
        return False


    items = categories[category]


    # =========================
    # Préparer la nouvelle mémoire
    # =========================

    new_items = []

    for item in items:

        should_remove = False

        for old_information in old_informations:

            if not old_information:
                continue

            old_lower = old_information.lower().strip()
            item_lower = item.lower().strip()

            if (
                old_lower in item_lower
                or item_lower in old_lower
            ):

                should_remove = True
                break

        if not should_remove:

            new_items.append(item)


    # =========================
    # Ajouter le souvenir fusionné
    # =========================

    new_items.append(
        new_information.strip()
    )


    # =========================
    # Remplacer la liste
    # =========================

    categories[category][:] = new_items


    # =========================
    # Sauvegarder
    # =========================

    save_memory(memory)

    return True


def find_exact_duplicates(memory):
    """Trouve les souvenirs strictement identiques."""

    duplicates = []

    categories = {
        "preference": memory["user"]["preferences"],
        "interest": memory["user"]["interests"],
        "project": memory["projects"],
        "fact": memory["facts"]
    }

    for category, items in categories.items():

        seen = set()

        for item in items:

            if item in seen:
                continue

            count = items.count(item)

            if count > 1:

                duplicates.append({
                    "category": category,
                    "information": item,
                    "count": count
                })

                seen.add(item)

    return duplicates

def find_memory_duplicates(memory):
    """Demande à Qwen de détecter les souvenirs qui parlent du même sujet."""

    from ollama import chat
    import json

    memory_text = f"""
Préférences :
{chr(10).join("- " + item for item in memory["user"]["preferences"])}

Centres d'intérêt :
{chr(10).join("- " + item for item in memory["user"]["interests"])}

Projets :
{chr(10).join("- " + item for item in memory["projects"])}

Autres informations :
{chr(10).join("- " + item for item in memory["facts"])}
"""

    prompt = f"""
Tu es un gestionnaire de mémoire.

Voici la mémoire actuelle :

{memory_text}

Analyse cette mémoire et cherche les souvenirs qui parlent
essentiellement du même sujet.

Deux souvenirs sont des doublons s'ils représentent la même
information ou le même sujet, même si leur formulation est différente.

Ne considère PAS comme doublons deux informations simplement
parce qu'elles utilisent certains mots similaires.

Pour chaque groupe de doublons, choisis une formulation courte
qui conserve les informations importantes.

Réponds UNIQUEMENT avec un JSON valide sous cette forme :

{{
    "duplicates": [
        {{
            "category": "project",
            "old_informations": [
                "souvenir 1",
                "souvenir 2"
            ],
            "new_information": "souvenir fusionné"
        }}
    ]
}}

S'il n'y a aucun doublon :

{{
    "duplicates": []
}}

IMPORTANT :
- old_informations doit contenir uniquement des souvenirs
  présents exactement dans la mémoire.
- Chaque souvenir doit apparaître UNE SEULE FOIS dans old_informations.
- Ne mets jamais deux fois exactement le même souvenir.
- Le nombre d'éléments dans old_informations doit correspondre
  au nombre de souvenirs distincts à fusionner.
- Ne crée aucun souvenir qui n'existe pas.
- Ne fusionne que les informations réellement liées.
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )

    try:

        result = json.loads(
            response.message.content
        )

        cleaned_duplicates = []

        for duplicate in result.get("duplicates", []):

            old_informations = duplicate.get(
                "old_informations",
                []
            )

            # Supprimer les répétitions exactes
            unique_informations = list(
                dict.fromkeys(old_informations)
            )

            # Un doublon sémantique doit contenir
            # au moins deux souvenirs différents.
            if len(unique_informations) < 2:
                continue

            duplicate["old_informations"] = unique_informations

            cleaned_duplicates.append(duplicate)

        result["duplicates"] = cleaned_duplicates

        return result

    except json.JSONDecodeError:

        return {
            "duplicates": []
        }

def clean_exact_duplicates(memory):
    """Supprime automatiquement les doublons strictement identiques."""

    categories = {
        "preference": memory["user"]["preferences"],
        "interest": memory["user"]["interests"],
        "project": memory["projects"],
        "fact": memory["facts"]
    }

    removed = 0

    for items in categories.values():

        seen = set()
        unique_items = []

        for item in items:

            if item in seen:
                removed += 1
                continue

            seen.add(item)
            unique_items.append(item)

        items[:] = unique_items

    if removed > 0:
        save_memory(memory)

    return removed