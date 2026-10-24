from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import streamlit as st

from ponte.extracao import FalhaNaExtracao, Extracao, extrair
from ponte.fatos import (
    CAMPOS,
    NAO_SEI,
    Caso,
    Estado,
    Fato,
    descrever_valor,
    versao_do_relato,
)
from ponte.fontes import EDITAL_01_2026 as EDITAL
from ponte.mudancas import comparar, descrever
from ponte.regras import LIMITE, Tipo, gerar_plano
from ponte.resumo import gerar_resumo

APP_DIR = Path(__file__).resolve().parent
FUSO_RIO_BRANCO = timezone(timedelta(hours=-5))
EXEMPLO_FICTICIO = (
    "No dia 10 de outubro de 2026, minha casa foi alagada. "
    "Precisei sair da minha residência e perdi meus documentos pessoais."
)

st.set_page_config(
    page_title="Ponte · Preparação documental",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');
      html, body, [class*="css"] { font-family: 'IBM Plex Sans', system-ui, sans-serif; }
      .block-container { max-width: 1120px; padding-top: 2rem; padding-bottom: 3rem; }
      .ponte-kicker { color: #52645c; font-size: .82rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase; }
      .ponte-note { border-left: 4px solid #1f5b47; padding: .8rem 1rem; background: #edf4ef; border-radius: .35rem; }
      div.stButton > button[kind="primary"] { background: #1f5b47; border-color: #1f5b47; }
      a { color: #1f5b47; }
    </style>
    """,
    unsafe_allow_html=True,
)


def data_local() -> date:
    return datetime.now(FUSO_RIO_BRANCO).date()


def chave_gemma() -> str:
    value = os.getenv("GEMINI_API_KEY", "").strip()
    if value:
        return value
    try:
        return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except Exception:
        return ""


def modelo_gemma() -> str:
    value = os.getenv("GEMMA_MODEL", "").strip()
    if value:
        return value
    try:
        return str(st.secrets.get("GEMMA_MODEL", "models/gemma-4-26b-a4b-it")).strip()
    except Exception:
        return "models/gemma-4-26b-a4b-it"


def inicializar_estado() -> None:
    st.session_state.setdefault("etapa", 0)
    st.session_state.setdefault("modo_entrada", "relato")
    st.session_state.setdefault("relato", "")
    st.session_state.setdefault("extracao", None)
    st.session_state.setdefault("caso", Caso.novo(data_local()))
    st.session_state.setdefault("plano_anterior", None)
    st.session_state.setdefault("caso_anterior", None)


def apagar_sessao() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    inicializar_estado()


def titulo() -> None:
    st.markdown('<p class="ponte-kicker">Protótipo independente</p>', unsafe_allow_html=True)
    st.title("Ponte")
    st.caption("Preparação documental com fontes · UFAC / Proaes")
    st.info(
        "A Ponte organiza fatos informados e próximos passos parciais. "
        "A Proaes é responsável pela análise e decisão do pedido."
    )


def cabecalho_etapas() -> None:
    labels = ["Contexto", "Sua situação", "Conferir fatos", "Próximos passos"]
    atual = st.session_state.etapa
    st.progress((atual + 1) / len(labels), text=f"Etapa {atual + 1} de {len(labels)} · {labels[atual]}")


def fonte_link(texto: str, url: str) -> None:
    st.link_button(texto, url, use_container_width=False)


def mostrar_fontes() -> None:
    st.markdown("#### Fontes oficiais")
    st.markdown(f"- [Página do edital]({EDITAL.pagina_oficial})")
    for documento in EDITAL.documentos.values():
        st.markdown(f"- [{documento.titulo}]({documento.url})")
    st.caption("Consulta registrada em 24/10/2026. Confira a página oficial para alterações e situação atual.")


def pagina_contexto() -> None:
    st.subheader("Prepare seus próximos passos")
    st.write(
        "Conte sua situação ou responda perguntas. Você poderá conferir e corrigir as informações "
        "antes de ver as orientações."
    )
    with st.container(border=True):
        st.markdown("**Edital Proaes nº 01/2026 · Auxílio Emergencial**")
        st.write(f"Universidade Federal do Acre · Processo {EDITAL.processo}")
        st.write(
            "Cobertura parcial: saída da própria residência por evento adverso e perda de documentos pessoais."
        )
        st.caption(
            "Outros requisitos não foram avaliados. A Ponte não confirma elegibilidade, autenticidade "
            "ou suficiência documental."
        )
        mostrar_fontes()

    st.radio(
        "Como prefere informar sua situação?",
        options=["Quero contar minha situação", "Prefiro responder perguntas"],
        key="modo_visivel",
        horizontal=True,
    )
    st.session_state.modo_entrada = (
        "relato" if st.session_state.modo_visivel == "Quero contar minha situação" else "perguntas"
    )
    if st.button("Começar", type="primary"):
        st.session_state.etapa = 1
        st.rerun()


def usar_exemplo() -> None:
    st.session_state.relato = EXEMPLO_FICTICIO


def pagina_situacao() -> None:
    st.subheader("Minha situação")
    st.write("Informe somente o necessário. Você pode deixar fatos desconhecidos sem resposta.")
    if st.session_state.modo_entrada == "relato":
        st.markdown(
            '<div class="ponte-note"><strong>Privacidade:</strong> o texto fica no estado da sessão '
            "processado pelo servidor da aplicação. Ao usar a análise do Gemma, o relato é enviado à "
            "Gemini API. Não inclua nomes, CPF, matrícula, endereço completo ou dados de terceiros. "
            "Para a cota gratuita da API, use somente exemplos fictícios.</div>",
            unsafe_allow_html=True,
        )
        if st.button("Usar exemplo fictício"):
            usar_exemplo()
        st.text_area(
            "Conte o que aconteceu",
            key="relato",
            height=170,
            placeholder="Exemplo: precisei sair da minha residência após um evento adverso...",
            help="Não envie fotos ou arquivos. O MVP analisa apenas o texto digitado.",
        )
        st.caption(f"{len(st.session_state.relato)} de 4.000 caracteres")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Analisar relato com Gemma", type="primary", use_container_width=True):
                relato = st.session_state.relato.strip()
                if not relato:
                    st.warning("Escreva uma situação ou use o exemplo fictício.")
                elif len(relato) > 4000:
                    st.error("O relato deve ter até 4.000 caracteres.")
                elif not chave_gemma():
                    st.error("A chave da Gemini API não está configurada. Você ainda pode responder às perguntas.")
                else:
                    try:
                        with st.spinner("Organizando sugestões para você conferir..."):
                            st.session_state.extracao = extrair(
                                relato,
                                chave_gemma(),
                                modelo=modelo_gemma(),
                            )
                        st.success("Análise concluída. Confira os fatos na próxima etapa.")
                        st.session_state.etapa = 2
                        st.rerun()
                    except (FalhaNaExtracao, ValueError) as erro:
                        st.error(f"Não foi possível analisar o relato: {erro}")
                        st.info("Você pode continuar respondendo às perguntas sem usar a análise.")
        with col2:
            if st.button("Continuar com perguntas", use_container_width=True):
                st.session_state.modo_entrada = "perguntas"
                st.session_state.etapa = 1
                st.rerun()
    else:
        formulario_perguntas()


def formulario_perguntas() -> None:
    caso: Caso = st.session_state.caso
    st.markdown(
        "Responda sobre um acontecimento por vez. O formulário não solicita documentos pessoais."
    )
    with st.form("perguntas_diretas"):
        valores: dict[str, object] = {}
        for chave, campo in CAMPOS.items():
            fato = caso.fatos[chave]
            if campo.tipo == "data":
                choices = ["Sem resposta", "Não sei", "Informar data"]
                if fato.estado in (Estado.NAO_SEI,):
                    default = "Não sei"
                elif isinstance(fato.valor, date):
                    default = "Informar data"
                else:
                    default = "Sem resposta"
                escolha = st.selectbox(
                    campo.pergunta,
                    choices,
                    index=choices.index(default),
                    key=f"direct_{chave}_state",
                )
                if escolha == "Informar data":
                    inicio = fato.valor if isinstance(fato.valor, date) else data_local()
                    valores[chave] = st.date_input(
                        f"{campo.rotulo} (dia/mês/ano)",
                        value=inicio,
                        format="DD/MM/YYYY",
                        key=f"direct_{chave}_date",
                    )
                else:
                    valores[chave] = NAO_SEI if escolha == "Não sei" else None
            elif campo.tipo == "texto":
                valores[chave] = st.text_input(
                    campo.pergunta,
                    value=str(fato.valor or ""),
                    key=f"direct_{chave}",
                )
            else:
                opcoes = campo.opcoes or {}
                labels = ["Sem resposta", *opcoes.values()]
                valor_atual = fato.valor
                atual_label = opcoes.get(valor_atual, "Sem resposta")
                if fato.estado is Estado.NAO_SEI:
                    atual_label = opcoes.get(NAO_SEI, "Não sei")
                escolha = st.selectbox(
                    campo.pergunta,
                    labels,
                    index=labels.index(atual_label) if atual_label in labels else 0,
                    key=f"direct_{chave}",
                )
                valores[chave] = next(
                    (valor for valor, label in opcoes.items() if label == escolha),
                    None,
                )
        enviado = st.form_submit_button("Conferir informações", type="primary")
    if enviado:
        atualizado = caso
        for chave, valor in valores.items():
            fato_atual = atualizado.fatos[chave]
            if valor is None or valor == "":
                atualizado = atualizado.limpar(chave)
            elif valor == NAO_SEI:
                atualizado = atualizado.informar(chave, NAO_SEI)
            elif fato_atual.valor == valor and fato_atual.estado in (Estado.CONFIRMADO, Estado.INFORMADO):
                continue
            else:
                atualizado = atualizado.informar(chave, valor)
        st.session_state.caso = atualizado
        st.session_state.extracao = None
        st.session_state.etapa = 2
        st.rerun()


def _valor_para_widget(chave: str, fato: Fato) -> object:
    if fato.valor is None:
        return None
    if chave in CAMPOS and CAMPOS[chave].tipo == "data":
        return fato.valor if isinstance(fato.valor, date) else None
    return fato.valor


def formulario_conferencia() -> None:
    caso: Caso = st.session_state.caso
    extracao: Extracao | None = st.session_state.extracao

    if extracao:
        st.markdown("**Sugestões do Gemma** · confira cada informação antes de usá-la.")
        if extracao.eventos:
            rotulos = [evento.rotulo for evento in extracao.eventos]
            indice = st.selectbox(
                "Qual acontecimento deseja analisar?",
                range(len(rotulos)),
                format_func=lambda i: rotulos[i],
                key="evento_escolhido",
            )
            sugestoes = extracao.sugestoes(indice)
            if extracao.eventos_descartados:
                st.caption(
                    f"{extracao.eventos_descartados} acontecimento(s) não puderam ser relacionado(s) "
                    "a trechos do relato e não serão usados."
                )
        else:
            st.info("Não foi possível identificar um acontecimento. Confira as informações gerais sugeridas.")
            sugestoes = extracao.sugestoes(None)
        if st.button("Aplicar sugestões para conferir", type="primary"):
            st.session_state.caso = caso.aplicar_sugestoes(
                sugestoes,
                versao_do_relato(st.session_state.relato),
            )
            st.session_state.extracao = None
            st.rerun()

    caso = st.session_state.caso
    st.markdown("Revise as informações. Sugestões do relato ainda não estão confirmadas.")
    if caso.versao_relato and st.session_state.relato:
        st.caption("O relato permanece nesta sessão para permitir conferência dos trechos. Ele não é salvo em histórico.")

    with st.form("revisar_fatos"):
        valores: dict[str, object] = {}
        for chave, campo in CAMPOS.items():
            fato = caso.fatos[chave]
            if fato.estado is Estado.SEM_RESPOSTA and campo.so_do_relato:
                continue
            with st.container(border=True):
                st.markdown(f"**{campo.pergunta}**")
                if fato.trecho:
                    st.caption(f'Trecho do relato: “{fato.trecho}”')
                if fato.nota:
                    st.warning(fato.nota)
                if campo.tipo == "data":
                    state_options = ["Sem resposta", "Não sei", "Informar data"]
                    if fato.estado is Estado.NAO_SEI:
                        estado_inicial = "Não sei"
                    elif isinstance(fato.valor, date):
                        estado_inicial = "Informar data"
                    else:
                        estado_inicial = "Sem resposta"
                    state = st.selectbox(
                        "Estado",
                        state_options,
                        index=state_options.index(estado_inicial),
                        key=f"review_{chave}_state",
                    )
                    if state == "Informar data":
                        current = fato.valor if isinstance(fato.valor, date) else data_local()
                        valor = st.date_input(
                            campo.rotulo,
                            value=current,
                            format="DD/MM/YYYY",
                            key=f"review_{chave}_date",
                        )
                        valores[chave] = valor
                    else:
                        valores[chave] = NAO_SEI if state == "Não sei" else None
                elif campo.tipo == "texto":
                    valores[chave] = st.text_input(
                        campo.rotulo,
                        value=str(fato.valor or ""),
                        key=f"review_{chave}",
                    )
                else:
                    opcoes = campo.opcoes or {}
                    labels = ["Sem resposta", *opcoes.values()]
                    atual = opcoes.get(fato.valor, "Sem resposta")
                    escolha = st.selectbox(
                        campo.rotulo,
                        labels,
                        index=labels.index(atual) if atual in labels else 0,
                        key=f"review_{chave}",
                    )
                    valores[chave] = next(
                        (valor for valor, label in opcoes.items() if label == escolha),
                        None,
                    )
        enviado = st.form_submit_button("Salvar correções e ver próximos passos", type="primary")
    if enviado:
        antes = caso
        plano_antes = gerar_plano(antes)
        atualizado = antes
        for chave, valor in valores.items():
            fato_atual = atualizado.fatos[chave]
            if valor is None or valor == "":
                if fato_atual.estado is not Estado.SEM_RESPOSTA:
                    atualizado = atualizado.limpar(chave)
            elif valor == NAO_SEI:
                if fato_atual.estado is not Estado.NAO_SEI:
                    atualizado = atualizado.informar(chave, NAO_SEI)
            elif fato_atual.valor == valor and fato_atual.estado in (Estado.CONFIRMADO, Estado.INFORMADO):
                continue
            elif fato_atual.valor == valor and fato_atual.estado is Estado.A_CONFERIR:
                atualizado = atualizado.confirmar(chave)
            else:
                atualizado = atualizado.informar(chave, valor)
        plano_depois = gerar_plano(atualizado)
        st.session_state.caso_anterior = antes
        st.session_state.plano_anterior = plano_antes
        st.session_state.caso = atualizado
        st.session_state.etapa = 3
        st.session_state.plano_depois = plano_depois
        st.rerun()


def pagina_conferencia() -> None:
    st.subheader("Conferir informações")
    formulario_conferencia()


def mostrar_orientacao(orientacao) -> None:
    with st.container(border=True):
        st.markdown(f"**{orientacao.titulo}**")
        st.write(orientacao.instrucao)
        if orientacao.pendencia:
            st.warning(orientacao.pendencia)
        if orientacao.motivo:
            st.caption(f"Por que aparece: {orientacao.motivo}")
        for chave in orientacao.fontes:
            trecho = EDITAL.trecho(chave)
            documento = EDITAL.documento_do_trecho(chave)
            with st.expander(f"Fonte: {EDITAL.citar(chave)}"):
                st.write(trecho.texto)
                if trecho.observacao:
                    st.info(trecho.observacao)
                st.link_button(f"Abrir {documento.titulo}", documento.url)
                st.link_button("Abrir página oficial do edital", EDITAL.pagina_oficial)


def pagina_resultado() -> None:
    st.subheader("Próximos passos e resumo")
    caso: Caso = st.session_state.caso
    plano = gerar_plano(caso)
    anterior = st.session_state.get("caso_anterior")
    plano_anterior = st.session_state.get("plano_anterior")
    if anterior is not None and plano_anterior is not None:
        mudancas = comparar(anterior, plano_anterior, caso, plano)
        if mudancas:
            st.markdown("### O que mudou")
            for mudanca in mudancas:
                st.write(descrever(mudanca, anterior, caso))
    for tipo in Tipo:
        orientacoes = plano.do_tipo(tipo)
        if not orientacoes:
            continue
        st.markdown(f"### {tipo.value}")
        for orientacao in orientacoes:
            mostrar_orientacao(orientacao)
    st.info(LIMITE)
    st.markdown("### Resumo copiável")
    resumo = gerar_resumo(caso, plano, EDITAL)
    st.text_area(
        "Selecione e copie o resumo atualizado",
        value=resumo,
        height=320,
        help="O resumo é gerado a partir dos fatos atuais desta sessão.",
    )
    st.download_button(
        "Baixar resumo em texto",
        data=resumo.encode("utf-8"),
        file_name="resumo-ponte.txt",
        mime="text/plain",
    )
    st.caption(
        "O resumo é baixado pelo seu navegador quando você solicita. A Ponte não cria uma cópia "
        "persistente do arquivo no servidor."
    )


def rodape_privacidade() -> None:
    st.divider()
    st.caption(
        "Protótipo independente. Sem cadastro, upload ou banco de casos. "
        "A sessão é processada pelo servidor do Streamlit; o relato é enviado à Gemini API somente "
        "quando você escolhe analisá-lo com Gemma. Não use dados pessoais reais na demonstração."
    )


def main() -> None:
    inicializar_estado()
    titulo()
    cabecalho_etapas()
    etapa = st.session_state.etapa
    if etapa == 0:
        pagina_contexto()
    elif etapa == 1:
        pagina_situacao()
    elif etapa == 2:
        pagina_conferencia()
    else:
        pagina_resultado()

    if etapa > 0:
        cols = st.columns([1, 1, 4])
        with cols[0]:
            if st.button("Voltar etapa", disabled=etapa == 0):
                st.session_state.etapa = max(0, etapa - 1)
                st.rerun()
        with cols[1]:
            st.button("Apagar sessão", on_click=apagar_sessao)
    rodape_privacidade()


if __name__ == "__main__":
    main()



