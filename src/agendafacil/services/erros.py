class RegraNegocioError(Exception):
    """Violação de regra de negócio; a mensagem é mostrada ao usuário."""


class ValidacaoError(RegraNegocioError):
    """Entrada inválida. `erros` mapeia campo -> mensagem."""

    def __init__(self, erros: dict):
        self.erros = erros
        super().__init__(" ".join(erros.values()))


class AcessoNegadoError(RegraNegocioError):
    def __init__(self, mensagem="Você não tem permissão para realizar esta ação."):
        super().__init__(mensagem)
