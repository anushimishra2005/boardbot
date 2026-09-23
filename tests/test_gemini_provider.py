from api.agent.gemini_provider import GeminiProvider


def test_gemini_provider_configuration():
    provider = GeminiProvider()

    assert provider.model_name == "gemini-3.8-flash"
    assert len(provider.tools) ==7