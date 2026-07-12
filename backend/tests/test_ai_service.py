from app.services.ai import MIN_EVENTS_FOR_SUMMARY, build_child_summary


class FakeResult:
    def __iter__(self):
        return iter([])


class FakeDB:
    def scalars(self, query):
        return FakeResult()


def test_summary_requires_minimum_data():
    result = build_child_summary(FakeDB(), "child-id")
    assert result["status"] == "insufficient_data"
    assert result["data_points"] < MIN_EVENTS_FOR_SUMMARY

