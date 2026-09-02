class SandboxError(Exception):
    pass

class ModuleNotAllowedError(SandboxError):
    pass

class NetworkDisabledError(SandboxError):
    pass
