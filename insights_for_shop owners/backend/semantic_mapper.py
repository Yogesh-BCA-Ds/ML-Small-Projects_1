from backend.retail_ontology import RETAIL_ONTOLOGY
from backend.retail_validator import normalize_column_name

def get_semantic_targets(ontology):
    """
    Extract canonical semantic concepts
    from the existing retail ontology.
    """

    semantic_targets = {}

    for family, concepts in ontology.items():

        semantic_targets[family] = list(
            concepts.keys()
        )

    return semantic_targets


SEMANTIC_TARGETS = get_semantic_targets(
    RETAIL_ONTOLOGY
)

def find_known_synonym_matches(
    column_name,
    ontology
):
    normalized_column = normalize_column_name(
        column_name
    )

    candidates = []

    for family, concepts in ontology.items():

        for concept, synonyms in concepts.items():

            for synonym in synonyms:

                normalized_synonym = (
                    normalize_column_name(
                        synonym
                    )
                )

                if normalized_column == normalized_synonym:

                    candidates.append({
                        "family": family,
                        "concept": concept,
                        "matched_synonym": synonym
                    })

    return candidates
