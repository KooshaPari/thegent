from teleprompter import Teleprompter


def test_teleprompter_improves_score():
    def metric(p: str) -> float:
        return float(len(p))

    tele = Teleprompter(iterations=3)
    prompts = ["hello"]
    result = tele.optimize(prompts, metric)
    assert len(result) == 1
    assert len(result[0]) >= len(prompts[0])


def test_teleprompter_multiple_prompts():
    def metric(p: str) -> float:
        return float(p.count("please"))

    tele = Teleprompter(iterations=3)
    prompts = ["fix this", "review code", "write docs"]
    result = tele.optimize(prompts, metric)
    assert len(result) == 3
    for r in result:
        assert isinstance(r, str)
