import streamlit as st
import json
import os
from pathlib import Path
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Analisador de Motores - Siemens",
    page_icon="⚡",
    layout="wide"
)

# Título
st.title("⚡ Analisador de Motores Elétricos")
st.markdown("### Sistema de Extração de Requisitos e Matching")
st.markdown("---")

# Sidebar
with st.sidebar:
    # Nota: Verifique se o caminho da imagem está correto no seu ambiente local
    st.image(r"C:\projeto-siemens\webpage\siemens-energy-logo.png", width=200)
    st.markdown("## Sobre")
    st.info("""
    **Desafio Técnico Siemens Energy**
    
    Sistema automatizado para:
    - Extração de requisitos de PDFs
    - Matching com catálogo de motores
    - Geração de recomendações
    """)
    
    st.markdown("## Tecnologias")
    st.markdown("""
    - Python 3.12
    - Groq API (Llama 3.3)
    - PyPDF2
    - Streamlit
    """)

# Tabs principais
tab1, tab2, tab3, tab4 = st.tabs(["📄 Requisitos Extraídos", "🔍 Análises de Matching", "📊 Dashboard", "ℹ️ Sobre o Projeto"])

# TAB 1: Requisitos Extraídos
with tab1:
    st.header("Requisitos Extraídos")
    
    # Define o caminho direto para o arquivo consolidado
    outputs_dir = Path("outputs")
    arquivo_requisitos = outputs_dir / "requisitos_consolidados.json"
    
    # Verifica se o arquivo específico existe
    if arquivo_requisitos.exists():
        # Carrega o JSON
        with open(arquivo_requisitos, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        st.success(f"✅ Arquivo carregado: {arquivo_requisitos.name}")
        
        # Exibição dos dados estruturados
        col1, col2 = st.columns([2, 1])
        
        with col1:
           
            st.subheader("📋 Consolidação de Documentos")
            if 'documentos_origem' in data:
                for doc in data['documentos_origem']:
                    st.caption(f"• {doc}")
            
            st.markdown(f"**Data de Extração:** {data.get('data_extracao', 'N/A')}")
            
            # Requisitos Elétricos
            with st.expander("⚡ Requisitos Elétricos", expanded=True):
                if 'eletricos' in data['requisitos']:
                    df_eletricos = pd.DataFrame([data['requisitos']['eletricos']]).T
                    df_eletricos.columns = ['Valor']
                    st.dataframe(df_eletricos, use_container_width=True)
            
            # Requisitos Mecânicos
            with st.expander("⚙️ Requisitos Mecânicos"):
                if 'mecanicos' in data['requisitos']:
                    df_mecanicos = pd.DataFrame([data['requisitos']['mecanicos']]).T
                    df_mecanicos.columns = ['Valor']
                    st.dataframe(df_mecanicos, use_container_width=True)
            
            # Requisitos Operacionais
            with st.expander("🔧 Requisitos Operacionais"):
                if 'operacionais' in data['requisitos']:
                    df_operacionais = pd.DataFrame([data['requisitos']['operacionais']]).T
                    df_operacionais.columns = ['Valor']
                    st.dataframe(df_operacionais, use_container_width=True)
        
        with col2:
            st.subheader("📊 Métricas de Confiança")
            confianca = data.get('confianca_extracao', {})
            
            for categoria, valor in confianca.items():
                porcentagem = valor * 100
                st.metric(
                    label=categoria.replace('_', ' ').title(),
                    value=f"{porcentagem:.0f}%"
                )
            
            if data.get('informacoes_faltantes'):
                st.warning("⚠️ Informações Faltantes")
                for info in data['informacoes_faltantes']:
                    st.text(f"• {info}")
        
        # Adição da visualização do JSON bruto
        st.markdown("---")
        with st.expander("📝 Visualizar JSON Completo"):
            st.json(data)
    
    else:
        st.warning(f"⚠️ Arquivo '{arquivo_requisitos.name}' não encontrado na pasta 'outputs/'")
        st.info("Certifique-se de que o processo de extração foi concluído com sucesso.")

# TAB 2: Análises de Matching
with tab2:
    st.header("🔍 Análises de Matching")
    
    outputs_dir = Path("outputs")
    arquivo_matching = outputs_dir / "analise_matching.json"
    
    if arquivo_matching.exists():
        with open(arquivo_matching, 'r', encoding='utf-8') as f:
            matching_data = json.load(f)
        
        st.success(f"✅ Análise carregada: {arquivo_matching.name}")

        # --- SEÇÃO: RESUMO EXECUTIVO ---
        resumo = matching_data.get('resumo_executivo', {})
        st.subheader("🏆 Recomendação Principal")
        
        col_rec1, col_rec2 = st.columns(2)
        with col_rec1:
            st.info(f"**Motor Sugerido:** {resumo.get('recomendacao_principal')}")
        with col_rec2:
           
            score_rec = resumo.get('score_recomendacao', 0)
            st.metric("Score de Adequação", f"{score_rec}%")

        # --- SEÇÃO: RANKING ---
        st.markdown("---")
        st.subheader("🥇 Ranking Geral")
        ranking = matching_data.get('ranking', [])
        if ranking:
            df_ranking = pd.DataFrame(ranking)
            colunas_rank = ['posicao', 'fabricante', 'score', 'classificacao', 'preco_brl', 'prazo_dias']
            df_display = df_ranking[colunas_rank].copy()
            df_display.columns = ['Posição', 'Fabricante', 'Score (%)', 'Status', 'Preço (BRL)', 'Prazo (Dias)']
            st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # --- SEÇÃO: ANÁLISES DETALHADAS ---
        st.subheader("📋 Detalhamento Técnico e Comercial")
        
        # Mapeamento: "analises_detalhadas"
        motores_detalhados = matching_data.get('analises_detalhadas', [])
        
        if motores_detalhados:
            for motor in motores_detalhados:
                # CORREÇÃO: Chaves exatas do seu JSON
                id_motor = motor.get('codigo_produto', 'Motor Desconhecido')
                score_motor = motor.get('score_adequacao')
                justificativa = motor.get('justificativa_recomendacao')
                
                # Definir cor baseada no score
                cor_texto = "green" if score_motor >= 80 else "orange" if score_motor >= 50 else "red"
                
                with st.expander(f"📌 {id_motor} - Adequação: {score_motor}%"):
                    # Exibição da Justificativa Técnica corrigida
                    st.markdown(f"**Justificativa Técnica:** {justificativa}")
                    
                    # Colunas de Vantagens, Desvantagens e Riscos
                    col_v, col_d, col_r = st.columns(3)
                    
                    with col_v:
                        st.markdown("### 🌟 Vantagens")
                        for v in motor.get('vantagens', []):
                            st.markdown(f"✅ {v}")
                            
                    with col_d:
                        st.markdown("### ⚠️ Desvantagens")
                        for d in motor.get('desvantagens', []):
                            st.markdown(f"❌ {d}")
                            
                    with col_r:
                        st.markdown("### 🚩 Riscos Técnicos")
                        for r in motor.get('riscos_tecnicos', []):
                            st.markdown(f"🚩 {r}")
                    
                    st.markdown("---")
                    
                    # Dados Comerciais e Eficiência
                    c1, c2, c3 = st.columns(3)
                    comercial = motor.get('dados_comerciais', {})
                    eficiencia = motor.get('analise_eficiencia', {})
                    
                    with c1:
                        st.write("**💰 Comercial**")
                        st.write(f"Preço: R$ {comercial.get('preco_base_brl', 0):,.2f}")
                        st.write(f"Prazo: {comercial.get('prazo_entrega_dias')} dias")
                    with c2:
                        st.write("**⚙️ Técnico**")
                        st.write(f"Origem: {comercial.get('origem')}")
                        st.write(f"Garantia: {comercial.get('garantia_meses')} meses")
                    with c3:
                        st.write("**🌱 Eficiência**")
                        st.write(f"ROI: {eficiencia.get('roi_anos')} anos")
                        st.write(f"TCO (5 anos): R$ {eficiencia.get('tco_5anos_brl', 0):,.2f}")
                    
                    st.progress(int(score_motor) / 100)

            # JSON bruto no final para conferência
            st.markdown("---")
            with st.expander("📝 Visualizar JSON de Matching Completo"):
                st.json(matching_data)
        else:
            st.warning("⚠️ Nenhuma análise encontrada em 'analises_detalhadas'.")
            
    else:
        st.error(f"❌ Arquivo '{arquivo_matching.name}' não encontrado.")


# TAB 3: Dashboard
with tab3:
    st.header("📊 Comparativo: Requisitos vs. Catálogo")
    
    outputs_dir = Path("outputs")
    file_req = outputs_dir / "requisitos_consolidados.json"
    file_match = outputs_dir / "analise_matching.json"
    
    if file_req.exists() and file_match.exists():
        with open(file_req, 'r', encoding='utf-8') as f:
            req_data = json.load(f)
        with open(file_match, 'r', encoding='utf-8') as f:
            match_data = json.load(f)

    # 1. Requisitos 
        reqs = req_data.get('requisitos', {})
        req_eletricos = reqs.get('eletricos', {})
        req_mecanicos = reqs.get('mecanicos', {})

    # 2. Configuração da Matriz
        # Mapeamento: (Nome na Tabela, Chave no arquivo Requisitos, Chave no arquivo Matching)
        campos = [
            ("Potência (kW)", "potencia_kw", "potencia"),
            ("Rotação (RPM)", "rotacao_rpm", "rotacao"),
            ("Tensão (V)", "tensao_v", "tensao"),
            ("Eficiência", "eficiencia_desejada", "eficiencia")
        ]

        matriz_dados = []
        motores = match_data.get('analises_detalhadas', [])

        for label, chave_req, chave_match in campos:
            # 1. Pega o Valor Alvo do arquivo de Requisitos
            valor_alvo = req_eletricos.get(chave_req) or req_mecanicos.get(chave_req) or "N/A"
            
            linha = {"Especificação": label, "REQUISITO ALVO": str(valor_alvo)}
            
            # 2. Busca o valor_motor em cada fabricante dentro do arquivo de Matching
            for m in motores:
                fabricante = m.get('fabricante', 'Motor')
                analise_tec = m.get('analise_tecnica', {})
                
                # Acessa o objeto da característica (ex: analise_tec['rotacao'])
                caracteristica = analise_tec.get(chave_match, {})
                
                # Extrai especificamente o valor_motor conforme solicitado
                if isinstance(caracteristica, dict):
                    valor_final = caracteristica.get('valor_motor') or caracteristica.get('valor_especificado') or "N/A"
                else:
                    valor_final = "N/A"
                    
                linha[fabricante] = str(valor_final)
            
            matriz_dados.append(linha)

    # 3. Linha de Score (score_adequacao)
        linha_score = {"Especificação": "⭐ SCORE DE ADEQUAÇÃO", "REQUISITO ALVO": "100%"}
        for m in motores:
            fabricante = m.get('fabricante', 'Motor')
            # No seu JSON, o score está na raiz de cada motor em analises_detalhadas
            linha_score[fabricante] = f"{m.get('score', 0)}%"

        matriz_dados.append(linha_score)

    # 4. Exibição da Tabela
        st.subheader("📋 Matriz de Conformidade Técnica (Datasheet Comparativo)")
        df_matriz = pd.DataFrame(matriz_dados)
        st.dataframe(df_matriz, use_container_width=True, hide_index=True)

        

    # 5. Cards de Resumo
        st.markdown("---")
        st.subheader("🥇 Classificação Final")
        cols = st.columns(len(motores))
        for idx, m in enumerate(motores):
            with cols[idx]:
                st.metric(
                    label=m.get('fabricante'), 
                    value=f"{m.get('score')}%", 
                    delta=m.get('classificacao')
                )
    else:
        st.error("Arquivos de dados não encontrados em /outputs.")

