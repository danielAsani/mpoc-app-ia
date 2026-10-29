from scripts.setup_app import save_api_key


def test_save_key_preserves_other_settings(tmp_path):
    path = tmp_path / '.env'
    path.write_text('OPENAI_API_KEY=old\nLLM_MODEL=gpt-6-astra\n', encoding='utf-8')
    save_api_key(path, 'synthetic-test-key')
    assert path.read_text(encoding='utf-8') == 'OPENAI_API_KEY=synthetic-test-key\nLLM_MODEL=gpt-6-astra\n'


def test_save_key_rejects_multiline_input(tmp_path):
    import pytest
    path = tmp_path / '.env'
    path.write_text('LLM_MODEL=gpt-6-astra\n', encoding='utf-8')
    with pytest.raises(ValueError):
        save_api_key(path, 'synthetic\ninjected')
    assert 'OPENAI_API_KEY' not in path.read_text(encoding='utf-8')
