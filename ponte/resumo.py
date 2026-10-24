"""Resumo copiável, derivado apenas do estado atual do caso."""

from ponte.fatos import CAMPOS, Caso, Estado, descrever_valor
from ponte.fontes import Edital
from ponte.regras import LIMITE, Orientacao, Plano, Tipo


def gerar_resumo(caso: Caso, plano: Plano, edital: Edital) -> str:
    linhas = [
        "Resumo preparado com a Ponte (protótipo independente, sem vínculo oficial com a Ufac)",
        "",
        f"Edital: {edital.instituicao}, {edital.orgao}, Edital nº {edital.numero}, processo {edital.processo}.",
        f"Fontes consultadas em {_data_de_consulta(edital)}. Situação das inscrições: consulte a página oficial.",
        "",
        "Informações declaradas",
    ]
    declarados, pendentes = [], []
    for chave, fato in caso.fatos.items():
        if fato.estado is Estado.SEM_RESPOSTA:
            continue
        estado = "" if fato.estado is Estado.NAO_SEI else f" ({fato.estado.value.lower()})"
        linha = f"- {CAMPOS[chave].rotulo}: {descrever_valor(chave, fato)}{estado}"
        (declarados if fato.conhecido else pendentes).append(linha)
    linhas += declarados or ["- Nenhuma informação confirmada."]
    linhas += ["", "Informações desconhecidas ou a conferir"]
    sem_resposta = [
        f"- {CAMPOS[chave].rotulo}: sem resposta"
        for chave, fato in caso.fatos.items()
        if fato.estado is Estado.SEM_RESPOSTA and not CAMPOS[chave].so_do_relato and CAMPOS[chave].tipo != "texto"
    ]
    linhas += pendentes + sem_resposta or ["- Nenhuma."]

    for tipo in Tipo:
        orientacoes = plano.do_tipo(tipo)
        if orientacoes:
            linhas += ["", tipo.value]
            linhas += [_linha_da_orientacao(numero, orientacao, edital) for numero, orientacao in enumerate(orientacoes, 1)]

    linhas += ["", "Documentos oficiais"]
    linhas += [f"- Página do edital: {edital.pagina_oficial}"]
    linhas += [f"- {documento.titulo}: {documento.url}" for documento in edital.documentos.values()]
    linhas += [f"- Dúvidas: {', '.join(edital.canais_de_duvida)}"]
    linhas += ["", f"Limite: {LIMITE}"]
    return "\n".join(linhas)


def _linha_da_orientacao(numero: int, orientacao: Orientacao, edital: Edital) -> str:
    partes = [f"{numero}. {orientacao.titulo}. {orientacao.instrucao}"]
    if orientacao.pendencia:
        partes.append(f"Observação: {orientacao.pendencia}")
    partes.append("Fonte: " + "; ".join(edital.citar(chave) for chave in orientacao.fontes) + ".")
    return " ".join(partes)


def _data_de_consulta(edital: Edital) -> str:
    datas = sorted({documento.consultado_em for documento in edital.documentos.values()})
    return ", ".join(f"{data:%d/%m/%Y}" for data in datas)
