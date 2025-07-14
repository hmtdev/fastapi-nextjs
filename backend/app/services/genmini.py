import google.generativeai as genai
from app.core.config import get_settings


class GeminiService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GeminiService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not GeminiService._initialized:
            self.model = None
            GeminiService._initialized = True

    def initialize(self):
        settings = get_settings()
        if not settings.GENMINI_API_KEY:
            raise ValueError("GENMINI_API_KEY is not set in environment variables")
        genai.configure(api_key=settings.GENMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        print("✅ Gemini model initialized successfully")

    async def correct_text(self, text: str) -> dict:
        """ """
        if not self.model:
            raise RuntimeError("Gemini model not initialized")

        prompt = f"""Correct the following English text for grammar, spelling, and stylistic mistakes.
            
    Format your response with TWO clearly separated sections delimited by special markers:
    
    [HTML_START]
    <div class="corrected-text">
        <p>Your corrected text here, with corrected parts highlighted using <span style="color:red">corrected text</span> for each error fixed</p>
    </div>
    [HTML_END]
    
    [MARKDOWN_START]
    ## Errors Fixed
    - **Original**: "[Original error]"
      **Corrected**: "[Corrected version]"
      **Explanation**: [Brief explanation of why the correction was made]
    
    ## Suggestions for Improvement
    - **Original**: "[Original sentence/phrase]"
      **Suggestion**: "[Suggested alternative]"
      **Reason**: [Reason for suggestion]
    [MARKDOWN_END]
    
    Input Text: "{text}"
    
    IMPORTANT INSTRUCTIONS:
    1. First section (HTML): Provide ONLY the corrected text with corrections highlighted in red spans.
    2. Second section (Markdown): Provide detailed error analysis and suggestions using proper Markdown formatting.
    3. Use the exact markers [HTML_START], [HTML_END], [MARKDOWN_START], and [MARKDOWN_END] to delimit the sections.
    4. Do not include any text outside these sections.
            """

        response = await self.model.generate_content_async(prompt)
        response_text = response.text.strip()

        # Parse the response to extract HTML and Markdown parts
        html_part = ""
        markdown_part = ""

        # Extract HTML part
        if "[HTML_START]" in response_text and "[HTML_END]" in response_text:
            html_start = response_text.find("[HTML_START]") + len("[HTML_START]")
            html_end = response_text.find("[HTML_END]")
            html_part = response_text[html_start:html_end].strip()

        # Extract Markdown part
        if "[MARKDOWN_START]" in response_text and "[MARKDOWN_END]" in response_text:
            md_start = response_text.find("[MARKDOWN_START]") + len("[MARKDOWN_START]")
            md_end = response_text.find("[MARKDOWN_END]")
            markdown_part = response_text[md_start:md_end].strip()

        return {"html": html_part, "markdown": markdown_part}


gemini_service = GeminiService()


def get_gemini_service() -> GeminiService:
    if gemini_service.model is None:
        raise RuntimeError("Gemini service was not properly initialized")
    return gemini_service
