"""Regras revisadas que relacionam os fatos declarados ao recorte do Edital 01/2026.

Cada orientação declara as fontes em que se apoia e os fatos de que depende.
Orientação personalizada (Tipo.PASSO) só aparece quando todos os fatos de que
depende são conhecidos. Fato desconhecido gera pergunta factual, nunca
conclusão negativa. Caso fora do recorte é sinalizado como não avaliado, sem
afirmar ausência de direito ou de alternativa.

As regras não chamam o modelo e não decidem elegibilidade, dispensa ou
suficiência documental.
"""

from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum

from ponte.fatos import CAMPOS, Caso

LIMITE = (
    "Este plano consulta apenas orientações sobre saída da residência por alagação, "
    "incêndio ou outro evento adverso e perda de documentos pessoais. Outros requisitos "
    "do edital não foram avaliados. A análise do pedido é da Proaes."
)
JANELA_EM_DIAS = 90
ACONTECIMENTOS_NOMEADOS = {"alagacao": "alagação", "incendio": "incêndio"}
FATOS_DO_RAMO = (
    "aconteceu_com_voce",
    "acontecimento",
    "saiu_da_residencia",
    "perdeu_documentos",
    "data_evento",
    "data_referencia",
)


class Tipo(StrEnum):
    PASSO = "Passos relacionados às informações confirmadas"
    ESCLARECER = "Informações que você ainda pode esclarecer"
    PERGUNTA_PROAES = "Perguntas para a Proaes"
    REFERENCIA = "Informações gerais do edital"
    NAO_AVALIADO = "Não avaliado neste recorte"


@dataclass(frozen=True)
class Orientacao:
    chave: str
    tipo: Tipo
    titulo: str
    instrucao: str
    motivo: str
    fontes: tuple[str, ...]
    depende_de: tuple[str, ...] = ()
    pendencia: str = ""


@dataclass(frozen=True)
class Plano:
    orientacoes: tuple[Orientacao, ...]

    def do_tipo(self, tipo: Tipo) -> list[Orientacao]:
        return [orientacao for orientacao in self.orientacoes if orientacao.tipo is tipo]

    def chaves(self) -> set[str]:
        return {orientacao.chave for orientacao in self.orientacoes}


class Janela(StrEnum):
    DESCONHECIDA = "desconhecida"
    DATA_POSTERIOR = "data do acontecimento posterior à referência"
    DENTRO = "dentro"
    FORA = "fora"


@dataclass(frozen=True)
class Situacao:
    """Leitura dos fatos do ramo 2.2(b) + 6.9, calculada uma vez por plano."""

    janela: Janela
    dias: int | None
    faltando: tuple[str, ...]
    contrarios: tuple[tuple[str, str], ...]
    acontecimento_a_esclarecer: bool

    @property
    def personalizavel(self) -> bool:
        return not self.faltando and not self.contrarios and not self.acontecimento_a_esclarecer


def avaliar_janela(caso: Caso) -> tuple[Janela, int | None]:
    evento = caso.valor("data_evento")
    referencia = caso.valor("data_referencia")
    if not isinstance(evento, date) or not isinstance(referencia, date):
        return Janela.DESCONHECIDA, None
    dias = (referencia - evento).days
    if dias < 0:
        return Janela.DATA_POSTERIOR, dias
    return (Janela.DENTRO if dias <= JANELA_EM_DIAS else Janela.FORA), dias


def ler_situacao(caso: Caso) -> Situacao:
    janela, dias = avaliar_janela(caso)
    faltando: list[str] = []
    contrarios: list[tuple[str, str]] = []

    respostas_contrarias = {
        "aconteceu_com_voce": ("outra_pessoa", "Você informou que a situação aconteceu com outra pessoa."),
        "saiu_da_residencia": ("nao", "Você informou que não precisou sair da própria residência."),
        "perdeu_documentos": ("nao", "Você informou que não perdeu documentos pessoais."),
    }
    for chave, (valor_contrario, frase) in respostas_contrarias.items():
        valor = caso.valor(chave)
        if valor is None:
            faltando.append(chave)
        elif valor == valor_contrario:
            contrarios.append((chave, frase))

    if caso.valor("acontecimento") is None:
        faltando.append("acontecimento")

    if janela is Janela.DESCONHECIDA:
        faltando.extend(chave for chave in ("data_evento", "data_referencia") if caso.valor(chave) is None)
    elif janela is Janela.DATA_POSTERIOR:
        faltando.extend(("data_evento", "data_referencia"))
    elif janela is Janela.FORA:
        contrarios.append(
            (
                "data_evento",
                f"Pelas datas informadas, o acontecimento ocorreu {dias} dias antes da data de "
                f"referência, mais que os {JANELA_EM_DIAS} dias do item 2.2.2.",
            )
        )

    return Situacao(
        janela=janela,
        dias=dias,
        faltando=tuple(faltando),
        contrarios=tuple(contrarios),
        acontecimento_a_esclarecer=caso.valor("acontecimento") == "outro",
    )


def gerar_plano(caso: Caso) -> Plano:
    situacao = ler_situacao(caso)
    if caso.valor("aconteceu_com_voce") == "outra_pessoa":
        orientacoes = [
            *_item_6_9(caso, situacao),
            *_fora_do_recorte(situacao),
            *_item_6_8(caso),
            *_item_6_10(caso),
        ]
    else:
        orientacoes = [
            *_perguntas_factuais(caso, situacao),
            *_janela(caso, situacao),
            *_item_6_9(caso, situacao),
            *_enquadramento_do_acontecimento(caso, situacao),
            *_moradia(caso, situacao),
            *_item_6_8(caso),
            *_fora_do_recorte(situacao),
            *_item_6_10(caso),
        ]
    return Plano(tuple(orientacoes))


def _perguntas_factuais(caso: Caso, situacao: Situacao) -> list[Orientacao]:
    perguntas = {
        "aconteceu_com_voce": (
            "Informe se a situação aconteceu com você",
            "Responda se o acontecimento afetou você diretamente. Fatos sobre outra pessoa "
            "não são usados para relacionar o edital à sua situação.",
            "O item 2.2, alínea b, trata do próprio estudante.",
            ("2.2.b",),
        ),
        "acontecimento": (
            "Informe qual acontecimento você quer analisar",
            "Escolha um acontecimento por vez: alagação, incêndio ou outro evento.",
            "O item 2.2, alínea b, menciona alagação, incêndio ou outro evento adverso.",
            ("2.2.b",),
        ),
        "saiu_da_residencia": (
            "Informe se precisou sair da sua própria residência",
            "Responda se você precisou deixar a sua própria residência por causa desse "
            "acontecimento. Uma alagação no bairro ou na cidade, por si, não significa que "
            "você precisou sair.",
            "O item 2.2, alínea b, trata do estudante obrigado a sair da própria residência.",
            ("2.2.b",),
        ),
        "perdeu_documentos": (
            "Informe se perdeu documentos pessoais",
            "Responda se você perdeu documentos pessoais.",
            "O item 6.9 trata de quem está na situação da alínea b do item 2.2 e perdeu "
            "documentos pessoais.",
            ("6.9",),
        ),
    }
    orientacoes = []
    for chave, (titulo, instrucao, motivo, fontes) in perguntas.items():
        if chave in situacao.faltando:
            orientacoes.append(
                Orientacao(
                    chave=f"esclarecer.{chave}",
                    tipo=Tipo.ESCLARECER,
                    titulo=titulo,
                    instrucao=_com_nota(instrucao, caso, chave),
                    motivo=motivo,
                    fontes=fontes,
                    depende_de=(chave,),
                )
            )
    return orientacoes


def _janela(caso: Caso, situacao: Situacao) -> list[Orientacao]:
    motivo = (
        f"O item 2.2.2 considera acontecimentos ocorridos em até {JANELA_EM_DIAS} dias "
        "antes da solicitação do auxílio."
    )
    if situacao.janela is Janela.DATA_POSTERIOR:
        return [
            Orientacao(
                chave="esclarecer.datas",
                tipo=Tipo.ESCLARECER,
                titulo="Confira as datas informadas",
                instrucao="A data do acontecimento informada é posterior à data de referência. "
                "Corrija uma das datas.",
                motivo=motivo,
                fontes=("2.2.2",),
                depende_de=("data_evento", "data_referencia"),
            )
        ]
    if situacao.janela is Janela.DENTRO:
        evento = caso.valor("data_evento")
        prazo = evento + timedelta(days=JANELA_EM_DIAS)
        return [
            Orientacao(
                chave="2.2.2.prazo",
                tipo=Tipo.PASSO,
                titulo=f"Observe o prazo de {JANELA_EM_DIAS} dias do item 2.2.2",
                instrucao=f"Pelas datas informadas, o acontecimento ocorreu {situacao.dias} dias "
                f"antes da data de referência. Contando {JANELA_EM_DIAS} dias a partir do "
                f"acontecimento, o prazo vai até {prazo:%d/%m/%Y}.",
                motivo=motivo,
                fontes=("2.2.2",),
                depende_de=("data_evento", "data_referencia"),
                pendencia="Isso confere apenas a condição de prazo deste recorte, não o direito ao auxílio.",
            )
        ]
    orientacoes = []
    if caso.valor("data_evento") is None:
        orientacoes.append(
            Orientacao(
                chave="esclarecer.data_evento",
                tipo=Tipo.ESCLARECER,
                titulo="Informe a data do acontecimento",
                instrucao=_com_nota(
                    f"Falta informar a data para conferir a condição de {JANELA_EM_DIAS} dias do item 2.2.2.",
                    caso,
                    "data_evento",
                ),
                motivo=motivo,
                fontes=("2.2.2",),
                depende_de=("data_evento",),
            )
        )
    if caso.valor("data_referencia") is None:
        orientacoes.append(
            Orientacao(
                chave="esclarecer.data_referencia",
                tipo=Tipo.ESCLARECER,
                titulo="Confirme a data de referência",
                instrucao="A data de referência é o dia em que você pretende solicitar o auxílio. "
                "Confirme ou corrija essa data.",
                motivo=motivo,
                fontes=("2.2.2",),
                depende_de=("data_referencia",),
            )
        )
    return orientacoes


def _item_6_9(caso: Caso, situacao: Situacao) -> list[Orientacao]:
    if not situacao.personalizavel:
        return [_item_6_9_geral(situacao)]

    acontecimento = ACONTECIMENTOS_NOMEADOS[caso.valor("acontecimento")]
    motivo = (
        f"Você informou que precisou sair da própria residência por causa de {acontecimento} "
        "e que perdeu documentos pessoais."
    )
    orientacoes = [
        Orientacao(
            chave="6.9.documentos-disponiveis",
            tipo=Tipo.PASSO,
            titulo="Separe os documentos pessoais que você ainda possui",
            instrucao="O item 6.9 permite incluir no sistema de Bolsas e Auxílios os documentos que você possui.",
            motivo=motivo,
            fontes=("6.9",),
            depende_de=FATOS_DO_RAMO,
            pendencia="Isso organiza a preparação. Não garante que a documentação esteja completa para a inscrição.",
        ),
        Orientacao(
            chave="6.9.anexo-vi",
            tipo=Tipo.PASSO,
            titulo="Consulte a Justificativa do Auxílio Emergencial (Anexo VI)",
            instrucao="O item 6.9 menciona o Anexo VI. O formulário está na página 6 do pacote de "
            "anexos e inclui a opção de estudante obrigado a sair da própria residência.",
            motivo=motivo,
            fontes=("6.9", "anexo-vi.cabecalho"),
            depende_de=FATOS_DO_RAMO,
            pendencia="O cabeçalho do Anexo VI cita 2025 e o Edital 02/2025. Veja a pergunta sugerida para a Proaes.",
        ),
        Orientacao(
            chave="6.9.comprovantes",
            tipo=Tipo.PASSO,
            titulo="Reúna comprovantes da situação emergencial",
            instrucao="O item 8.3 cita como exemplos, para alagação ou incêndio: boletim de "
            "ocorrência, comprovante emitido por órgãos estaduais e/ou municipais e foto da "
            "residência nessa situação.",
            motivo=motivo,
            fontes=("6.9", "8.3", "anexo-vi.alagacao"),
            depende_de=FATOS_DO_RAMO,
            pendencia="A lista do edital termina em “etc” e é exemplificativa. A Ponte não avalia "
            "se um comprovante será aceito.",
        ),
        Orientacao(
            chave="6.9.anexo-vii",
            tipo=Tipo.PASSO,
            titulo="Consulte a Autodeclaração de Vulnerabilidade Socioeconômica (Anexo VII)",
            instrucao="O item 6.9 menciona o Anexo VII. O formulário está na página 7 do pacote de anexos.",
            motivo=motivo,
            fontes=("6.9", "anexo-vii.opcao"),
            depende_de=FATOS_DO_RAMO,
            pendencia="A única opção do formulário descreve quem recebeu bolsas ou auxílios nos "
            "últimos 3 anos. Veja a pergunta sugerida para a Proaes.",
        ),
        Orientacao(
            chave="proaes.versao-anexo-vi",
            tipo=Tipo.PERGUNTA_PROAES,
            titulo="Pergunte qual versão do Anexo VI usar",
            instrucao="Pergunta sugerida: “O Anexo VI publicado na página do Edital 01/2026 tem no "
            "cabeçalho ‘Justificativa do Auxílio Emergencial 2025 - Edital 02/2025’. Devo usar esse "
            "formulário?”",
            motivo="O cabeçalho cita outro ano e outro edital. A Ponte não conclui que o formulário seja inválido.",
            fontes=("anexo-vi.cabecalho", "6.9"),
            depende_de=FATOS_DO_RAMO,
        ),
    ]
    if caso.valor("beneficio_anterior") != "sim":
        orientacoes.append(
            Orientacao(
                chave="proaes.opcao-anexo-vii",
                tipo=Tipo.PERGUNTA_PROAES,
                titulo="Pergunte como preencher o Anexo VII na sua situação",
                instrucao="Pergunta sugerida: “O item 6.9 indica o Anexo VII para quem saiu da "
                "própria residência e perdeu documentos pessoais. A única opção do formulário é para "
                "quem foi contemplado com bolsas ou auxílios nos últimos 3 anos. Como devo proceder "
                "se essa opção não corresponder à minha situação?”",
                motivo="A Ponte não orienta a marcar uma opção que talvez não corresponda à sua situação.",
                fontes=("6.9", "anexo-vii.opcao"),
                depende_de=(*FATOS_DO_RAMO, "beneficio_anterior"),
            )
        )
    return orientacoes


def _item_6_9_geral(situacao: Situacao) -> Orientacao:
    if situacao.contrarios:
        motivo = "Não relacionado às informações atuais. " + " ".join(frase for _, frase in situacao.contrarios)
    elif situacao.faltando:
        rotulos = ", ".join(CAMPOS[chave].rotulo.lower() for chave in dict.fromkeys(situacao.faltando))
        motivo = f"Para relacionar este item à sua situação, falta informar ou confirmar: {rotulos}."
    else:
        motivo = "Depende de a Proaes esclarecer se o acontecimento se enquadra no item 2.2, alínea b."
    return Orientacao(
        chave="6.9.geral",
        tipo=Tipo.REFERENCIA,
        titulo="O que o item 6.9 prevê",
        instrucao="Para o estudante na situação da alínea b do item 2.2, por perda dos documentos "
        "pessoais, o item 6.9 prevê incluir no sistema os documentos que possui, o Anexo VI com os "
        "comprovantes da situação emergencial e o Anexo VII.",
        motivo=motivo,
        fontes=("6.9", "2.2.b"),
        depende_de=FATOS_DO_RAMO,
    )


def _enquadramento_do_acontecimento(caso: Caso, situacao: Situacao) -> list[Orientacao]:
    if not situacao.acontecimento_a_esclarecer or caso.valor("saiu_da_residencia") == "nao":
        return []
    descricao = caso.valor("descricao_acontecimento")
    acontecimento = f"({descricao})" if descricao else "(outro evento)"
    return [
        Orientacao(
            chave="proaes.enquadramento",
            tipo=Tipo.PERGUNTA_PROAES,
            titulo="Pergunte se o acontecimento se enquadra no item 2.2, alínea b",
            instrucao=f"Pergunta sugerida: “O acontecimento que vivi {acontecimento} se enquadra "
            "como ‘outro evento adverso’ do item 2.2, alínea b?”",
            motivo="O item menciona alagação, incêndio ou outro evento adverso. A Ponte não decide "
            "se um acontecimento diferente se enquadra.",
            fontes=("2.2.b",),
            depende_de=("acontecimento", "descricao_acontecimento", "saiu_da_residencia"),
        )
    ]


def _moradia(caso: Caso, situacao: Situacao) -> list[Orientacao]:
    if caso.valor("dificuldade_moradia") != "sim":
        return []
    motivo = (
        "Você informou dificuldade com comprovante de moradia ou contrato. O edital não esclarece "
        "como os itens 6.9 e 8.4 se relacionam; a Ponte não presume dispensa nem exigência adicional."
    )
    if situacao.personalizavel:
        return [
            Orientacao(
                chave="proaes.moradia",
                tipo=Tipo.PERGUNTA_PROAES,
                titulo="Pergunte como apresentar o comprovante de moradia",
                instrucao="Pergunta sugerida: “Considerando a situação descrita no item 6.9, como "
                "devo apresentar a documentação de moradia mencionada no item 8.4?”",
                motivo=motivo,
                fontes=("6.9", "8.4"),
                depende_de=(*FATOS_DO_RAMO, "dificuldade_moradia"),
            )
        ]
    return [
        Orientacao(
            chave="proaes.moradia",
            tipo=Tipo.PERGUNTA_PROAES,
            titulo="Pergunte como apresentar o comprovante de moradia",
            instrucao="Pergunta sugerida: “Tenho dificuldade para apresentar o comprovante de moradia "
            "do item 8.4. Como devo proceder?”",
            motivo="Você informou dificuldade com comprovante de moradia ou contrato.",
            fontes=("8.4",),
            depende_de=("dificuldade_moradia",),
        )
    ]


def _item_6_8(caso: Caso) -> list[Orientacao]:
    descricao = (
        "O item 6.8 trata de documentos exigidos no item 8 que não possam ser anexados por perda, "
        "roubo ou extravio e menciona Boletim de Ocorrência com prazo não superior a 6 meses da "
        "data do ocorrido."
    )
    if caso.valor("perdeu_documentos") == "sim" and caso.valor("aconteceu_com_voce") == "sim":
        return [
            Orientacao(
                chave="6.8",
                tipo=Tipo.PASSO,
                titulo="Consulte também o item 6.8",
                instrucao=descricao,
                motivo="Você informou que perdeu documentos pessoais.",
                fontes=("6.8",),
                depende_de=("perdeu_documentos", "aconteceu_com_voce"),
                pendencia="A Ponte não avaliou se o item 6.8 se aplica ao seu caso nem se ele "
                "substitui algum documento.",
            )
        ]
    return [
        Orientacao(
            chave="6.8",
            tipo=Tipo.REFERENCIA,
            titulo="Item 6.8: perda, roubo ou extravio de documentos",
            instrucao=descricao,
            motivo="Informação geral do edital, mostrada independentemente das suas respostas.",
            fontes=("6.8",),
        )
    ]


def _item_6_10(caso: Caso) -> list[Orientacao]:
    descricao = (
        "O item 6.10 prevê que quem foi beneficiário de bolsas ou auxílios da Assistência "
        "Estudantil da Ufac nos últimos 3 anos e ainda tem renda inferior a 1 salário-mínimo pode "
        "usar o Anexo VII no lugar da documentação de renda do item 8."
    )
    if caso.valor("beneficio_anterior") == "sim":
        return [
            Orientacao(
                chave="6.10",
                tipo=Tipo.NAO_AVALIADO,
                titulo="Item 6.10: benefício nos últimos 3 anos",
                instrucao=descricao,
                motivo="Você mencionou ter recebido benefício da assistência estudantil. Essa "
                "alternativa não foi avaliada pela Ponte.",
                fontes=("6.10",),
                depende_de=("beneficio_anterior",),
            )
        ]
    return [
        Orientacao(
            chave="6.10",
            tipo=Tipo.NAO_AVALIADO,
            titulo="Item 6.10: alternativa não avaliada",
            instrucao=descricao,
            motivo="A Ponte não avaliou essa alternativa.",
            fontes=("6.10",),
        )
    ]


def _fora_do_recorte(situacao: Situacao) -> list[Orientacao]:
    if not situacao.contrarios:
        return []
    fontes = ("2.2.1", "2.2.2") if situacao.janela is Janela.FORA else ("2.2.1",)
    return [
        Orientacao(
            chave="fora-do-recorte",
            tipo=Tipo.NAO_AVALIADO,
            titulo="Este recorte não cobre essa combinação de informações",
            instrucao="O recorte trata de estudante que precisou sair da própria residência por "
            "alagação, incêndio ou outro evento adverso e perdeu documentos pessoais. "
            + " ".join(frase for _, frase in situacao.contrarios),
            motivo="Isso não significa ausência de direito ou de outra alternativa. O item 2.2.1 "
            "prevê que outras situações excepcionais podem ser analisadas pela Comissão de Seleção "
            "da Proaes.",
            fontes=fontes,
            depende_de=tuple(chave for chave, _ in situacao.contrarios),
        )
    ]


def _com_nota(instrucao: str, caso: Caso, chave: str) -> str:
    nota = caso.fatos[chave].nota
    return f"{instrucao} {nota}" if nota else instrucao
