def ssm_param(name, version):
    return f"{{{{resolve:ssm:{name}:{version}}}}}"
