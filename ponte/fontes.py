"""Fontes revisadas do recorte do Edital Proaes nº 01/2026 da UFAC.

Os trechos foram transcritos das cópias em fontes/ufac-proaes-01-2026/, obtidas
nas URLs oficiais em 24/10/2026. Quebras de linha e espaços extras da extração
do PDF foram normalizados; a grafia original foi mantida, inclusive desvios
como "necessidades básica". tests/test_fontes.py confere cada trecho contra a
página indicada do PDF e o hash de cada cópia.

Este módulo registra o que o edital diz. A relação entre fatos e orientações
fica em ponte/regras.py.
"""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Documento:
    chave: str
    titulo: str
    url: str
    arquivo_local: str
    sha256: str
    paginas: int
    consultado_em: date


@dataclass(frozen=True)
class Trecho:
    chave: str
    rotulo: str
    documento: str
    pagina: int
    texto: str
    observacao: str = ""


@dataclass(frozen=True)
class Edital:
    instituicao: str
    orgao: str
    numero: str
    processo: str
    objeto: str
    assinado_em: date
    pagina_oficial: str
    canais_de_duvida: tuple[str, ...]
    conferencia_de_alteracoes: str
    documentos: dict[str, Documento]
    trechos: dict[str, Trecho]

    def trecho(self, chave: str) -> Trecho:
        return self.trechos[chave]

    def documento_do_trecho(self, chave: str) -> Documento:
        return self.documentos[self.trechos[chave].documento]

    def citar(self, chave: str) -> str:
        trecho = self.trechos[chave]
        documento = self.documentos[trecho.documento]
        return f"{trecho.rotulo} ({documento.titulo}, p. {trecho.pagina})"


CONSULTA = date(2026, 10, 24)
PAGINA_OFICIAL = (
    "https://www3.ufac.br/proaes/2026/"
    "edital-ndeg-01-2026-proaes-selecao-do-programa-de-auxilio-emergencial-e-01-26"
)

_DOCUMENTOS = (
    Documento(
        chave="edital",
        titulo="Edital nº 01/2026, SEI 1956124",
        url=f"{PAGINA_OFICIAL}/sei_1956124_edital_01.pdf",
        arquivo_local="fontes/ufac-proaes-01-2026/sei_1956124_edital_01.pdf",
        sha256="4e5a84cb1277d43f14cdef9a9480ee36a14096ee798184bf459ee7a23b1129c6",
        paginas=9,
        consultado_em=CONSULTA,
    ),
    Documento(
        chave="anexos",
        titulo="Anexos - Auxílio Emergencial 2026",
        url=f"{PAGINA_OFICIAL}/anexos-auxilio-emergencial-2026.pdf",
        arquivo_local="fontes/ufac-proaes-01-2026/anexos-auxilio-emergencial-2026.pdf",
        sha256="220e904a5f6f25e061437d33d8a1755b3000755a190c58b3bc56c6ffe98fb16c",
        paginas=8,
        consultado_em=CONSULTA,
    ),
)

_TRECHOS = (
    Trecho(
        chave="2.2",
        rotulo="Item 2.2",
        documento="edital",
        pagina=2,
        texto=(
            "Caracteriza-se por emergência, para fins de cobertura deste Auxílio, "
            "a incapacidade temporária de suprir as necessidades básicas, "
            "prioritariamente nos aspectos de moradia e alimentação do estudante "
            "universitário, a saber:"
        ),
    ),
    Trecho(
        chave="2.2.b",
        rotulo="Item 2.2, alínea b",
        documento="edital",
        pagina=2,
        texto=(
            "Estudante obrigado a sair da própria residência em virtude da "
            "ocorrência de alagação, incêndio ou outro evento adverso;"
        ),
    ),
    Trecho(
        chave="2.2.1",
        rotulo="Item 2.2.1",
        documento="edital",
        pagina=2,
        texto=(
            "Excepcionalmente, outras situações de vulnerabilidade extrema geradas "
            "por situações inesperadas, não descritas nos subitens anteriores, "
            "poderão ser analisadas pela Comissão de Seleção da Proaes."
        ),
    ),
    Trecho(
        chave="2.2.2",
        rotulo="Item 2.2.2",
        documento="edital",
        pagina=2,
        texto=(
            "A situação será considerada emergência se o fator motivador da "
            "incapacidade temporária no suprimento das necessidades básica tiver "
            "ocorrido em no máximo 90 dias anteriores à solicitação do presente "
            "auxílio."
        ),
        observacao=(
            "O resultado final da 11ª chamada, de 08/10/2026, repete a regra: "
            "o auxílio pode ser solicitado em até 90 dias da ocorrência do "
            "evento adverso."
        ),
    ),
    Trecho(
        chave="5.3",
        rotulo="Item 5.3",
        documento="edital",
        pagina=3,
        texto=(
            "Este edital será de fluxo contínuo e terá vigência até 31 de dezembro "
            "de 2026 e/ou até a utilização de todo o recurso orçamentário previsto;"
        ),
        observacao="Vigência do edital não confirma que as inscrições estejam abertas hoje.",
    ),
    Trecho(
        chave="6.8",
        rotulo="Item 6.8",
        documento="edital",
        pagina=3,
        texto=(
            "Caso o estudante não possa anexar algum dos documentos exigidos no "
            "Item 08 deste Edital, em virtude de perda, roubo, ou extravio, anexar "
            "Boletim de Ocorrência com prazo não superior à 06 (seis) meses da data "
            "do ocorrido;"
        ),
    ),
    Trecho(
        chave="6.9",
        rotulo="Item 6.9",
        documento="edital",
        pagina=3,
        texto=(
            "Caso o estudante esteja na situação prevista na alínea (b) do item "
            "2.2, por perda dos documentos pessoais, poderá incluir no sistema de "
            "Bolsas e Auxílios os documentos que possui, o Anexo VI (Justificativa "
            "de Auxílio Emergencial) juntamente com os comprovantes da situação "
            "emergencial e o Anexo VII (Autodeclaração de Vulnerabilidade "
            "Socioeconômica);"
        ),
    ),
    Trecho(
        chave="6.10",
        rotulo="Item 6.10",
        documento="edital",
        pagina=3,
        texto=(
            "Caso o estudante tenha sido beneficiário(a) das bolsas ou auxílios da "
            "Assistência Estudantil/Pnaes da Ufac nos últimos 3 anos e ainda "
            "possuir renda inferior a 1 salário-mínimo, poderá aproveitar a "
            "documentação através do Anexo VII (Autodeclaração de Vulnerabilidade "
            "Socioeconômica), substituindo a documentação de renda solicitada no "
            "Item 8 do Edital;"
        ),
    ),
    Trecho(
        chave="8.3",
        rotulo="Item 8.3",
        documento="edital",
        pagina=4,
        texto=(
            "Documentação comprobatória da situação emergencial: a) Justificativa "
            "do Auxílio Emergencial (Anexo VI) com a documentação comprobatória, "
            "nos casos de Falecimento: Certidão de óbito e comprovante que não vai "
            "receber pensão; Alagação ou incêndio: boletim de ocorrência, "
            "comprovante emitido por órgãos estaduais e/ou municipais, foto da "
            "residência nessa situação, etc; Estudantes oriundos de outras "
            "localidades: fatura de energia da residência de origem e outros "
            "documentos que sejam relevantes;"
        ),
        observacao="A enumeração termina em \"etc\"; é exemplificativa, não uma lista fechada.",
    ),
    Trecho(
        chave="8.4",
        rotulo="Item 8.4",
        documento="edital",
        pagina=4,
        texto=(
            "Comprovantes de Moradia (do estudante e de todos os membros do grupo "
            "familiar): a) Imóvel próprio: Cópia da fatura de energia atualizada do "
            "imóvel onde reside (Caso todos os membros do grupo familiar residam na "
            "mesma casa, apresentar somente uma cópia da fatura de energia). Não "
            "serão aceitas cópias cortadas, ilegíveis, incompletas, sem "
            "identificação de titular e/ou endereço. b) Imóvel cedido: Cópia da "
            "fatura de energia atualizada do imóvel onde reside (Caso todos os "
            "membros do grupo familiar residam na mesma casa, apresentar somente "
            "uma cópia da fatura de energia) e Declaração de cessão do imóvel. Não "
            "serão aceitas cópias cortadas, ilegíveis, incompletas, sem "
            "identificação de titular e/ou endereço. c) Imóvel alugado: Cópia da "
            "fatura de energia atualizada do imóvel onde reside (Caso todos os "
            "membros do grupo familiar residam na mesma casa, apresentar somente "
            "uma cópia da fatura de energia) e Contrato de aluguel. Não serão "
            "aceitas cópias cortadas, ilegíveis, incompletas, sem identificação de "
            "titular e/ou endereço."
        ),
    ),
    Trecho(
        chave="anexo-vi.cabecalho",
        rotulo="Anexo VI, cabeçalho",
        documento="anexos",
        pagina=6,
        texto="JUSTIFICATIVA DO AUXÍLIO EMERGENCIAL 2025 - Edital 02/2025",
        observacao=(
            "O cabeçalho cita 2025 e o Edital 02/2025, enquanto a linha de data do "
            "mesmo formulário traz 2026. Não está claro qual versão usar."
        ),
    ),
    Trecho(
        chave="anexo-vi.alagacao",
        rotulo="Anexo VI, documentos comprobatórios",
        documento="anexos",
        pagina=6,
        texto=(
            "Alagação ou incêndio: boletim de ocorrência, comprovante emitido pelos "
            "órgãos estaduais e/ou municipais, fotos da residência nessa situação, "
            "entre outros;"
        ),
    ),
    Trecho(
        chave="anexo-vii.opcao",
        rotulo="Anexo VII, opção de declaração",
        documento="anexos",
        pagina=7,
        texto=(
            "contemplado com bolsas ou auxílios da Assistência Estudantil/Pnaes da "
            "Ufac nos últimos 3 anos e ainda possuo renda inferior a 1 "
            "salário-mínimo;"
        ),
        observacao=(
            "É a única opção marcável do formulário e descreve quem já recebeu "
            "benefício. O item 6.9 indica o Anexo VII também para a situação da "
            "alínea (b), que pode não corresponder a essa opção."
        ),
    ),
)

EDITAL_01_2026 = Edital(
    instituicao="Universidade Federal do Acre",
    orgao="Pró-Reitoria de Assuntos Estudantis (Proaes)",
    numero="01/2026",
    processo="23107.000688/2026-82",
    objeto="Edital de Seleção do Programa de Auxílio Emergencial (E-01/26)",
    assinado_em=date(2026, 1, 23),
    pagina_oficial=PAGINA_OFICIAL,
    canais_de_duvida=(
        "coaps.dae@ufac.br (Campus Sede)",
        "proaesczs@ufac.br (Campus Floresta)",
    ),
    conferencia_de_alteracoes=(
        "Em 24/10/2026, a listagem da página oficial não continha adendo nem "
        "retificação; havia resultados de chamadas até a 11ª, de 08/10/2026."
    ),
    documentos={documento.chave: documento for documento in _DOCUMENTOS},
    trechos={trecho.chave: trecho for trecho in _TRECHOS},
)
