import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class GeminiLLMService:
    """
    Serviço de processamento com Google Gemini LLM.
    Analisa texto extraído de livros e gera análise estruturada.
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.client = None
        if api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
            except ImportError:
                logger.warning("google-generativeai não instalado. LLM será simulado.")
            except Exception as e:
                logger.warning(f"Erro ao configurar Gemini: {str(e)}. LLM será simulado.")

    def analyze_book_content(self, title: str, author: str, extracted_text: str) -> dict[str, Any]:
        """
        Analisa conteúdo de um livro extraído por OCR.
        Retorna estrutura com:
        - disciplina (subject)
        - sequência pedagógica (chapters/topics em ordem)
        - habilidades BNCC
        - nivel de dificuldade
        """
        if not self.api_key:
            logger.warning("Gemini API key não configurada. Retornando análise simulada.")
            return self._simulate_analysis(title, author)

        try:
            prompt = f"""
Analise o seguinte texto extraído de um livro infantil/educativo e gere uma análise estruturada em JSON:

LIVRO: "{title}"
AUTOR: "{author}"

TEXTO EXTRAÍDO:
{extracted_text[:3000]}...

Por favor, retorne um JSON válido com a seguinte estrutura:
{{
    "subject": "disciplina identificada (ex: Português, Matemática, História)",
    "proficiency_level": "nível de proficiência (Infantil, Fundamental 1, Fundamental 2)",
    "chapters": [
        {{
            "number": 1,
            "title": "título do capítulo",
            "themes": ["tema 1", "tema 2"],
            "skills": ["habilidade BNCC 1", "habilidade BNCC 2"],
            "difficulty": "easy|medium|hard"
        }}
    ],
    "pedagogical_sequence": ["conceito 1", "conceito 2", "conceito 3"],
    "bncc_skills": ["EF01LP01", "EF01LP02"],
    "learning_style_recommendations": ["visual", "kinesthetic", "auditory"],
    "summary": "resumo breve do livro e seu propósito pedagógico"
}}

Retorne APENAS o JSON, sem markdown ou explicações adicionais.
"""

            try:
                response = self.model.generate_content(prompt)
                response_text = response.text

                try:
                    analysis = json.loads(response_text)
                    logger.info(f"Análise IA gerada com sucesso para: {title}")
                    return analysis
                except json.JSONDecodeError:
                    logger.error(f"Resposta da IA não é JSON válido: {response_text[:200]}")
                    return self._simulate_analysis(title, author)
            except Exception as e:
                logger.error(f"Erro ao chamar Gemini API: {str(e)}")
                return self._simulate_analysis(title, author)
        except Exception as e:
            logger.error(f"Erro geral em analyze_book_content: {str(e)}")
            return self._simulate_analysis(title, author)

    def generate_study_plan(self, book_analysis: dict, child_grade: str, child_preferences: dict | None = None) -> str:
        """
        Gera plano de estudos personalizado baseado na análise do livro + perfil da criança.
        """
        if not self.api_key:
            logger.warning("Gemini API key não configurada. Retornando plano simulado.")
            return self._simulate_study_plan(book_analysis, child_grade)

        try:
            prompt = f"""
Gere um plano de estudos personalizado para uma criança do nível "{child_grade}"
com base na seguinte análise de livro:

{json.dumps(book_analysis, ensure_ascii=False, indent=2)}

Preferências de aprendizagem: {json.dumps(child_preferences, ensure_ascii=False) if child_preferences else "não especificadas"}

Por favor, gere um plano estruturado com:
1. Sequência diária de tópicos (7-10 dias)
2. Atividades para cada dia
3. Tempo estimado
4. Indicadores de progresso
5. Sugestões de reforço para pais

Retorne em formato Markdown bem estruturado.
"""

            try:
                response = self.model.generate_content(prompt)
                plan_text = response.text
                logger.info(f"Plano de estudos gerado com sucesso")
                return plan_text
            except Exception as e:
                logger.error(f"Erro ao gerar plano com Gemini: {str(e)}")
                return self._simulate_study_plan(book_analysis, child_grade)
        except Exception as e:
            logger.error(f"Erro geral em generate_study_plan: {str(e)}")
            return self._simulate_study_plan(book_analysis, child_grade)

    def generate_daily_interaction(
        self,
        child_name: str,
        chapter: str,
        theme: str,
        recipient_type: str = "child",
    ) -> str:
        """
        Gera interação personalizada para criança ou pais sobre tema específico.
        """
        if not self.api_key:
            logger.warning("Gemini API key não configurada. Retornando interação simulada.")
            return self._simulate_interaction(child_name, chapter, theme, recipient_type)

        try:
            if recipient_type == "child":
                prompt = f"""
Gere uma mensagem interativa e lúdica para uma criança sobre o seguinte:
- Nome da criança: {child_name}
- Capítulo: {chapter}
- Tema: {theme}

A mensagem deve:
1. Ser amigável e motivadora
2. Fazer uma pergunta aberta para engajar a criança
3. Sugerir uma atividade prática relacionada ao tema
4. Usar vocabulário apropriado para crianças
5. Ter entre 100-200 palavras

Responda apenas com a mensagem, sem formatação adicional.
"""
            else:  # parent
                prompt = f"""
Gere uma orientação para os pais sobre como apoiar a aprendizagem do filho(a) sobre:
- Capítulo: {chapter}
- Tema: {theme}

A orientação deve:
1. Explicar brevemente o objetivo pedagógico
2. Sugerir 3-4 atividades práticas em casa
3. Dicas de como conversar com a criança sobre o tema
4. Indicadores de progresso a observar
5. Ter entre 150-250 palavras

Responda apenas com a orientação, sem formatação adicional.
"""

            try:
                response = self.model.generate_content(prompt)
                interaction_text = response.text
                logger.info(f"Interação gerada com sucesso para {recipient_type}")
                return interaction_text
            except Exception as e:
                logger.error(f"Erro ao gerar interação com Gemini: {str(e)}")
                return self._simulate_interaction(child_name, chapter, theme, recipient_type)
        except Exception as e:
            logger.error(f"Erro geral em generate_daily_interaction: {str(e)}")
            return self._simulate_interaction(child_name, chapter, theme, recipient_type)

    @staticmethod
    def _simulate_analysis(title: str, author: str) -> dict[str, Any]:
        """Simula análise de IA para testes sem API configurada."""
        logger.info(f"Simulando análise para livro: {title}")
        return {
            "subject": "Português",
            "proficiency_level": "Fundamental 1",
            "chapters": [
                {
                    "number": 1,
                    "title": "As Vogais - Descobrindo os Sons",
                    "themes": ["vogais", "sons", "pronuncia"],
                    "skills": ["EF01LP01", "EF01LP03"],
                    "difficulty": "easy"
                },
                {
                    "number": 2,
                    "title": "Formando Palavras Simples",
                    "themes": ["consonantes", "sílabas", "palavras"],
                    "skills": ["EF01LP04", "EF01LP05"],
                    "difficulty": "medium"
                },
                {
                    "number": 3,
                    "title": "Leitura com Compreensão",
                    "themes": ["frase", "contexto", "significado"],
                    "skills": ["EF01LP15", "EF01LP16"],
                    "difficulty": "medium"
                }
            ],
            "pedagogical_sequence": [
                "Identificar vogais",
                "Reconhecer consonantes",
                "Formar sílabas",
                "Ler palavras simples",
                "Compreender sentido"
            ],
            "bncc_skills": ["EF01LP01", "EF01LP03", "EF01LP04"],
            "learning_style_recommendations": ["visual", "kinesthetic"],
            "summary": f"O livro '{title}' de {author} é uma introdução estruturada à leitura e escrita no nível fundamental."
        }

    @staticmethod
    def _simulate_study_plan(book_analysis: dict, child_grade: str) -> str:
        """Simula plano de estudos."""
        logger.info(f"Simulando plano de estudos para nível: {child_grade}")
        return f"""
# Plano de Estudos Personalizado

## Nível: {child_grade}
## Disciplina: {book_analysis.get('subject', 'Português')}

### Semana 1

**Dia 1: Introdução e Vogais**
- Tempo: 30 minutos
- Atividade: Identificar vogais em palavras simples
- Reforço para pais: Mostrar figuras de objetos que começam com cada vogal

**Dia 2: Reconhecendo Padrões**
- Tempo: 30 minutos
- Atividade: Exercícios de pareamento vogais-palavras
- Reforço para pais: Brincar de "jogo da vogal"

### Próximos Passos
Continuar com consonantes e formação de sílabas após dominar as vogais.
"""

    @staticmethod
    def _simulate_interaction(child_name: str, chapter: str, theme: str, recipient_type: str) -> str:
        """Simula interação personalizada."""
        logger.info(f"Simulando interação para {recipient_type}")
        if recipient_type == "child":
            return (
                f"Oi, {child_name}! 🌟\n\n"
                f"Hoje vamos explorar '{theme}' no capítulo '{chapter}'.\n\n"
                f"Você consegue pensar em 3 palavras que começam com cada letra que vamos estudar?\n\n"
                f"Tente completar essa atividade e me conte depois! 📚✏️"
            )
        else:
            return (
                f"Olá!\n\n"
                f"Hoje seu(a) filho(a) estudou sobre '{theme}' ({chapter}).\n\n"
                f"Dicas para reforçar em casa:\n"
                f"1. Peça para ele(a) mostrar o que aprendeu\n"
                f"2. Brincam juntos com as palavras\n"
                f"3. Leiam histórias curtas sobre o tema\n\n"
                f"Observação importante: Foque no esforço e interesse, não apenas na perfeição! 🎯"
            )


llm_service = None


def get_llm_service(api_key: str | None = None) -> GeminiLLMService:
    """Factory function para criar ou obter instância do serviço LLM."""
    global llm_service
    if llm_service is None:
        llm_service = GeminiLLMService(api_key)
    return llm_service
