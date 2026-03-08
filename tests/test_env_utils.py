from config.env_utils import normalize_host, normalize_origin, split_env_list


def test_split_env_list_handles_empty_and_spaces():
    assert split_env_list(None) == []
    assert split_env_list("") == []
    assert split_env_list(" a, b ,,c ") == ["a", "b", "c"]


def test_normalize_host_accepts_host_or_url():
    assert normalize_host("api.example.com") == "api.example.com"
    assert normalize_host("https://api.example.com") == "api.example.com"
    assert normalize_host("https://api.example.com/path") == "api.example.com"


def test_normalize_origin_accepts_only_full_origins():
    assert normalize_origin("https://frontend.pages.dev/") == "https://frontend.pages.dev"
    assert normalize_origin("http://localhost:3000/some/path") == "http://localhost:3000"
    assert normalize_origin("frontend.pages.dev") == ""
