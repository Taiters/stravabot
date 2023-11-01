from infx.utils import ssm_param

def test_ssm_param_returns_expected_string_without_version():
    assert ssm_param("a_value") == "{{resolve:ssm:a_value:1}}"

def test_ssm_param_returns_expected_string_with_version():
    assert ssm_param("a_value", 42) == "{{resolve:ssm:a_value:42}}"
