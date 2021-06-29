def ssm_param(name: str, version: int = 1):
    return f"{{{{resolve:ssm:{name}:{version}}}}}"
