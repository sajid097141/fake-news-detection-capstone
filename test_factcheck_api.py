from webapp.factcheck import search_fact_checks, add_relevance_labels

query = "The Earth is flat"

result = search_fact_checks(query, page_size=5)

filtered = add_relevance_labels(query, result["claims"])

print("\n=== RELEVANT CLAIMS ===")

for claim in filtered["claims"]:
    print(
        claim["relevance"]["label"],
        "|",
        claim["claim_text"]
    )

print("\n=== EXCLUDED CLAIMS ===")

for claim in filtered["excluded_claims"]:
    print(
        claim["relevance"]["label"],
        "|",
        claim["claim_text"]
    )

print("\n=== SUMMARY ===")
print(filtered["relevance_summary"])