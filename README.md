# Ponte — versão Streamlit

Esta pasta contém uma adaptação Streamlit do fluxo guiado da Ponte para o Edital Proaes nº 01/2026 da UFAC. Ela reaproveita os módulos Python de fatos, regras, fontes, extração Gemma e resumo do repositório original.

## O que foi convertido

- Fluxo em quatro etapas: contexto do edital, entrada de situação, conferência e próximos passos.
- Entrada por relato com chamada real ao Gemma 4 pela Gemini API.
- Alternativa por perguntas diretas quando não houver chave ou quando a API falhar.
- Sugestões com trechos de origem, confirmação e edição de fatos.
- Recalculo das orientações após alterações e resumo copiável/baixável.
- Trechos e links das fontes oficiais do edital.

Esta versão mantém o escopo do MVP revisado. Não inclui o catálogo de exemplos fictícios nem as perguntas genéricas simuladas do protótipo React, porque elas não são regras revisadas de editais reais. Não inclui SQLite, login, upload de documentos, OCR ou histórico.

## Executar localmente

Requer Python 3.11 ou superior.

    cd Ponte-Streamlit
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    $env:GEMINI_API_KEY="sua-chave"
    streamlit run streamlit_app.py

A chave é opcional para a entrada manual. Não a coloque no código nem no Git. Para Streamlit Community Cloud, configure GEMINI_API_KEY em App settings → Secrets. O modelo padrão é models/gemma-4-26b-a4b-it; se necessário, defina GEMMA_MODEL como secret ou variável de ambiente.

## Dados e privacidade

A aplicação não tem banco de casos, cadastro ou upload. As respostas e o relato permanecem no estado da sessão processado pelo servidor Streamlit enquanto o fluxo está aberto; a sessão pode ser perdida ao atualizar ou reconectar. O botão Apagar sessão limpa o estado da aplicação.

Quando a pessoa escolhe Analisar relato com Gemma, o texto é enviado à Gemini API. A cota gratuita da API tem termos que permitem uso do conteúdo para melhoria dos serviços e revisão humana. Por isso, esta versão orienta usar somente dados fictícios na demonstração e não afirma que nenhum dado é processado ou recebido por fornecedores. A chave não é enviada ao navegador pelo código da aplicação.

A aplicação não salva relatos em arquivos, SQLite ou logs próprios. Isso não constitui uma auditoria dos logs ou políticas do provedor de hospedagem e da Gemini API.

## Limites do produto

A Ponte relaciona fatos informados pela pessoa a um recorte revisado do edital. Ela não confirma acontecimentos, não verifica autenticidade documental, não decide elegibilidade e não determina que a documentação é suficiente para concluir a inscrição. A decisão cabe à Proaes. Confira sempre a página oficial e alterações do edital.

## Publicação

Para Streamlit Community Cloud, publique esta pasta em um repositório GitHub e selecione streamlit_app.py como arquivo principal. Configure GEMINI_API_KEY nos secrets do app. A pasta SQLite foi deixada de fora conforme o escopo atual; esta versão não persiste formulários gerados nem respostas.

Arquivos do edital incluídos em fontes/ufac-proaes-01-2026/ são cópias de documentos públicos citados pelo código-fonte original. A licença MIT da aplicação não altera os direitos ou termos dos documentos e do modelo.

