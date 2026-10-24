"""Explica o que mudou no plano depois de uma alteração nos fatos."""

from dataclasses import dataclass

from ponte.fatos import CAMPOS, Caso, descrever_valor
from ponte.regras import Orientacao, Plano


@dataclass(frozen=True)
class Mudanca:
    efeito: str
    orientacao: Orientacao
    campos_alterados: tuple[str, ...]


def comparar(caso_antes: Caso, plano_antes: Plano, caso_depois: Caso, plano_depois: Plano) -> list[Mudanca]:
    antes = {orientacao.chave: orientacao for orientacao in plano_antes.orientacoes}
    depois = {orientacao.chave: orientacao for orientacao in plano_depois.orientacoes}
    mudancas = []
    for chave, orientacao in antes.items():
        if chave not in depois:
            mudancas.append(Mudanca("retirada", orientacao, _campos_alterados(orientacao, caso_antes, caso_depois)))
        elif depois[chave] != orientacao:
            mudancas.append(Mudanca("alterada", depois[chave], _campos_alterados(depois[chave], caso_antes, caso_depois)))
    for chave, orientacao in depois.items():
        if chave not in antes:
            mudancas.append(Mudanca("incluída", orientacao, _campos_alterados(orientacao, caso_antes, caso_depois)))
    return mudancas


def descrever(mudanca: Mudanca, caso_antes: Caso, caso_depois: Caso) -> str:
    texto = f"{mudanca.efeito.capitalize()}: “{mudanca.orientacao.titulo}”."
    if not mudanca.campos_alterados:
        return texto
    alteracoes = "; ".join(
        f"“{CAMPOS[chave].rotulo}” de {descrever_valor(chave, caso_antes.fatos[chave])} "
        f"para {descrever_valor(chave, caso_depois.fatos[chave])}"
        for chave in mudanca.campos_alterados
    )
    return f"{texto} Motivo: você alterou {alteracoes}."


def _campos_alterados(orientacao: Orientacao, caso_antes: Caso, caso_depois: Caso) -> tuple[str, ...]:
    return tuple(
        chave
        for chave in orientacao.depende_de
        if caso_antes.fatos[chave].valor != caso_depois.fatos[chave].valor
        or caso_antes.valor(chave) != caso_depois.valor(chave)
    )
