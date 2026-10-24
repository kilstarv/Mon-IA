from pathlib import Path
import json

from ollama import chat

from memory import (
    load_memory,
    add_memory,
    update_memory,
    delete_memory,
    merge_memory,
    find_memory_duplicates,
    find_exact_duplicates,
    clean_exact_duplicates,
    display_memory
)

MODEL = "qwen3:8b"


# =========================
# Personnalité
# =========================

personality = Path(
    "personality.txt"
).read_text(encoding="utf-8")


# =========================
# Mémoire
# =========================

memory = load_memory()


def build_memory_context(memory):

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


# =========================
# Détection mémoire
# =========================

def detect_memory(user_message, memory):

    prompt = f"""
Tu es le gestionnaire de mémoire d'une IA personnelle.

=========================
MÉMOIRE ACTUELLE
=========================

{build_memory_context(memory)}

=========================
MESSAGE DE L'UTILISATEUR
=========================

{user_message}

=========================
TA MISSION
=========================

Analyse le message et décide si la mémoire doit être modifiée.

Tu peux choisir UNE action :

- none
- add
- update
- delete

=========================
NONE
=========================

Aucune modification nécessaire.

{{
    "action": "none",
    "category": "",
    "information": "",
    "old_informations": [],
    "new_information": ""
}}

=========================
ADD
=========================

Utilise add si l'information est nouvelle et qu'aucun
souvenir existant ne parle du même sujet.

{{
    "action": "add",
    "category": "interest",
    "information": "Information courte et durable",
    "old_informations": [],
    "new_information": ""
}}

=========================
UPDATE
=========================

Utilise update si l'information concerne un souvenir
existant.

Tu peux utiliser plusieurs souvenirs existants si
plusieurs parlent essentiellement du même sujet.

Exemple :

Mémoire :

- Création de mon IA personnelle
- L'utilisateur développe une IA avec Python et Ollama
- Developing a personal AI using Python and Ollama

Nouvelle information :

Je continue à développer mon IA avec Python et Ollama.

Tu dois alors fusionner les souvenirs.

Format :

{{
    "action": "update",
    "category": "project",
    "information": "",
    "old_informations": [
        "Création de mon IA personnelle",
        "L'utilisateur développe une IA avec Python et Ollama",
        "Developing a personal AI using Python et Ollama"
    ],
    "new_information": "Création de mon IA personnelle avec Python et Ollama"
}}

IMPORTANT :
old_informations doit contenir uniquement des souvenirs
qui existent réellement dans la mémoire.

=========================
DELETE
=========================

Utilise delete uniquement lorsque l'utilisateur indique
clairement qu'une information ne doit plus être conservée.

{{
    "action": "delete",
    "category": "interest",
    "information": "Minecraft",
    "old_informations": [],
    "new_information": ""
}}

=========================
RÈGLES
=========================

- Ne mémorise pas les questions ponctuelles.
- Ne mémorise pas les informations temporaires.
- Ne mémorise pas les détails banals.
- Ne mémorise pas les informations sensibles.
- Ne crée jamais de doublons.
- Compare toujours la nouvelle information avec TOUS les souvenirs existants.
- Deux souvenirs doivent être considérés comme des doublons
  s'ils concernent le même sujet, projet, préférence ou information
  durable, même si leur formulation est différente.
- Les différences de langue, de formulation ou de niveau de détail
  ne suffisent pas à considérer deux souvenirs comme différents.
- Si un nouveau souvenir apporte une précision à un souvenir existant,
  utilise update plutôt que add.
- Si plusieurs souvenirs existants concernent le même sujet,
  utilise update et place TOUS ces souvenirs dans old_informations.
- Pour update, fusionne les informations utiles dans un seul souvenir.
- Le nouveau souvenir doit conserver les informations importantes
  des anciens souvenirs sans répéter inutilement les mêmes choses.
- Pour update, old_informations doit contenir uniquement des souvenirs
  réellement présents dans la mémoire.
- Ne supprime jamais un souvenir simplement parce qu'il est similaire.
  Il faut qu'il représente réellement la même information ou le même sujet.
- Ne modifie pas la mémoire si le message n'apporte aucune information
  durable ou utile.

Réponds UNIQUEMENT avec un JSON valide.
"""

    response = chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"
    )

    try:

        return json.loads(
            response.message.content
        )

    except json.JSONDecodeError:

        return {
            "action": "none",
            "category": "",
            "information": "",
            "old_informations": [],
            "new_information": ""
        }


# =========================
# Prompt système
# =========================

memory_text = build_memory_context(
    memory
)


system_prompt = f"""
{personality}

Voici les informations actuellement présentes
dans ta mémoire :

{memory_text}

Utilise ces informations lorsqu'elles sont pertinentes.
"""


messages = [
    {
        "role": "system",
        "content": system_prompt
    }
]


# =========================
# Démarrage
# =========================

print("Mon IA est démarrée.")
print()
print("/help : Affiche les commandes disponibles.")
print()


# =========================
# Boucle principale
# =========================

while True:

    user_message = input("Toi > ")


    # =====================
    # Commandes
    # =====================

    if user_message.lower() == "/help":

        print("Commandes disponibles :")
        print()
        print("/help")
        print("/remember name <nom>")
        print("/remember preference <information>")
        print("/remember interest <information>")
        print("/remember project <information>")
        print("/remember fact <information>")
        print("/memory")
        print("/exit")
        print()

        continue


    # =====================
    # Quitter
    # =====================

    if user_message.lower() == "/exit":

        print("IA arrêtée.")

        break


    # =====================
    # Mémoire manuelle
    # =====================

    if user_message.startswith("/remember "):

        parts = user_message.split(" ", 2)

        if len(parts) < 3:

            print(
                "IA > Utilisation : "
                "/remember [categorie] [information]\n"
            )

            continue

        category = parts[1].lower()

        information = parts[2].strip()

        success = add_memory(
            memory,
            category,
            information
        )

        if success:

            print(
                "IA > Information enregistrée "
                "dans ma mémoire.\n"
            )

        else:

            print(
                "IA > Catégorie inconnue.\n"
            )

        continue


    # =====================
    # Afficher mémoire
    # =====================

    if user_message.lower() == "/memory":

        display_memory(memory)

        continue
    
    # =====================
    # Détecter les doublons
    # =====================

    if user_message.lower() == "/duplicates":

        print("\n[DEBUG] Recherche des doublons...")

        # =====================
        # Doublons exacts
        # =====================

        exact_duplicates = find_exact_duplicates(
            memory
        )

        print(
            "\n[DEBUG] Doublons exacts :"
        )

        print(
            json.dumps(
                exact_duplicates,
                ensure_ascii=False,
                indent=4
            )
        )

        # =====================
        # Nettoyage automatique
        # =====================

        removed = clean_exact_duplicates(
            memory
        )

        if removed > 0:

            print(
                f"\n[NETTOYAGE] {removed} doublon(s) exact(s) supprimé(s)."
            )

        else:

            print(
                "\n[NETTOYAGE] Aucun doublon exact à supprimer."
            )

        # =====================
        # Doublons sémantiques
        # =====================

        semantic_duplicates = find_memory_duplicates(
            memory
        )

        print(
            "\n[DEBUG] Doublons sémantiques :"
        )

        print(
            json.dumps(
                semantic_duplicates,
                ensure_ascii=False,
                indent=4
            )
        )

        print()

        continue

    # =====================
    # Détection automatique
    # =====================

    print("[DEBUG] Analyse de la mémoire...")

    memory_decision = detect_memory(
        user_message,
        memory
    )

    print(
        "[DEBUG] Décision mémoire :",
        memory_decision
    )


    action = memory_decision.get(
        "action",
        "none"
    )

    category = memory_decision.get(
        "category",
        ""
    )

    information = memory_decision.get(
        "information",
        ""
    )


    # =====================
    # Modification de la mémoire
    # =====================

    if action == "add":

        success = add_memory(
            memory,
            category,
            information
        )

        if success:

            print(
                f"\n[ Mémoire ] Information ajoutée : "
                f"{information}\n"
            )

        else:

            print(
                "\n[ Mémoire ] "
                "Impossible d'ajouter l'information.\n"
            )


    elif action == "update":

        old_informations = memory_decision.get(
            "old_informations",
            []
        )

        new_information = memory_decision.get(
            "new_information",
            ""
        )

        success = merge_memory(
            memory,
            category,
            old_informations,
            new_information
        )

        if success:

            print(
                "\n[ Mémoire ] Souvenirs fusionnés :"
            )

            for old_information in old_informations:

                print(
                    f"  - {old_information}"
                )

            print(
                "\n[ Mémoire ] Nouveau souvenir :"
            )

            print(
                f"  - {new_information}\n"
            )

        else:

            print(
                "\n[ Mémoire ] "
                "Impossible de fusionner les souvenirs.\n"
            )


    elif action == "delete":

        success = delete_memory(
            memory,
            category,
            information
        )

        if success:

            print(
                f"\n[ Mémoire ] Souvenir supprimé : "
                f"{information}\n"
            )

        else:

            print(
                "\n[ Mémoire ] "
                "Impossible de supprimer le souvenir.\n"
            )

    # =====================
    # Conversation avec Qwen
    # =====================

    messages.append({
        "role": "user",
        "content": user_message
    })


    # Actualiser la mémoire

    memory_text = build_memory_context(
        memory
    )

    messages[0] = {
        "role": "system",
        "content": f"""
{personality}

Voici les informations actuellement présentes
dans ta mémoire :

{memory_text}

Utilise ces informations lorsqu'elles sont pertinentes.
"""
    }


    print("[DEBUG] Envoi du message à Qwen...")


    response = chat(
        model=MODEL,
        messages=messages
    )


    answer = response.message.content


    messages.append({
        "role": "assistant",
        "content": answer
    })


    print(
        f"\nIA > {answer}\n"
    )