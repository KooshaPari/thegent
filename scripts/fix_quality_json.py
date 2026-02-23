import orjson as json


def fix_quality_json(file_path):
    with open(file_path) as f:
        data = json.load(f)

    gov = data.get("governance", {})

    # Remove unexpected properties from $.governance
    unexpected_gov = [
        "accessibility",
        "break_glass",
        "brownfield_paths",
        "characterization",
        "characterization_dir",
        "enforce_schema_registry",
        "performance",
        "schema_registry_url",
        "supply_chain",
    ]
    for prop in unexpected_gov:
        if prop in gov:
            del gov[prop]

    # Fix $.governance.smart_contract.rekor
    sc = gov.get("smart_contract", {})
    rekor = sc.get("rekor", {})

    # Add missing required properties
    rekor["require_inclusion_by_tier"] = {"new": False, "established": True, "critical": True}
    rekor["require_api_verification"] = True
    rekor["max_inclusion_age_days"] = 30

    # Remove unexpected 'require_inclusion'
    if "require_inclusion" in rekor:
        del rekor["require_inclusion"]

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Fixed {file_path}")


if __name__ == "__main__":
    fix_quality_json("../heliosShield/.claude/quality.json")
