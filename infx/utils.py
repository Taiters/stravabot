def ssm_param(name: str, version: int = 1) -> str:
    return f"{{{{resolve:ssm:{name}:{version}}}}}"
