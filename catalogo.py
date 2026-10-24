from __future__ import annotations
from datetime import date
import streamlit as st

# Catálogo equivalente ao protótipo React. Somente a linha UFAC tem fonte documental
# vinculada; as demais são fixtures fictícias e aparecem rotuladas como demonstração.
EDITAIS = [
 dict(id='ufac-01-2026',inst='UFAC · Campus Rio Branco',uf='AC',numero='Edital 01/2026',titulo='Programa de Auxílio Emergencial',area='Assistência estudantil',tipo='Auxílio emergencial',publico='Graduação',inicio='2026-10-05',fim='2026-11-06',valor=None,resumo='Seleção para auxílio emergencial. Inclui situações de saída da própria residência por evento adverso e perda de documentos pessoais.',real=True,url='https://www3.ufac.br/proaes/2026/edital-ndeg-01-2026-proaes-selecao-do-programa-de-auxilio-emergencial-e-01-26'),
 dict(id='ufac-03-2026',inst='UFAC · Campus Rio Branco',uf='AC',numero='Edital 03/2026',titulo='Auxílio Moradia',area='Assistência estudantil',tipo='Moradia',publico='Graduação',inicio='2026-09-20',fim='2026-10-30',valor=500,resumo='Apoio mensal para estudantes que moram longe da família e pagam aluguel.'),
 dict(id='ufac-12-2026',inst='UFAC · Campus Rio Branco',uf='AC',numero='Edital 12/2026',titulo='PIBIC 2026–2027',area='Pesquisa',tipo='Iniciação científica',publico='Graduação',inicio='2026-08-15',fim='2026-09-15',valor=700,resumo='Bolsas de iniciação científica vinculadas a projetos de docentes orientadores.'),
 dict(id='ufac-07-2026',inst='UFAC · Campus Rio Branco',uf='AC',numero='Edital 07/2026',titulo='Bolsas de extensão universitária',area='Extensão',tipo='Extensão',publico='Graduação',inicio='2026-11-03',fim='2026-11-24',valor=700,resumo='Bolsas para atuação em projetos e programas de extensão com a comunidade.'),
 dict(id='ufac-05-2026',inst='UFAC · Campus Rio Branco',uf='AC',numero='Edital 05/2026',titulo='Monitoria acadêmica',area='Ensino',tipo='Monitoria',publico='Graduação',inicio='2026-10-12',fim='2026-10-28',valor=400,resumo='Monitoria em disciplinas do CCSD, com carga de 12 horas semanais.'),
 dict(id='ufac-czs-02-2026',inst='UFAC · Campus Floresta',uf='AC',numero='Edital 02/2026',titulo='Auxílio Alimentação',area='Assistência estudantil',tipo='Alimentação',publico='Graduação',inicio='2026-10-15',fim='2026-11-10',valor=300,resumo='Auxílio para alimentação de estudantes do Campus Floresta.'),
 dict(id='ifac-18-2026',inst='IFAC · Campus Rio Branco',uf='AC',numero='Edital 18/2026',titulo='Auxílio Inclusão Digital',area='Assistência estudantil',tipo='Inclusão digital',publico='Técnico e graduação',inicio='2026-10-06',fim='2026-10-31',valor=150,resumo='Auxílio para contratação de internet e acesso a equipamentos para estudo.'),
 dict(id='ufam-21-2026',inst='UFAM · Campus Manaus',uf='AM',numero='Edital 21/2026',titulo='Auxílio Acadêmico',area='Assistência estudantil',tipo='Permanência',publico='Graduação',inicio='2026-10-20',fim='2026-11-14',valor=400,resumo='Auxílio para permanência de estudantes em situação de vulnerabilidade socioeconômica.'),
 dict(id='ufam-09-2026',inst='UFAM · Campus Manaus',uf='AM',numero='Edital 09/2026',titulo='Programa de Apoio à Iniciação Científica',area='Pesquisa',tipo='Iniciação científica',publico='Graduação',inicio='2026-09-02',fim='2026-10-02',valor=700,resumo='Bolsas de iniciação científica com duração de 12 meses.'),
 dict(id='ufam-14-2026',inst='UFAM · Campus Manaus',uf='AM',numero='Edital 14/2026',titulo='Bolsas de inovação tecnológica',area='Inovação',tipo='Inovação',publico='Graduação e pós-graduação',inicio='2026-10-26',fim='2026-11-30',valor=800,resumo='Bolsas para projetos de desenvolvimento tecnológico com parceiros externos.'),
 dict(id='uea-33-2026',inst='UEA · Manaus',uf='AM',numero='Edital 33/2026',titulo='Auxílio Transporte',area='Assistência estudantil',tipo='Transporte',publico='Graduação',inicio='2026-10-05',fim='2026-10-25',valor=200,resumo='Apoio para deslocamento até a unidade acadêmica.'),
 dict(id='unir-06-2026',inst='UNIR · Porto Velho',uf='RO',numero='Edital 06/2026',titulo='Auxílio Emergencial',area='Assistência estudantil',tipo='Auxílio emergencial',publico='Graduação',inicio='2026-10-13',fim='2026-11-13',valor=400,resumo='Auxílio pontual para estudantes afetados por situações imprevistas.'),
 dict(id='unir-11-2026',inst='UNIR · Porto Velho',uf='RO',numero='Edital 11/2026',titulo='Monitoria — Núcleo de Saúde',area='Ensino',tipo='Monitoria',publico='Graduação',inicio='2026-10-01',fim='2026-10-20',valor=400,resumo='Monitoria em disciplinas básicas dos cursos de saúde.'),
 dict(id='ufrr-04-2026',inst='UFRR · Campus Paricarana',uf='RR',numero='Edital 04/2026',titulo='Bolsa Esporte Universitário',area='Esporte e cultura',tipo='Esporte',publico='Graduação',inicio='2026-10-19',fim='2026-11-09',valor=350,resumo='Bolsas para estudantes-atletas que representam a universidade em competições.'),
 dict(id='ufpa-27-2026',inst='UFPA · Campus Belém',uf='PA',numero='Edital 27/2026',titulo='PIBIC Ações Afirmativas',area='Pesquisa',tipo='Iniciação científica',publico='Graduação',inicio='2026-11-02',fim='2026-12-01',valor=700,resumo='Iniciação científica com vagas para estudantes ingressantes por ações afirmativas.'),
 dict(id='ufpa-15-2026',inst='UFPA · Campus Belém',uf='PA',numero='Edital 15/2026',titulo='Auxílio Moradia',area='Assistência estudantil',tipo='Moradia',publico='Graduação',inicio='2026-10-09',fim='2026-11-03',valor=530,resumo='Auxílio mensal para estudantes que não residem com a família em Belém.'),
 dict(id='unifap-08-2026',inst='UNIFAP · Campus Marco Zero',uf='AP',numero='Edital 08/2026',titulo='Bolsas de extensão em cultura',area='Esporte e cultura',tipo='Extensão',publico='Graduação',inicio='2026-10-14',fim='2026-11-05',valor=700,resumo='Bolsas para projetos culturais desenvolvidos com comunidades do Amapá.'),
 dict(id='uft-19-2026',inst='UFT · Campus Palmas',uf='TO',numero='Edital 19/2026',titulo='Bolsas de mestrado',area='Pesquisa',tipo='Pós-graduação',publico='Pós-graduação',inicio='2026-10-05',fim='2026-11-20',valor=2100,resumo='Bolsas para estudantes regularmente matriculados em programas de mestrado.'),
]

HOJE = date(2026, 10, 24)  # data de cenário fixa do protótipo React

def pagina_catalogo() -> None:
    st.subheader('Encontre editais de bolsas e auxílios')
    st.caption('Catálogo de demonstração atualizado a partir do PonteFront. Somente o edital UFAC 01/2026 está associado a fontes oficiais e possui orientação guiada; os demais registros são fictícios.')
    busca = st.text_input('Buscar por nome, número, área, tipo ou instituição', key='catalogo_busca').casefold().strip()
    c1,c2,c3=st.columns(3)
    with c1: uf=st.selectbox('Estado', ['Todos']+sorted({x['uf'] for x in EDITAIS}), key='catalogo_uf')
    with c2: area=st.selectbox('Área', ['Todas']+sorted({x['area'] for x in EDITAIS}), key='catalogo_area')
    with c3: situacao=st.selectbox('Inscrições', ['Todas','Abertas','Em breve','Encerradas'], key='catalogo_situacao')
    so_guiado=st.checkbox('Somente editais com orientação guiada', key='catalogo_guiado')
    resultado=[]
    for e in EDITAIS:
        texto=' '.join(str(e.get(k,'')) for k in ('numero','titulo','area','tipo','publico','resumo','inst')).casefold()
        status='Em breve' if HOJE < date.fromisoformat(e['inicio']) else ('Encerradas' if HOJE > date.fromisoformat(e['fim']) else 'Abertas')
        if busca and busca not in texto: continue
        if uf!='Todos' and e['uf']!=uf: continue
        if area!='Todas' and e['area']!=area: continue
        if situacao!='Todas' and status!=situacao: continue
        if so_guiado and not e.get('real'): continue
        resultado.append((e,status))
    st.caption(f'{len(resultado)} edital(is) · situação calculada na data de cenário {HOJE:%d/%m/%Y}')
    for e,status in resultado:
        with st.container(border=True):
            st.markdown(f"**{e['numero']} · {e['titulo']}** — {e['inst']} · {e['uf']}")
            st.caption(f"{e['area']} · {e['tipo']} · {status} · inscrições: {e['inicio'][8:10]}/{e['inicio'][5:7]} a {e['fim'][8:10]}/{e['fim'][5:7]}/{e['fim'][:4]}")
            st.write(e['resumo'])
            if e.get('real'):
                st.success('Edital com fonte oficial vinculada e fluxo guiado disponível.')
                st.link_button('Abrir página oficial do edital',e['url'])
                if st.button('Preparar para este edital',key='preparar_'+e['id'],type='primary'):
                    st.session_state.visao='Preparar edital UFAC 01/2026'; st.session_state.etapa=0; st.rerun()
            else:
                st.warning('Exemplo fictício do protótipo. Não use as informações como edital vigente ou orientação de inscrição.')
    st.info('Preparação geral por perguntas para outros editais ainda não foi portada nesta versão Streamlit; não apresentamos seus itens como recomendações confirmadas.')
