import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.milvus_service import init_milvus, insert_documents, close_milvus

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

WIKICHESS_OPENINGS = [
    {
        "title": "Ouverture italienne",
        "opening_name": "Italienne",
        "source": "wikichess",
        "chunks": [
            "L'ouverture italienne commence par les coups 1.e4 e5 2.Cf3 Cc6 3.Fc4. C'est l'une des plus anciennes ouvertures connues, pratiquée depuis le XVIe siècle par les maîtres italiens. Le Fou vise la case f7, point faible de la position noire.",
            "Dans l'ouverture italienne, le Giuoco Piano (jeu tranquille) survient après 3...Fc5. Les Blancs peuvent jouer 4.c3 préparant d4 pour occuper le centre, ou 4.d3 pour un jeu plus calme et positionnel. Le Giuoco Piano est recommandé pour les débutants car il enseigne les principes fondamentaux du développement.",
            "L'attaque Evans dans l'italienne se caractérise par le sacrifice de pion 4.b4. Après 3...Fc5 4.b4 Fxb4 5.c3, les Blancs obtiennent un centre puissant et un développement rapide en échange du pion. Cette variante agressive fut popularisée par le capitaine William Evans au XIXe siècle.",
            "La défense des deux cavaliers 3...Cf6 est une réponse active à l'ouverture italienne. Les Noirs contre-attaquent immédiatement le pion e4. Après 4.Cg5, la position devient très tactique avec des variantes comme l'attaque Fegatello (5.Cxf7) ou la ligne principale 4...d5 5.exd5 Ca5.",
        ],
    },
    {
        "title": "Partie espagnole (Ruy Lopez)",
        "opening_name": "Espagnole",
        "source": "wikichess",
        "chunks": [
            "La partie espagnole ou Ruy Lopez commence par 1.e4 e5 2.Cf3 Cc6 3.Fb5. Inventée par le prêtre espagnol Ruy López de Segura au XVIe siècle, c'est l'une des ouvertures les plus jouées au plus haut niveau. Le Fou met la pression sur le cavalier qui défend le pion e5.",
            "La variante Morphy de la partie espagnole suit avec 3...a6 4.Fa4 Cf6 5.O-O. C'est la ligne principale moderne. Les Noirs chassent le Fou tout en préparant leur développement. Après 5...Fe7 6.Te1 b5 7.Fb3 d6 8.c3 O-O, on atteint la position de base de l'espagnole fermée.",
            "La défense berlinoise 3...Cf6 dans l'espagnole a été rendue célèbre par Vladimir Kramnik lors de son match contre Kasparov en 2000. Après 4.O-O Cxe4, la finale berlinoise qui en résulte est considérée comme très solide pour les Noirs malgré l'apparente simplicité de la position.",
            "La variante d'échange de l'espagnole 3...a6 4.Fxc6 dxc6 donne aux Blancs un avantage structural à long terme avec la meilleure structure de pions. Les Blancs visent une finale avantageuse. Bobby Fischer a utilisé cette variante avec succès à plusieurs reprises.",
        ],
    },
    {
        "title": "Défense sicilienne",
        "opening_name": "Sicilienne",
        "source": "wikichess",
        "chunks": [
            "La défense sicilienne 1.e4 c5 est la réponse la plus populaire et la plus combative à 1.e4. Les Noirs déséquilibrent immédiatement la position en évitant la symétrie. C'est l'ouverture qui produit statistiquement le plus de victoires pour les Noirs contre 1.e4.",
            "La variante Najdorf de la sicilienne se caractérise par 1.e4 c5 2.Cf3 d6 3.d4 cxd4 4.Cxd4 Cf6 5.Cc3 a6. Popularisée par Miguel Najdorf et perfectionnée par Bobby Fischer et Garry Kasparov, c'est l'une des variantes les plus analysées de l'histoire des échecs. Le coup a6 prépare b5 et contrôle la case b5.",
            "La variante Dragon de la sicilienne survient après 1.e4 c5 2.Cf3 d6 3.d4 cxd4 4.Cxd4 Cf6 5.Cc3 g6. Les Noirs fianchettent leur Fou en g7, créant une diagonale puissante. L'attaque yougoslave avec 6.Fe3 Fg7 7.f3 O-O 8.Dd2 Cc6 9.Fh6 mène à des positions extrêmement tranchantes.",
            "La sicilienne Scheveningen avec ...e6 et ...d6 offre aux Noirs une structure solide mais flexible. Les pions e6 et d6 forment un petit centre compact. Les Blancs peuvent lancer l'attaque Keres avec 6.g4 ou opter pour l'attaque anglaise avec 6.Fe2 suivi de f4.",
        ],
    },
    {
        "title": "Défense française",
        "opening_name": "Française",
        "source": "wikichess",
        "chunks": [
            "La défense française 1.e4 e6 est une ouverture solide où les Noirs préparent d5 pour contester le centre. Après 2.d4 d5, les Noirs ont un centre solide mais leur Fou de cases blanches est enfermé derrière la chaîne de pions, ce qui est le problème stratégique principal de cette défense.",
            "La variante d'avance de la française 3.e5 crée une chaîne de pions d4-e5. Les Noirs attaquent typiquement cette chaîne par c5 (attaque de la base) et f6 (attaque du sommet). Le plan classique noir est ...c5, ...Cc6, ...Db6 avec pression sur d4. La structure rappelle les positions de type Benoni inversé.",
            "La variante Winawer de la française 3.Cc3 Fb4 est une ligne agressive et complexe. Après 4.e5 c5 5.a3 Fxc3+ 6.bxc3, les Blancs ont la paire de Fous et un centre fort, mais une structure de pions abîmée. L'empoisonnement du pion avec 6...De7 7.Dg4 est une variante très théorique.",
            "La variante classique de la française avec 3.Cc3 Cf6 4.Fg5 est la ligne la plus ancienne. Après 4...Fe7 (ou 4...dxe4, la variante Burn), les Blancs maintiennent la tension au centre. La variante MacCutcheon 4...Fb4 est une alternative intéressante qui mène à des positions déséquilibrées.",
        ],
    },
    {
        "title": "Défense Caro-Kann",
        "opening_name": "Caro-Kann",
        "source": "wikichess",
        "chunks": [
            "La défense Caro-Kann 1.e4 c6 prépare 2...d5 pour contester le centre tout en gardant le Fou de cases blanches libre (contrairement à la Française). C'est une ouverture réputée solide, privilégiée par des joueurs positionnels comme Anatoly Karpov et Vishwanathan Anand.",
            "La variante d'avance de la Caro-Kann 3.e5 verrouille le centre. Les Noirs jouent typiquement 3...Ff5 (développant le Fou avant e6) suivi de e6, Cd7 et c5 pour attaquer le centre blanc. La structure résultante est similaire à la Française mais avec le Fou actif en f5.",
            "La variante classique de la Caro-Kann 3.Cc3 dxe4 4.Cxe4 Ff5 est la ligne principale. Après 5.Cg3 Fg6 6.h4 h6 7.Cf3 Cd7, les Noirs ont une position solide avec un bon Fou. Cette variante est considérée comme l'une des défenses les plus fiables contre 1.e4.",
            "L'attaque Panov de la Caro-Kann 3.exd5 cxd5 4.c4 transforme la partie en une structure de type Gambit Dame. Les Blancs cherchent à isoler le pion d5 noir. Après 4...Cf6 5.Cc3 e6, la position ressemble à une Défense Tarrasch du Gambit Dame avec des colonnes ouvertes au centre.",
        ],
    },
    {
        "title": "Gambit Dame",
        "opening_name": "Gambit Dame",
        "source": "wikichess",
        "chunks": [
            "Le Gambit Dame 1.d4 d5 2.c4 est l'une des ouvertures les plus classiques des échecs. Les Blancs proposent un pion en c4 pour détourner le pion d5 du centre. Ce n'est pas un vrai gambit car les Blancs peuvent toujours récupérer le pion. C'est le pilier des ouvertures fermées.",
            "Le Gambit Dame refusé (GQR) avec 2...e6 est la réponse la plus solide. Les Noirs maintiennent leur pion au centre mais enferment leur Fou de cases blanches. La variante orthodoxe continue avec 3.Cc3 Cf6 4.Fg5 Fe7 5.e3 O-O 6.Cf3 Cbd7. C'est une position riche en possibilités stratégiques.",
            "Le Gambit Dame accepté 2...dxc4 est parfaitement jouable. Les Noirs ne cherchent pas à garder le pion mais à se développer rapidement avec ...e6, ...c5, ...a6 et ...b5. Après 3.Cf3 Cf6 4.e3 e6, les Noirs ont une position saine et active.",
            "La défense slave 2...c6 dans le Gambit Dame protège d5 tout en gardant le Fou c8 libre. La variante semi-slave avec ...e6 crée une structure solide. Le gambit Meran (semi-slave avec ...dxc4 et ...b5) est l'une des lignes les plus riches de la théorie des ouvertures.",
        ],
    },
    {
        "title": "Défense indienne du Roi",
        "opening_name": "Indienne du Roi",
        "source": "wikichess",
        "chunks": [
            "La défense indienne du Roi (KID) se caractérise par 1.d4 Cf6 2.c4 g6 3.Cc3 Fg7. Les Noirs adoptent une approche hypermoderne : au lieu d'occuper le centre immédiatement, ils le contrôlent à distance avec le fianchetto du Fou en g7. C'est une ouverture dynamique et combative.",
            "Dans la variante classique de l'indienne du Roi, après 4.e4 d6 5.Cf3 O-O 6.Fe2 e5, les Noirs attaquent le centre. Si les Blancs ferment avec 7.d5, la lutte s'organise sur les deux ailes : les Noirs attaquent sur l'aile roi avec f5-f4, les Blancs sur l'aile dame avec c5.",
            "Le système Sämisch 4.e4 d6 5.f3 est une ligne agressive contre l'indienne du Roi. Les Blancs renforcent le centre et préparent Fe3 suivi éventuellement de Dd2 et O-O-O pour une attaque sur l'aile roi. Les Noirs répondent souvent par ...c5 ou ...e5.",
            "La variante des quatre pions de l'indienne du Roi avec 4.e4 d6 5.f4 est la réponse la plus ambitieuse. Les Blancs construisent un centre imposant mais celui-ci peut devenir une cible. Après 5...O-O 6.Cf3 c5, les Noirs minent le centre blanc.",
        ],
    },
    {
        "title": "Défense Pirc",
        "opening_name": "Pirc",
        "source": "wikichess",
        "chunks": [
            "La défense Pirc 1.e4 d6 2.d4 Cf6 3.Cc3 g6 est une ouverture hypermoderne où les Noirs fianchettent leur Fou de cases noires et laissent les Blancs occuper le centre. L'idée est de contre-attaquer ce centre plus tard. Elle porte le nom du grand maître yougoslave Vasja Pirc.",
            "Dans la Pirc, l'attaque autrichienne 4.f4 Fg7 5.Cf3 O-O est la réponse la plus agressive des Blancs. Avec les pions en e4, d4 et f4, les Blancs contrôlent un maximum d'espace. Les Noirs doivent trouver le bon moment pour frapper au centre avec ...c5 ou ...e5.",
        ],
    },
    {
        "title": "Ouverture anglaise",
        "opening_name": "Anglaise",
        "source": "wikichess",
        "chunks": [
            "L'ouverture anglaise 1.c4 est une ouverture de flanc flexible. Les Blancs contrôlent la case d5 sans engager immédiatement leur pion d. L'anglaise peut transposer dans de nombreuses ouvertures (Gambit Dame, Indienne du Roi inversée) et possède son propre système avec Cc3, g3 et Fg2.",
            "L'anglaise symétrique 1.c4 c5 crée une structure similaire à une sicilienne avec les couleurs inversées. Les Blancs ont un temps supplémentaire, ce qui leur donne un petit avantage. Après 2.Cf3 Cf6 3.g3 d5 4.cxd5 Cxd5, les Noirs obtiennent une position confortable.",
        ],
    },
    {
        "title": "Défense hollandaise",
        "opening_name": "Hollandaise",
        "source": "wikichess",
        "chunks": [
            "La défense hollandaise 1.d4 f5 est une ouverture ambitieuse où les Noirs visent à contrôler la case e4. Le mur de Stonewall avec ...d5, ...f5, ...e6, ...c6 crée une structure très solide mais limite le Fou de cases blanches. La variante Leningrad avec ...g6 et ...Fg7 est plus dynamique.",
            "Dans la hollandaise classique, après 1.d4 f5 2.c4 Cf6 3.g3 e6 4.Fg2 Fe7, les Noirs préparent un jeu sur l'aile roi. Le plan typique inclut ...d6, ...De8 suivi de ...Dh5 ou ...Dg6 pour une attaque directe sur le roi blanc.",
        ],
    },
]


def chunk_text(text: str, max_chunk_size: int = 500) -> list[str]:
    if len(text) <= max_chunk_size:
        return [text]

    sentences = text.replace(". ", ".|").split("|")
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


def main():
    logger.info("Initialisation de la connexion Milvus...")
    init_milvus()

    all_titles = []
    all_chunks = []
    all_sources = []
    all_opening_names = []

    for opening in WIKICHESS_OPENINGS:
        for chunk_text_raw in opening["chunks"]:
            sub_chunks = chunk_text(chunk_text_raw)
            for sub_chunk in sub_chunks:
                all_titles.append(opening["title"])
                all_chunks.append(sub_chunk)
                all_sources.append(opening["source"])
                all_opening_names.append(opening["opening_name"])

    logger.info("Nombre total de chunks à insérer : %d", len(all_chunks))

    count = insert_documents(
        titles=all_titles,
        chunks=all_chunks,
        sources=all_sources,
        opening_names=all_opening_names,
    )
    logger.info("Insertion terminée : %d documents insérés", count)

    close_milvus()
    logger.info("Script terminé avec succès")


if __name__ == "__main__":
    main()
