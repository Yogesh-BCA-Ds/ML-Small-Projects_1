from backend.retail_ontology import RETAIL_ONTOLOGY
from backend.retail_validator import normalize_column_name
from rapidfuzz import fuzz
from backend.retail_validator import detect_observed_datatype

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

# ============================================================

def tokenize_column_name(column_name):
    """
    Split a normalized column name into individual tokens.
    """

    normalized_column = normalize_column_name(
        column_name
    )

    return normalized_column.split("_")


def find_token_matches(
    column_name,
    ontology
):
    """
    Find semantic concepts whose known synonyms
    contain tokens appearing in the column name.
    """

    tokens = tokenize_column_name(
        column_name
    )

    candidates = []

    for family, concepts in ontology.items():

        for concept, synonyms in concepts.items():

            matched_tokens = set()

            for synonym in synonyms:

                normalized_synonym = (
                    normalize_column_name(
                        synonym
                    )
                )

                synonym_tokens = set(
                    normalized_synonym.split("_")
                )

                matched = (
                    set(tokens)
                    & synonym_tokens
                )

                matched_tokens.update(
                    matched
                )

            if matched_tokens:

                candidates.append({
                    "family": family,
                    "concept": concept,
                    "matched_tokens": list(
                        matched_tokens
                    )
                })

    return candidates

def find_fuzzy_matches(
    column_name,
    ontology,
    threshold=70
):
    """
    Find semantic concepts that are similar
    to the uploaded column name.

    Unlike Phase 3, this function keeps
    the similarity score.
    """

    normalized_column = normalize_column_name(
        column_name
    )

    candidates = []

    if len(normalized_column) < 4:
        return candidates

    for family, concepts in ontology.items():

        for concept, synonyms in concepts.items():

            for synonym in synonyms:

                normalized_synonym = (
                    normalize_column_name(
                        synonym
                    )
                )

                if len(normalized_synonym) < 4:
                    continue

                similarity = fuzz.ratio(
                    normalized_column,
                    normalized_synonym
                )

                if similarity >= threshold:

                    candidates.append({
                        "family": family,
                        "concept": concept,
                        "matched_synonym": synonym,
                        "similarity": similarity
                    })

    return candidates

CONCEPT_DATATYPE_RULES = {

    "quantity": {"numeric"},
    "unit_price": {"numeric"},
    "total_amount": {"numeric"},
    "revenue": {"numeric"},
    "order_value": {"numeric"},

    "age": {"numeric"},
    "income": {"numeric"},

    "transaction_date": {"date"},
    "purchase_date": {"date"},
    "order_date": {"date"},
    "invoice_date": {"date"},
    "sale_date": {"date"},
}


def get_datatype_support(
    concept,
    observed_datatype
):
    """
    Check whether the observed datatype is
    compatible with a semantic concept.
    """

    expected_datatypes = CONCEPT_DATATYPE_RULES.get(
        concept
    )

    if expected_datatypes is None:
        return None

    return observed_datatype in expected_datatypes


def add_datatype_evidence(
    candidates,
    column_profile
):
    """
    Add datatype compatibility evidence
    to semantic candidates.
    """

    observed_datatype = detect_observed_datatype(
        column_profile
    )

    for candidate in candidates:

        concept = candidate["concept"]

        support = get_datatype_support(
            concept,
            observed_datatype
        )

        candidate["observed_datatype"] = (
            observed_datatype
        )

        candidate["datatype_support"] = support

    return candidates

def collect_value_characteristics(column_profile):
    """
    Extract generic characteristics of the actual values
    in a column.

    These characteristics do not assume a particular dataset
    or a fixed list of possible values.
    """

    characteristics = {}

    # Numeric-like values
    numeric_like_ratio = column_profile.get(
        "numeric_like_ratio"
    )

    if numeric_like_ratio is not None:
        characteristics["numeric_like_ratio"] = (
            numeric_like_ratio
        )

    # Date-like values
    date_like_ratio = column_profile.get(
        "date_like_ratio"
    )

    if date_like_ratio is not None:
        characteristics["date_like_ratio"] = (
            date_like_ratio
        )

    # Integer-like values
    integer_like_ratio = column_profile.get(
        "integer_like_ratio"
    )

    if integer_like_ratio is not None:
        characteristics["integer_like_ratio"] = (
            integer_like_ratio
        )

    # Digit-only values
    digit_only_ratio = column_profile.get(
        "digit_only_ratio"
    )

    if digit_only_ratio is not None:
        characteristics["digit_only_ratio"] = (
            digit_only_ratio
        )

    # Alphabetic values
    alpha_only_ratio = column_profile.get(
        "alpha_only_ratio"
    )

    if alpha_only_ratio is not None:
        characteristics["alpha_only_ratio"] = (
            alpha_only_ratio
        )

    # Alpha-numeric values
    alpha_numeric_ratio = column_profile.get(
        "alpha_numeric_ratio"
    )

    if alpha_numeric_ratio is not None:
        characteristics["alpha_numeric_ratio"] = (
            alpha_numeric_ratio
        )

    # Cardinality / uniqueness
    if "cardinality" in column_profile:
        characteristics["cardinality"] = (
            column_profile["cardinality"]
        )

    if "unique_ratio" in column_profile:
        characteristics["unique_ratio"] = (
            column_profile["unique_ratio"]
        )

    return characteristics

def evaluate_value_evidence(
    candidate,
    column_profile
):
    """
    Evaluate whether the observed value characteristics
    are compatible with an existing semantic candidate.

    This function does not create a semantic candidate.
    It only provides supporting evidence.
    """

    concept = candidate["concept"]

    characteristics = collect_value_characteristics(
        column_profile
    )

    evidence = {
        "concept": concept,
        "characteristics": characteristics,
        "support": None,
        "reasons": []
    }

    numeric_ratio = characteristics.get(
        "numeric_like_ratio"
    )

    date_ratio = characteristics.get(
        "date_like_ratio"
    )

    integer_ratio = characteristics.get(
        "integer_like_ratio"
    )

    # --------------------------------------------------------
    # Numeric concepts
    # --------------------------------------------------------

    numeric_concepts = {
        "quantity",
        "unit_price",
        "total_amount",
        "revenue",
        "order_value",
        "age",
        "income"
    }

    if concept in numeric_concepts:

        if numeric_ratio is not None:

            if numeric_ratio >= 80:

                evidence["support"] = True

                evidence["reasons"].append(
                    "values are predominantly numeric"
                )

            else:

                evidence["support"] = False

                evidence["reasons"].append(
                    "values are not predominantly numeric"
                )

    # --------------------------------------------------------
    # Date concepts
    # --------------------------------------------------------

    date_concepts = {
        "transaction_date",
        "purchase_date",
        "order_date",
        "invoice_date",
        "sale_date"
    }

    if concept in date_concepts:

        if date_ratio is not None:

            if date_ratio >= 80:

                evidence["support"] = True

                evidence["reasons"].append(
                    "values are predominantly date-like"
                )

            else:

                evidence["support"] = False

                evidence["reasons"].append(
                    "values are not predominantly date-like"
                )

    # --------------------------------------------------------
    # Integer-like evidence
    # --------------------------------------------------------

    if concept == "quantity":

        if integer_ratio is not None:

            if integer_ratio >= 80:

                evidence["support"] = True

                evidence["reasons"].append(
                    "values are predominantly integer-like"
                )

    return evidence

def add_value_evidence(
    candidates,
    column_profile
):
    """
    Add generic value-pattern evidence
    to existing semantic candidates.
    """

    for candidate in candidates:

        candidate["value_evidence"] = (
            evaluate_value_evidence(
                candidate,
                column_profile
            )
        )

    return candidates


# PART 8 — CARDINALITY EVIDENCE
# ============================================================

def get_cardinality_ratio(column_profile):
    """
    Get the proportion of unique values in a column.
    """

    if "unique_ratio" in column_profile:

        return (
            column_profile["unique_ratio"] / 100
        )

    cardinality = column_profile.get(
        "cardinality"
    )

    rows = column_profile.get(
        "rows"
    )

    if (
        cardinality is not None
        and rows is not None
        and rows > 0
    ):

        return cardinality / rows

    return None


def evaluate_cardinality_evidence(
    candidate,
    column_profile
):
    """
    Evaluate whether the column's uniqueness pattern
    supports the semantic candidate.
    """

    concept = candidate["concept"]

    unique_ratio = get_cardinality_ratio(
        column_profile
    )

    evidence = {
        "concept": concept,
        "unique_ratio": unique_ratio,
        "support": None,
        "reason": None
    }

    if unique_ratio is None:
        return evidence

    # Transaction/order identifiers
    if concept in {
        "transaction_id",
        "invoice_id",
        "order_id"
    }:

        if unique_ratio >= 0.80:

            evidence["support"] = True
            evidence["reason"] = (
                "column is mostly unique"
            )

        else:

            evidence["support"] = False
            evidence["reason"] = (
                "column is not mostly unique"
            )

    # Customer identifier
    elif concept == "customer_id":

        if unique_ratio < 0.80:

            evidence["support"] = True
            evidence["reason"] = (
                "column contains repeated values"
            )

        else:

            evidence["support"] = False
            evidence["reason"] = (
                "column is highly unique"
            )

    return evidence


def add_cardinality_evidence(
    candidates,
    column_profile
):
    """
    Add cardinality evidence to existing
    semantic candidates.
    """

    for candidate in candidates:

        candidate["cardinality_evidence"] = (
            evaluate_cardinality_evidence(
                candidate,
                column_profile
            )
        )

    return candidates

def collect_detected_concepts(
    candidates_by_column
):
    """
    Collect semantic concepts already detected
    across the dataset.
    """

    detected_concepts = set()

    for candidates in candidates_by_column.values():

        for candidate in candidates:

            detected_concepts.add(
                candidate["concept"]
            )

    return detected_concepts


def evaluate_surrounding_concepts(
    candidate,
    detected_concepts
):
    """
    Check whether other semantic concepts in the
    dataset provide contextual support for a candidate.
    """

    concept = candidate["concept"]

    related_concepts = {
        "unit_price": {
            "product_id",
            "product_name",
            "quantity",
            "transaction_id",
            "transaction_date",
            "purchase_date",
            "order_date"
        },

        "quantity": {
            "product_id",
            "product_name",
            "unit_price",
            "total_amount",
            "transaction_id"
        },

        "customer_id": {
            "customer_name",
            "age",
            "gender",
            "transaction_id",
            "order_id"
        },

        "customer_name": {
            "customer_id",
            "age",
            "gender"
        },

        "transaction_date": {
            "transaction_id",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price"
        }
    }

    expected_context = related_concepts.get(
        concept
    )

    if expected_context is None:
        return {
            "support": None,
            "matched_context": []
        }

    matched_context = (
        expected_context
        & detected_concepts
    )

    return {
        "support": bool(matched_context),
        "matched_context": list(
            matched_context
        )
    }


def add_surrounding_concept_evidence(
    candidates_by_column
):
    """
    Add contextual evidence to candidates
    using concepts detected in other columns.
    """

    detected_concepts = (
        collect_detected_concepts(
            candidates_by_column
        )
    )

    for column, candidates in (
        candidates_by_column.items()
    ):

        for candidate in candidates:

            candidate[
                "surrounding_concept_evidence"
            ] = evaluate_surrounding_concepts(
                candidate,
                detected_concepts
            )

    return candidates_by_column

EVIDENCE_WEIGHTS = {
    "known_synonym": 30,
    "token_match": 15,
    "fuzzy_match": 20,
    "datatype": 10,
    "value": 10,
    "cardinality": 5,
    "context": 10
}


def calculate_candidate_score(candidate):
    """
    Calculate a confidence score for one semantic candidate.
    """

    score = 0

    # --------------------------------------------------------
    # Known synonym
    # --------------------------------------------------------

    if candidate.get("known_synonym") is True:

        score += EVIDENCE_WEIGHTS[
            "known_synonym"
        ]

    # --------------------------------------------------------
    # Token matching
    # --------------------------------------------------------

    if candidate.get("token_match") is True:

        score += EVIDENCE_WEIGHTS[
            "token_match"
        ]

    # --------------------------------------------------------
    # Fuzzy matching
    # --------------------------------------------------------

    similarity = candidate.get(
        "similarity"
    )

    if similarity is not None:

        fuzzy_score = (
            similarity / 100
        ) * EVIDENCE_WEIGHTS[
            "fuzzy_match"
        ]

        score += fuzzy_score

    # --------------------------------------------------------
    # Datatype evidence
    # --------------------------------------------------------

    datatype_evidence = candidate.get(
        "datatype_support"
    )

    if datatype_evidence is True:

        score += EVIDENCE_WEIGHTS[
            "datatype"
        ]

    # --------------------------------------------------------
    # Value evidence
    # --------------------------------------------------------

    value_evidence = candidate.get(
        "value_evidence"
    )

    if (
        value_evidence is not None
        and value_evidence.get("support") is True
    ):

        score += EVIDENCE_WEIGHTS[
            "value"
        ]

    # --------------------------------------------------------
    # Cardinality evidence
    # --------------------------------------------------------

    cardinality_evidence = candidate.get(
        "cardinality_evidence"
    )

    if (
        cardinality_evidence is not None
        and cardinality_evidence.get("support") is True
    ):

        score += EVIDENCE_WEIGHTS[
            "cardinality"
        ]

    # --------------------------------------------------------
    # Surrounding concepts
    # --------------------------------------------------------

    context_evidence = candidate.get(
        "surrounding_concept_evidence"
    )

    if (
        context_evidence is not None
        and context_evidence.get("support") is True
    ):

        score += EVIDENCE_WEIGHTS[
            "context"
        ]

    return round(
        min(score, 100),
        2
    )


def classify_candidate_score(score):

    if score >= 75:

        return "HIGH"

    elif score >= 50:

        return "MEDIUM"

    else:

        return "LOW"


def score_candidate(candidate):

    score = calculate_candidate_score(
        candidate
    )

    candidate["confidence_score"] = score

    candidate["confidence_level"] = (
        classify_candidate_score(score)
    )

    return candidate

def decide_mapping(
    candidate,
    high_threshold,
    medium_threshold
):
    """
    Decide what action should be taken
    based on the candidate confidence score.
    """

    score = candidate.get(
        "confidence_score",
        0
    )

    if score >= high_threshold:

        decision = "AUTO_MAP"

    elif score >= medium_threshold:

        decision = "SUGGEST"

    else:

        decision = "UNKNOWN"

    candidate["decision"] = decision

    return candidate

def finalize_mapping(candidate):
    """
    Accept a semantic mapping only when the evidence
    is sufficient. Otherwise keep it UNKNOWN.
    """

    decision = candidate.get(
        "decision"
    )

    if decision == "AUTO_MAP":
        return candidate

    if decision == "SUGGEST":
        return candidate

    candidate["concept"] = None
    candidate["decision"] = "UNKNOWN"

    return candidate
HIGH_THRESHOLD = 70
MEDIUM_THRESHOLD = 50
def merge_candidates(
    known_matches,
    token_matches,
    fuzzy_matches
):
    merged = {}

    # Known synonym matches
    for match in known_matches:

        key = (
            match["family"],
            match["concept"]
        )

        if key not in merged:

            merged[key] = {
                "family": match["family"],
                "concept": match["concept"],
                "known_synonym": False,
                "token_match": False,
                "similarity": None
            }

        merged[key]["known_synonym"] = True

        merged[key]["matched_synonym"] = (
            match["matched_synonym"]
        )


    # Token matches
    for match in token_matches:

        key = (
            match["family"],
            match["concept"]
        )

        if key not in merged:

            merged[key] = {
                "family": match["family"],
                "concept": match["concept"],
                "known_synonym": False,
                "token_match": False,
                "similarity": None
            }

        merged[key]["token_match"] = True

        merged[key]["matched_tokens"] = (
            match["matched_tokens"]
        )


    # Fuzzy matches
    for match in fuzzy_matches:

        key = (
            match["family"],
            match["concept"]
        )

        if key not in merged:

            merged[key] = {
                "family": match["family"],
                "concept": match["concept"],
                "known_synonym": False,
                "token_match": False,
                "similarity": None
            }

        old_similarity = merged[key]["similarity"]

        if (
            old_similarity is None
            or match["similarity"] > old_similarity
        ):

            merged[key]["similarity"] = (
                match["similarity"]
            )

            merged[key]["matched_synonym"] = (
                match["matched_synonym"]
            )

    return list(merged.values())

def semantic_map_dataset(df, profile_info):

    candidates_by_column = {}

    for column in df.columns:

        # --------------------------------------------------
        # Part 3 — Known synonym matching
        # --------------------------------------------------

        known_matches = find_known_synonym_matches(
            column,
            RETAIL_ONTOLOGY
        )


        # --------------------------------------------------
        # Part 4 — Token matching
        # --------------------------------------------------

        token_matches = find_token_matches(
            column,
            RETAIL_ONTOLOGY
        )


        # --------------------------------------------------
        # Part 5 — Fuzzy matching
        # --------------------------------------------------

        fuzzy_matches = find_fuzzy_matches(
            column,
            RETAIL_ONTOLOGY
        )


        # --------------------------------------------------
        # Merge duplicate candidates
        # --------------------------------------------------

        candidates = merge_candidates(
            known_matches,
            token_matches,
            fuzzy_matches
        )


        # --------------------------------------------------
        # Get profile information for this column
        # --------------------------------------------------

        column_profile = profile_info.get(
            column
        )

        if column_profile is None:

            candidates_by_column[column] = candidates

            continue


        # --------------------------------------------------
        # Part 6 — Datatype evidence
        # --------------------------------------------------

        candidates = add_datatype_evidence(
            candidates,
            column_profile
        )


        # --------------------------------------------------
        # Part 7 — Value evidence
        # --------------------------------------------------

        candidates = add_value_evidence(
            candidates,
            column_profile
        )


        # --------------------------------------------------
        # Part 8 — Cardinality evidence
        # --------------------------------------------------

        candidates = add_cardinality_evidence(
            candidates,
            column_profile
        )


        candidates_by_column[column] = candidates


    # ------------------------------------------------------
    # Part 9 — Surrounding concept evidence
    # ------------------------------------------------------

        candidates_by_column = (
        add_surrounding_concept_evidence(
            candidates_by_column
        )
    )

        # --------------------------------------------------------
    # Score each candidate
    # --------------------------------------------------------

    for column, candidates in candidates_by_column.items():

        for candidate in candidates:

            candidate = score_candidate(
                candidate
            )

            candidate = decide_mapping(
                candidate,
                HIGH_THRESHOLD,
                MEDIUM_THRESHOLD
            )

            candidate = finalize_mapping(
                candidate
            )

    return candidates_by_column