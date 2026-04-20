class EnergiaError(Exception):
    """Base para erros de dominio da aplicacao."""


class DataStoreError(EnergiaError):
    """Falha ao carregar ou salvar dados persistidos."""


class ValidationError(EnergiaError):
    """Dados informados nao atendem as regras de negocio."""
