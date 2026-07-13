from app.services.ai import MIN_DATA_POINTS_FOR_SUMMARY, build_child_summary
from app.models.child import Child


class FakeResult:
    def __iter__(self):
        return iter([])


class FakeDB:
    def scalars(self, query):
        return FakeResult()
        
    def get(self, model, ident):
        if model is Child:
            # Retorna um objeto mockado da Child
            class MockChild:
                id = ident
                full_name = "João da Silva"
                school_id = "some-school-id"
            return MockChild()
        return None


def test_summary_requires_minimum_data():
    result = build_child_summary(FakeDB(), "child-id")
    assert result["status"] == "insufficient_data"
    assert result["data_points"] < MIN_DATA_POINTS_FOR_SUMMARY
