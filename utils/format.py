def format_universities(data):
    if isinstance(data, dict) and "universities" in data:
        data = data["universities"]
    if not isinstance(data, list):
        return data
    return [
        {
            "University": uni.get("name", "-"),
            "Programs": uni.get("program_count", 0),
        }
        for uni in data
    ]


def format_eligible_programs(programs: list[dict]) -> list[dict]:
    return [
        {
            "Program": p.get("name", "-"),
            "Degree": p.get("degree", "-"),
            "Min Score": p.get("score", "-"),
        }
        for p in programs
    ]
