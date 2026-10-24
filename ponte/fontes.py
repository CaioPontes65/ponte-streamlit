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
        chave="2.2.a",
        rotulo="Item 2.2, alínea a",
        documento="edital",
        pagina=2,
        texto=(
            "Falecimento recente do provedor principal pela renda familiar, desde "
            "que o estudante e/ou o grupo familiar não estejam recebendo pensão;"
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
        chave="2.2.c",
        rotulo="Item 2.2, alínea c",
        documento="edital",
        pagina=2,
        texto=(
            "Estudantes ingressantes, oriundos de outro Estado da Federação ou de "
            "municípios do Acre de difícil acesso, que não possui parentes nos "
            "municípios de Rio Branco e Cruzeiro do Sul e nem condições financeiras "
            "para o custeio de moradia."
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
        chave="4.2",
        rotulo="Item 4.2",
        documento="edital",
        pagina=2,
        texto="Estar cursando a primeira graduação (Anexo IV);",
    ),
    Trecho(
        chave="4.3",
        rotulo="Item 4.3",
        documento="edital",
        pagina=2,
        texto="Não estar cursando outra graduação em Instituição de Ensino Superior (Anexo IV);",
    ),
    Trecho(
        chave="4.5",
        rotulo="Item 4.5",
        documento="edital",
        pagina=2,
        texto="Estar em alguma das situações descritas no item 2.2 deste Edital;",
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
        chave="8.2",
        rotulo="Item 8.2",
        documento="edital",
        pagina=4,
        texto=(
            "Documentação acadêmica (apenas do estudante): a) Declaração de que não "
            "possui matrícula em outra instituição de ensino superior, bem como não "
            "é portador de diploma de nível superior (com data atualizada), "
            "preenchida e assinada pelo estudante (Anexo IV)."
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
        chave="8.5",
        rotulo="Item 8.5",
        documento="edital",
        pagina=4,
        texto=(
            "Documentação de comprovação de Renda (do estudante e de todos os "
            "membros do grupo familiar maiores de 18 anos):"
        ),
    ),
    Trecho(
        chave="8.5.1",
        rotulo="Item 8.5.1",
        documento="edital",
        pagina=4,
        texto=(
            "Grupo familiar com Benefício Social do Programa Bolsa Família: a) Cópia "
            "da Folha Resumo do Cadastro Único atualizada disponível em: "
            "https://cadunico.dataprev.gov.br/#/consultaSimples ; b) Último extrato "
            "de recebimento do benefício; c) Declaração de beneficiário do Bolsa "
            "Família (substituindo todas as outras documentações de renda) conforme "
            "Anexo VIII."
        ),
        observacao="A alínea c está na página 5.",
    ),
    Trecho(
        chave="8.5.1.1",
        rotulo="Item 8.5.1.1",
        documento="edital",
        pagina=5,
        texto=(
            "O estudante deverá fazer parte do grupo familiar constante na Folha "
            "Resumo do Cadúnico apresentada na inscrição. Em caso de divergência, a "
            "inscrição será indeferida e no recurso deverá ser incluída todas as "
            "demais documentações de comprovação de renda de todo o grupo familiar, "
            "constante no item 8.5."
        ),
    ),
    Trecho(
        chave="8.5.4",
        rotulo="Item 8.5.4, alínea a",
        documento="edital",
        pagina=5,
        texto=(
            "Em caso de Trabalhador autônomo e/ou informal: a) Declaração de "
            "trabalho autônomo e/ou informal (com data atualizada) informando "
            "atividade exercida e a renda média mensal (com assinatura por extenso, "
            "manuscrita e igual ao documento identidade apresentado), conforme "
            "Anexo III;"
        ),
        observacao=(
            "As alíneas b a d, nas páginas 5 e 6, tratam de Carteira de Trabalho "
            "Digital, extratos bancários dos três últimos meses e de quem não "
            "possui conta bancária."
        ),
    ),
    Trecho(
        chave="8.5.5",
        rotulo="Item 8.5.5, alínea a",
        documento="edital",
        pagina=6,
        texto=(
            "Em caso de desemprego: a) Declaração de desemprego (com data "
            "atualizada), conforme Anexo II (com assinatura por extenso, manuscrita "
            "e conforme documentação oficial);"
        ),
        observacao=(
            "As alíneas b a e tratam de Carteira de Trabalho Digital, extratos "
            "bancários dos três últimos meses e de quem não possui conta bancária."
        ),
    ),
    Trecho(
        chave="8.5.7.b",
        rotulo="Item 8.5.7, alínea b",
        documento="edital",
        pagina=6,
        texto=(
            "Em caso de recebimento de pensão alimentícia, apresentar termo de "
            "audiência ou declaração assinada, onde conste o valor da pensão "
            "recebida. Caso receba ou não pensão alimentícia, apresentar declaração "
            "de pensão alimentícia (ANEXO V);"
        ),
        observacao="O texto começa na página 6 e termina na página 7.",
    ),
    Trecho(
        chave="anexo-ii.declaracao",
        rotulo="Anexo II, declaração de desemprego",
        documento="anexos",
        pagina=2,
        texto="estou desempregado (a) no momento e meu sustento tem sido proveniente de:",
    ),
    Trecho(
        chave="anexo-iii.observacao",
        rotulo="Anexo III, observação",
        documento="anexos",
        pagina=3,
        texto=(
            "Observação: não serão aceitas declarações que não contenha as "
            "informações solicitadas com o valor da renda média e a atividade "
            "exercida e sem as devidas assinaturas."
        ),
    ),
    Trecho(
        chave="anexo-iv.declaracao",
        rotulo="Anexo IV, declaração",
        documento="anexos",
        pagina=4,
        texto=(
            "não possuo vínculo acadêmico com outra instituição de ensino superior, "
            "bem como não sou portador (a) de diploma de Nível Superior."
        ),
    ),
    Trecho(
        chave="anexo-v.opcoes",
        rotulo="Anexo V, opções de declaração",
        documento="anexos",
        pagina=5,
        texto=(
            "RECEBO ( ) o valor mensal de R$ ____ referente à pensão "
            "alimentícia/auxílio financeiro em meu nome ou em nome de dependentes. "
            "NÃO RECEBO ( ) nenhum valor mensal referente à pensão "
            "alimentícia/auxílio financeiro em meu nome ou em nome de dependentes."
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
        chave="anexo-vi.falecimento",
        rotulo="Anexo VI, opção de falecimento",
        documento="anexos",
        pagina=6,
        texto=(
            "Falecimento recente do provedor principal pela renda familiar, desde "
            "que o estudante e/ou o grupo familiar não estejam recebendo pensão;"
        ),
    ),
    Trecho(
        chave="anexo-vi.ingressante",
        rotulo="Anexo VI, opção de ingressante",
        documento="anexos",
        pagina=6,
        texto=(
            "Estudante ingressantes, oriundo de outro Estado da Federação ou de "
            "municípios do Acre de difícil acesso, que não possui parentes nos "
            "municípios de Rio Branco e Cruzeiro do Sul e nem condições financeiras "
            "para o custeio de moradia."
        ),
    ),
    Trecho(
        chave="anexo-vi.obito",
        rotulo="Anexo VI, comprovantes de falecimento",
        documento="anexos",
        pagina=6,
        texto="Certidão de óbito e comprovante que não vai receber pensão;",
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
        chave="anexo-vi.outra-localidade",
        rotulo="Anexo VI, comprovantes de outra localidade",
        documento="anexos",
        pagina=6,
        texto=(
            "Para quem vem de outra localidade: fatura de energia da residência de "
            "origem e outros documentos que sejam relevantes."
        ),
    ),
    Trecho(
        chave="anexo-vi.outros",
        rotulo="Anexo VI, outros comprovantes",
        documento="anexos",
        pagina=6,
        texto="Outros: Quais?",
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
    Trecho(
        chave="anexo-viii.declaracao",
        rotulo="Anexo VIII, declaração",
        documento="anexos",
        pagina=8,
        texto=(
            "declaro, sob as penas a lei, ser beneficiário do Programa de "
            "transferência direta do governo federal - Bolsa Família e este "
            "benefício, representa a principal fonte de renda do meu grupo familiar."
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
