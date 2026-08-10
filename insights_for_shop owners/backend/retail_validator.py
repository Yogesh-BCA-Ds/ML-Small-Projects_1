import re
from backend.retail_ontology import RETAIL_ONTOLOGY
def normalize_column_name(column):
    """
    Converts a column name into a standard format
    so that ontology matching becomes easier.
    """
    column = str(column).lower().strip()
    # Replace spaces and special characters with _
    column = re.sub(r"[^a-z0-9]+", "_", column)
    # Remove leading/trailing underscores
    column = column.strip("_")

    return column

# 2. Match columns with retail ontology
def match_columns(columns, ontology):
    matches = {}
    for column in columns:
        normalized_column = normalize_column_name(column)
        column_matches = []
        # Search through ontology
        for family, concepts in ontology.items():
            for concept, vocabulary in concepts.items():
                if normalized_column in vocabulary:
                    column_matches.append({
                        "family": family,
                        "concept": concept
                    })

        if column_matches:
            matches[column] = column_matches

    return matches

# 3. Collect matched ontology families
def collect_families(matches):

    families = set()

    for column_matches in matches.values():

        for match in column_matches:
            families.add(match["family"])

    return families

# 4. Retail signal strength
# --------------------------------------------------
# 4. Retail signal strength
# --------------------------------------------------

STRONG_SIGNALS = {
    "product",
    "sales",
    "returns_refunds"
}


SUPPORTING_SIGNALS = {
    "transaction_order",
    "customer_identity",
    "customer_behaviour",
    "loyalty",
    "payment",
    "inventory",
    "shipping_fulfillment",
    "promotion",
    "store",
    "ecommerce_behaviour",
    "marketing",
    "customer_satisfaction",
    "customer_service",
    "staff_pos",
    "cost_profitability"
}


WEAK_SIGNALS = {
    "demographics",
    "geography",
    "time",
    "tax_currency",
    "text_unstructured",
    "derived_features",
    "ml_targets"
}

# 5. Signal weights
SIGNAL_WEIGHTS = {
    "strong": 3,
    "supporting": 2,
    "weak": 1
}

# 6. Calculate basic retail evidence
def calculate_evidence(families):

    strong = []
    supporting = []
    weak = []

    for family in families:

        if family in STRONG_SIGNALS:
            strong.append(family)

        elif family in SUPPORTING_SIGNALS:
            supporting.append(family)

        elif family in WEAK_SIGNALS:
            weak.append(family)

    score = (
        len(strong) * SIGNAL_WEIGHTS["strong"]
        + len(supporting) * SIGNAL_WEIGHTS["supporting"]
        + len(weak) * SIGNAL_WEIGHTS["weak"]
    )

    return {
        "strong_signals": strong,
        "supporting_signals": supporting,
        "weak_signals": weak,
        "evidence_score": score
    }

# 7. Calculate simple confidence
def calculate_confidence(evidence_score):

    confidence = (evidence_score / 10) * 100

    # Maximum confidence is 100
    confidence = min(confidence, 100)

    return round(confidence, 2)

# 8. Iteration 1 Retail Validator
def validate_retail_iteration_1(columns):

    # Step 1: Find ontology matches
    matches = match_columns(
        columns,
        RETAIL_ONTOLOGY
    )

    # Step 2: Get unique concept families
    families = collect_families(matches)

    # Step 3: Calculate basic evidence
    evidence = calculate_evidence(families)

    # Step 4: Calculate confidence
    confidence = calculate_confidence(
        evidence["evidence_score"]
    )

    return {
        "matched_columns": matches,
        "matched_families": list(families),
        "strong_signals": evidence["strong_signals"],
        "supporting_signals": evidence["supporting_signals"],
        "weak_signals": evidence["weak_signals"],
        "evidence_score": evidence["evidence_score"],
        "confidence": confidence
    }