"""Fatos declarados sobre a situação do estudante.

Um fato registra o que a pessoa informou ou confirmou. Confirmar não comprova o
acontecimento: apenas registra a declaração atual. Só fatos confirmados ou
informados diretamente alimentam as regras; sugestões ainda não conferidas,
"não sei" e conflitos contam como desconhecidos.

Cada mudança no caso incrementa a revisão. Uma extração do relato só pode ser
aplicada se o caso continuar na revisão em que ela foi pedida e se o relato não
tiver mudado (ver resultado_ainda_vale).
"""

import hashlib
from dataclasses import dataclass, replace
from datetime import date
from enum import StrEnum

NAO_SEI = "nao_sei"

SIM_NAO = {"sim": "Sim", "nao": "Não", NAO_SEI: "Não sei"}


class Estado(StrEnum):
    SEM_RESPOSTA = "Sem resposta"
    A_CONFERIR = "A conferir"
    CONFIRMADO = "Confirmado por você"
    INFORMADO = "Informado por você"
    NAO_SEI = "Não sei"
    PRECISA_ESCLARECER = "Precisa esclarecer"


class Origem(StrEnum):
    NENHUMA = "nenhuma"
    RELATO = "relato"
    PESSOA = "pessoa"
    SISTEMA = "sistema"


@dataclass(frozen=True)
class Campo:
    chave: str
    pergunta: str
    rotulo: str
    tipo: str = "escolha"
    opcoes: dict[str, str] | None = None
    extraivel: bool = True
    so_do_relato: bool = False


CAMPOS: dict[str, Campo] = {
    campo.chave: campo
    for campo in (
        Campo(
            chave="aconteceu_com_voce",
            pergunta="A situação relatada aconteceu com você?",
            rotulo="Aconteceu com você",
            opcoes={"sim": "Sim", "outra_pessoa": "Não, aconteceu com outra pessoa", NAO_SEI: "Não sei"},
        ),
        Campo(
            chave="acontecimento",
            pergunta="Qual acontecimento você quer analisar?",
            rotulo="Acontecimento",
            opcoes={"alagacao": "Alagação", "incendio": "Incêndio", "outro": "Outro evento", NAO_SEI: "Não sei"},
        ),
        Campo(
            chave="descricao_acontecimento",
            pergunta="Descreva o acontecimento em poucas palavras",
            rotulo="Descrição do acontecimento",
            tipo="texto",
        ),
        Campo(
            chave="saiu_da_residencia",
            pergunta="Você precisou sair da sua própria residência por causa desse acontecimento?",
            rotulo="Saída da própria residência",
            opcoes=SIM_NAO,
        ),
        Campo(
            chave="data_evento",
            pergunta="Data do acontecimento",
            rotulo="Data do acontecimento",
            tipo="data",
        ),
        Campo(
            chave="data_referencia",
            pergunta="Data de referência para esta consulta",
            rotulo="Data de referência",
            tipo="data",
            extraivel=False,
        ),
        Campo(
            chave="perdeu_documentos",
            pergunta="Você perdeu documentos pessoais?",
            rotulo="Perda de documentos pessoais",
            opcoes=SIM_NAO,
        ),
        Campo(
            chave="dificuldade_moradia",
            pergunta="Você tem dificuldade para apresentar comprovante de moradia ou contrato?",
            rotulo="Dificuldade com comprovante de moradia",
            opcoes={**SIM_NAO, "nao_quero_informar": "Não quero informar"},
        ),
        Campo(
            chave="beneficio_anterior",
            pergunta="Você recebeu bolsa ou auxílio da assistência estudantil da Ufac nos últimos 3 anos?",
            rotulo="Benefício anterior mencionado",
            opcoes=SIM_NAO,
            so_do_relato=True,
        ),
    )
}

ESTADOS_DECLARADOS = (Estado.CONFIRMADO, Estado.INFORMADO)
ESTADOS_DE_SUGESTAO = (Estado.A_CONFERIR, Estado.PRECISA_ESCLARECER)


@dataclass(frozen=True)
class Fato:
    valor: object = None
    estado: Estado = Estado.SEM_RESPOSTA
    origem: Origem = Origem.NENHUMA
    trecho: str = ""
    nota: str = ""

    @property
    def conhecido(self) -> bool:
        return self.estado in ESTADOS_DECLARADOS and self.valor not in (None, NAO_SEI)


def descrever_valor(chave: str, fato: Fato) -> str:
    if fato.valor is None:
        return "Sem resposta"
    if fato.valor == NAO_SEI:
        return "Não sei"
    if isinstance(fato.valor, date):
        return fato.valor.strftime("%d/%m/%Y")
    opcoes = CAMPOS[chave].opcoes
    if opcoes:
        return opcoes.get(fato.valor, str(fato.valor))
    return str(fato.valor)


def versao_do_relato(relato: str) -> str:
    return hashlib.sha256(relato.strip().encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Caso:
    fatos: dict[str, Fato]
    revisao: int = 0
    versao_relato: str = ""

    @classmethod
    def novo(cls, data_referencia: date) -> "Caso":
        fatos = {chave: Fato() for chave in CAMPOS}
        fatos["data_referencia"] = Fato(
            valor=data_referencia,
            estado=Estado.A_CONFERIR,
            origem=Origem.SISTEMA,
            nota="Preenchida com a data de hoje. Confira se é a data em que pretende solicitar o auxílio.",
        )
        return cls(fatos)

    def valor(self, chave: str) -> object | None:
        """Valor declarado do fato, ou None quando ele ainda é desconhecido."""
        fato = self.fatos[chave]
        return fato.valor if fato.conhecido else None

    def informar(self, chave: str, valor: object) -> "Caso":
        estado = Estado.NAO_SEI if valor == NAO_SEI else Estado.INFORMADO
        return self._com_fato(chave, Fato(valor=valor, estado=estado, origem=Origem.PESSOA))

    def confirmar(self, chave: str) -> "Caso":
        fato = self.fatos[chave]
        if fato.estado is not Estado.A_CONFERIR:
            raise ValueError(f"{chave} não está aguardando conferência")
        estado = Estado.NAO_SEI if fato.valor == NAO_SEI else Estado.CONFIRMADO
        return self._com_fato(chave, replace(fato, estado=estado))

    def limpar(self, chave: str) -> "Caso":
        return self._com_fato(chave, Fato())

    def descartar_relato(self) -> "Caso":
        """Retira os fatos derivados do relato anterior; declarações diretas permanecem."""
        fatos = {
            chave: Fato() if fato.origem is Origem.RELATO else fato
            for chave, fato in self.fatos.items()
        }
        return Caso(fatos, self.revisao + 1, "")

    def aplicar_sugestoes(self, sugestoes: dict[str, Fato], versao_relato: str) -> "Caso":
        """Substitui os fatos do relato anterior pelas sugestões da nova análise.

        Campos sugeridos voltam a exigir conferência, inclusive os que tinham
        sido informados diretamente. Campos sem sugestão mantêm apenas
        declarações diretas.
        """
        sem_relato_anterior = self.descartar_relato()
        fatos = dict(sem_relato_anterior.fatos)
        for chave, sugestao in sugestoes.items():
            if not CAMPOS[chave].extraivel:
                raise ValueError(f"{chave} não pode ser sugerido pelo relato")
            if sugestao.origem is not Origem.RELATO or sugestao.estado not in ESTADOS_DE_SUGESTAO:
                raise ValueError(f"sugestão inválida para {chave}")
            fatos[chave] = sugestao
        return Caso(fatos, sem_relato_anterior.revisao + 1, versao_relato)

    def _com_fato(self, chave: str, fato: Fato) -> "Caso":
        if chave not in CAMPOS:
            raise KeyError(chave)
        return Caso({**self.fatos, chave: fato}, self.revisao + 1, self.versao_relato)


def resultado_ainda_vale(caso: Caso, revisao_no_pedido: int, relato_no_pedido: str, relato_atual: str) -> bool:
    """Uma extração atrasada só vale se nada mudou desde o pedido."""
    return caso.revisao == revisao_no_pedido and versao_do_relato(relato_no_pedido) == versao_do_relato(relato_atual)
