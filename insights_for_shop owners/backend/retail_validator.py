import re
from backend.retail_ontology import RETAIL_ONTOLOGY
from itertools import combinations

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

# --------------------------------------------------
# Iteration 2 - Part 1
# Detect observed datatype
# --------------------------------------------------

def detect_observed_datatype(column_profile):

    original_dtype = str(
        column_profile["original_dtype"]
    ).lower()

    numeric_ratio = column_profile.get(
        "numeric_like_ratio",
        0
    )

    date_ratio = column_profile.get(
        "date_like_ratio",
        0
    )
    # Native numeric data
    if (
        "int" in original_dtype
        or "float" in original_dtype):
        return "numeric"
    
    # Numeric data
    if numeric_ratio >= 80:
        return "numeric"

    # Date-like data
    if date_ratio >= 80:
        return "date"

    # Native pandas datetime
    if "datetime" in original_dtype:
        return "date"

    # Text / object data
    if (
        "object" in original_dtype
        or "string" in original_dtype
    ):
        return "text"

    # Boolean data
    if "bool" in original_dtype:
        return "boolean"

    # Anything we don't recognize
    return "unknown"

# --------------------------------------------------
# Iteration 2 - Part 2
# Collect datatype evidence
# --------------------------------------------------
def collect_datatype_evidence(matches, profile_info):

    datatype_evidence = {}

    for column in matches:

        column_profile = profile_info.get(column)

        if column_profile is None:
            continue

        observed_datatype = detect_observed_datatype(
            column_profile
        )

        datatype_evidence[column] = {
            "observed_datatype": observed_datatype,
            "original_dtype": str(
                column_profile["original_dtype"]
            )
        }

    return datatype_evidence
# --------------------------------------------------
# Iteration 2 - Part 3
# Connect ontology + datatype evidence
# --------------------------------------------------

def validate_retail_iteration_2(columns, profile_info):

    # Step 1: Find ontology matches
    matches = match_columns(
        columns,
        RETAIL_ONTOLOGY
    )

    # Step 2: Collect datatype evidence
    datatype_evidence = collect_datatype_evidence(
        matches,
        profile_info
    )

    return {
        "matched_columns": matches,
        "datatype_evidence": datatype_evidence
    }

# --------------------------------------------------
# Iteration 3 - Part 1
# Detect integer-like values
# --------------------------------------------------

def detect_integer_like(column_profile):

    original_dtype = str(
        column_profile["original_dtype"]
    ).lower()

    # Native integer columns
    if "int" in original_dtype:
        return True

    # For other numeric columns, check whether
    # the values are mostly whole numbers.
    min_value = column_profile.get("min")
    max_value = column_profile.get("max")

    if min_value is None or max_value is None:
        return False

    # If min and max are whole numbers,
    # treat the column as potentially integer-like.
    if (
        float(min_value).is_integer()
        and float(max_value).is_integer()
    ):
        return True

    return False

# --------------------------------------------------
# Iteration 3 - Part 2
# Collect value-pattern evidence
# --------------------------------------------------

def collect_value_pattern_evidence(matches, profile_info):

    value_evidence = {}

    for column in matches:

        column_profile = profile_info.get(column)

        if column_profile is None:
            continue

        integer_like = detect_integer_like(
            column_profile
        )

        value_evidence[column] = {
            "integer_like": integer_like
        }

    return value_evidence

# --------------------------------------------------
# Iteration 3 - Part 3
# Connect value-pattern evidence
# --------------------------------------------------

def validate_retail_iteration_3(columns, profile_info):

    # Step 1: Find ontology matches
    matches = match_columns(
        columns,
        RETAIL_ONTOLOGY
    )

    # Step 2: Collect value-pattern evidence
    value_evidence = collect_value_pattern_evidence(
        matches,
        profile_info
    )

    return {
        "matched_columns": matches,
        "value_evidence": value_evidence
    }

# ============================================================
# ITERATION 4 — CONCEPT COMBINATIONS
# ============================================================

RETAIL_COMBINATION_RULES = {

    "strong": [
        {"required": {"product", "quantity", "price"}},
        {"required": {"product", "quantity", "sales"}},
        {"required": {"product", "price", "sales"}},
        {"required": {"product", "quantity", "price", "date"}},
    ],

    "supporting": [
        {"required": {"product", "quantity"}},
        {"required": {"product", "price"}},
        {"required": {"product", "sales"}},
        {"required": {"product", "date"}},
        {"required": {"customer_identity", "product"}},
        {"required": {"customer_identity", "sales"}},
    ]
}


COMBINATION_SCORES = {
    "strong": 3,
    "supporting": 1
}

MAX_COMBINATION_SCORE = 5


def generate_concept_combinations(concepts, max_size=4):

    combinations_found = []

    max_size = min(
        max_size,
        len(concepts)
    )

    for size in range(2, max_size + 1):

        for combo in combinations(
            concepts,
            size
        ):
            combinations_found.append(combo)

    return combinations_found


def classify_concept_combination(combo):

    combo_set = set(combo)

    matched_strength = None
    matched_size = 0

    for strength, rules in RETAIL_COMBINATION_RULES.items():

        for rule in rules:

            required = rule["required"]

            if required.issubset(combo_set):

                if len(required) > matched_size:

                    matched_strength = strength
                    matched_size = len(required)

    return matched_strength


def analyze_concept_combinations(concepts):

    combinations_found = (
        generate_concept_combinations(concepts)
    )

    meaningful_combinations = []

    total_score = 0

    for combo in combinations_found:

        strength = classify_concept_combination(
            combo
        )

        if strength is None:
            continue

        score = COMBINATION_SCORES[
            strength
        ]

        meaningful_combinations.append({
            "combination": combo,
            "strength": strength,
            "score": score
        })

        total_score += score

    total_score = min(
        total_score,
        MAX_COMBINATION_SCORE
    )

    return {
        "combinations_checked": combinations_found,
        "meaningful_combinations":
            meaningful_combinations,
        "combination_score": total_score
    }


# ============================================================
# ITERATION 5 — STRUCTURAL EVIDENCE
# ============================================================

STRUCTURAL_WEIGHTS = {
    "repeated_transaction_id": 2,
    "repeated_customer_id": 1,
    "repeated_product": 1,
    "numerical_relationship": 2
}

MAX_STRUCTURAL_SCORE = 5


def get_unique_ratio(column_profile):

    # If the profiler already provides a ratio
    if "unique_ratio" in column_profile:

        return column_profile["unique_ratio"]

    if "uniqueness_ratio" in column_profile:

        return column_profile[
            "uniqueness_ratio"
        ]

    # Otherwise calculate it
    unique_count = column_profile.get(
        "unique_count"
    )

    row_count = column_profile.get(
        "count"
    )

    if (
        unique_count is not None
        and row_count is not None
        and row_count > 0
    ):

        return unique_count / row_count

    return None


def detect_repeated_structure(
    column,
    column_matches,
    column_profile
):

    unique_ratio = get_unique_ratio(
        column_profile
    )

    if unique_ratio is None:
        return None

    concepts = {
        match["concept"]
        for match in column_matches
    }

    # Transaction / Order ID
    if (
        "transaction_order" in concepts
        and unique_ratio < 1
    ):

        return {
            "column": column,
            "type": "repeated_transaction_id",
            "score":
                STRUCTURAL_WEIGHTS[
                    "repeated_transaction_id"
                ]
        }

    # Customer ID
    if (
        "customer_identity" in concepts
        and unique_ratio < 1
    ):

        return {
            "column": column,
            "type": "repeated_customer_id",
            "score":
                STRUCTURAL_WEIGHTS[
                    "repeated_customer_id"
                ]
        }

    # Product
    if (
        "product" in concepts
        and unique_ratio < 1
    ):

        return {
            "column": column,
            "type": "repeated_product",
            "score":
                STRUCTURAL_WEIGHTS[
                    "repeated_product"
                ]
        }

    return None


def detect_numerical_relationship(
    relationship_info
):

    if not relationship_info:
        return None

    for relationship in relationship_info:

        if relationship.get("valid") is True:

            return {
                "type":
                    "numerical_relationship",

                "columns":
                    relationship.get(
                        "columns",
                        []
                    ),

                "score":
                    STRUCTURAL_WEIGHTS[
                        "numerical_relationship"
                    ]
            }

    return None


def analyze_structural_evidence(
    matches,
    profile_info,
    relationship_info=None
):

    structural_evidence = []

    total_score = 0

    for column in matches:

        column_profile = profile_info.get(
            column
        )

        if column_profile is None:
            continue

        column_matches = matches.get(
            column,
            []
        )

        repeated_structure = (
            detect_repeated_structure(
                column,
                column_matches,
                column_profile
            )
        )

        if repeated_structure is not None:

            structural_evidence.append(
                repeated_structure
            )

            total_score += (
                repeated_structure["score"]
            )

    numerical_relationship = (
        detect_numerical_relationship(
            relationship_info
        )
    )

    if numerical_relationship is not None:

        structural_evidence.append(
            numerical_relationship
        )

        total_score += (
            numerical_relationship["score"]
        )

    total_score = min(
        total_score,
        MAX_STRUCTURAL_SCORE
    )

    return {
        "structural_evidence":
            structural_evidence,

        "structural_score":
            total_score
    }


# ============================================================
# ITERATION 6 — FINAL DECISION
# ============================================================

ACCEPT_THRESHOLD = 70
REVIEW_THRESHOLD = 40


def calculate_final_confidence(
    evidence_score,
    combination_score,
    structural_score
):

    # Existing ontology evidence
    basic_confidence = min(
        evidence_score / 10,
        1
    )

    # Iteration 4
    combination_confidence = (
        combination_score
        / MAX_COMBINATION_SCORE
    )

    # Iteration 5
    structural_confidence = (
        structural_score
        / MAX_STRUCTURAL_SCORE
    )

    # Evidence weighting
    final_confidence = (

        basic_confidence * 50

        + combination_confidence * 30

        + structural_confidence * 20
    )

    return round(
        min(final_confidence, 100),
        2
    )


def classify_retail_result(confidence):

    if confidence >= ACCEPT_THRESHOLD:

        return "ACCEPT"

    elif confidence >= REVIEW_THRESHOLD:

        return "REVIEW"

    else:

        return "REJECT"


# ============================================================
# FINAL RETAIL VALIDATOR
# ITERATIONS 1 → 6
# ============================================================

def validate_retail(
    columns,
    profile_info,
    relationship_info=None
):

    # --------------------------------------------------------
    # ITERATION 1
    # --------------------------------------------------------

    matches = match_columns(
        columns,
        RETAIL_ONTOLOGY
    )

    families = collect_families(
        matches
    )

    evidence = calculate_evidence(
        families
    )

    evidence_score = evidence[
        "evidence_score"
    ]


    # --------------------------------------------------------
    # ITERATION 2
    # --------------------------------------------------------

    datatype_evidence = (
        collect_datatype_evidence(
            matches,
            profile_info
        )
    )


    # --------------------------------------------------------
    # ITERATION 3
    # --------------------------------------------------------

    value_evidence = (
        collect_value_pattern_evidence(
            matches,
            profile_info
        )
    )


    # --------------------------------------------------------
    # ITERATION 4
    # --------------------------------------------------------

    # Concepts are ontology concepts,
    # not families.

    detected_concepts = set()

    for column_matches in matches.values():

        for match in column_matches:

            detected_concepts.add(
                match["concept"]
            )

    combination_evidence = (
        analyze_concept_combinations(
            list(detected_concepts)
        )
    )

    combination_score = (
        combination_evidence[
            "combination_score"
        ]
    )


    # --------------------------------------------------------
    # ITERATION 5
    # --------------------------------------------------------

    structural_evidence = (
        analyze_structural_evidence(
            matches,
            profile_info,
            relationship_info
        )
    )

    structural_score = (
        structural_evidence[
            "structural_score"
        ]
    )


    # --------------------------------------------------------
    # ITERATION 6
    # --------------------------------------------------------

    final_confidence = (
        calculate_final_confidence(
            evidence_score,
            combination_score,
            structural_score
        )
    )

    decision = classify_retail_result(
        final_confidence
    )


    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {

        "matched_columns":
            matches,

        "matched_families":
            list(families),

        "detected_concepts":
            list(detected_concepts),

        "strong_signals":
            evidence["strong_signals"],

        "supporting_signals":
            evidence["supporting_signals"],

        "weak_signals":
            evidence["weak_signals"],

        "evidence_score":
            evidence_score,

        "datatype_evidence":
            datatype_evidence,

        "value_evidence":
            value_evidence,

        "combination_evidence":
            combination_evidence,

        "structural_evidence":
            structural_evidence,

        "final_confidence":
            final_confidence,

        "decision":
            decision
    }