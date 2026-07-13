from app.services.ai import MIN_DATA_POINTS_FOR_SUMMARY, build_child_summary, build_child_interaction
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


def test_interaction_requires_minimum_data():
    result = build_child_interaction(FakeDB(), "child-id", "conversation")
    assert result["status"] == "insufficient_data"
    assert "mínimo de 3 registros" in result["content"]


def test_interaction_invalid_type():
    # Para passar da validação de dados, precisaríamos mockar scalars para retornar dados,
    # mas se mockarmos db.get para None ele retorna erro direto
    class EmptyDB:
        def get(self, model, ident):
            return None
    result = build_child_interaction(EmptyDB(), "child-id", "invalid-type")
    assert result["status"] == "error"
    assert "Criança não encontrada" in result["content"]

