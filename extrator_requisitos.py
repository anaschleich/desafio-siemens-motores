"""
Extrator de Requisitos de Motores Elétricos - Desafio Siemens Energy
Extrai especificações técnicas de documentos PDF usando LLM
"""

from groq import Groq
import PyPDF2
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()


class ExtratorRequisitos:
    """
    Extrai requisitos técnicos de documentos PDF de especificação de motores
    Usa Groq LLM para análise inteligente de texto
    """
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = "llama-3.3-70b-versatile"
    
    def extrair_texto_pdf(self, caminho_pdf):
        """Extrai texto completo do PDF"""
        try:
            with open(caminho_pdf, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                texto_completo = ""
                
                for pagina in pdf_reader.pages:
                    texto_completo += pagina.extract_text() + "\n"
                
                return texto_completo
        except Exception as e:
            print(f"❌ Erro ao ler PDF {caminho_pdf}: {e}")
            return None
    
    def extrair_requisitos(self, caminho_pdf):
        """
        Extrai requisitos técnicos do PDF usando LLM
        """
        print(f"\n{'='*80}")
        print(f"📄 Processando: {Path(caminho_pdf).name}")
        print(f"{'='*80}\n")
        
        # Extrai texto do PDF
        print("🔍 Extraindo texto do PDF...")
        texto_pdf = self.extrair_texto_pdf(caminho_pdf)
        
        if not texto_pdf:
            return None
        
        print(f"✅ Texto extraído ({len(texto_pdf)} caracteres)")
        
        # Analisa com LLM
        print("🤖 Analisando com LLM (Groq - Llama 3.3)...")
        
        prompt = self._criar_prompt_extracao(texto_pdf, Path(caminho_pdf).name)
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.1,  # Baixa para maior precisão
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            
            resposta_texto = response.choices[0].message.content.strip()
            
            # Limpa markdown se houver
            if '```json' in resposta_texto:
                resposta_texto = resposta_texto.split('```json')[1].split('```')[0]
            elif '```' in resposta_texto:
                resposta_texto = resposta_texto.split('```')[1].split('```')[0]
            
            requisitos = json.loads(resposta_texto.strip())
            
            print("✅ Requisitos extraídos com sucesso!")
            
            return requisitos
            
        except Exception as e:
            print(f"❌ Erro ao processar com LLM: {e}")
            return None
    
    def _get_system_prompt(self):
        """Define a persona do LLM"""
        return """Você é um Engenheiro Especialista em especificação de motores elétricos industriais com vasta experiência em análise de documentação técnica.

Sua tarefa é extrair requisitos técnicos de documentos de especificação de motores com máxima precisão e completude.

Você deve:
- Identificar e extrair TODOS os dados técnicos presentes
- Converter unidades quando necessário (HP→kW: 1 HP = 0.746 kW)
- Normalizar nomenclaturas (ex: "trifásico" → 3 fases)
- Inferir informações implícitas quando óbvias (ex: bomba centrífuga → fluido provavelmente água)
- Marcar campos como null apenas quando genuinamente ausentes
- Estimar confiança da extração de cada seção (0.0 a 1.0)
- Listar informações faltantes de forma clara

SEMPRE retorne JSON válido, estruturado e completo."""
    
    def _criar_prompt_extracao(self, texto_pdf, nome_arquivo):
        """Cria o prompt detalhado para extração"""
        
        return f"""
DOCUMENTO TÉCNICO A ANALISAR:

Nome do arquivo: {nome_arquivo}
Data de processamento: {datetime.now().isoformat()}

═══════════════════════════════════════════════════════════════════════════
CONTEÚDO DO DOCUMENTO
═══════════════════════════════════════════════════════════════════════════

{texto_pdf}

═══════════════════════════════════════════════════════════════════════════
TAREFA: EXTRAÇÃO DE REQUISITOS
═══════════════════════════════════════════════════════════════════════════

Extraia TODAS as informações técnicas presentes no documento e estruture no formato JSON abaixo.

ATENÇÃO:
- Use null para campos NÃO encontrados (não invente dados)
- Converta unidades quando necessário
- Seja preciso nos valores numéricos
- Normalize nomenclaturas técnicas
- Identifique todas as normas mencionadas

═══════════════════════════════════════════════════════════════════════════
FORMATO DE SAÍDA (JSON)
═══════════════════════════════════════════════════════════════════════════

{{
  "documento_origem": "{nome_arquivo}",
  "data_extracao": "{datetime.now().isoformat()}",
  "requisitos": {{
    "eletricos": {{
      "potencia_kw": null,
      "potencia_cv": null,
      "potencia_hp": null,
      "tensao_v": null,
      "tensao_tolerancia": null,
      "corrente_nominal_a": null,
      "frequencia_hz": null,
      "numero_fases": null,
      "fator_potencia": null,
      "fator_potencia_desejado": null,
      "classe_isolamento": null,
      "elevacao_temperatura_classe": null,
      "eficiencia_minima": null,
      "eficiencia_desejada": null,
      "categoria_partida": null,
      "tipo_partida": null,
      "preparado_inversor": null,
      "resistencia_isolamento_min_mohm": null
    }},
    "mecanicos": {{
      "rotacao_rpm": null,
      "rotacao_tolerancia_rpm": null,
      "rotacao_tolerancia_percentual": null,
      "numero_polos": null,
      "torque_nominal_nm": null,
      "torque_partida_percentual": null,
      "torque_maximo_percentual": null,
      "tipo_montagem": null,
      "forma_construtiva_iec": null,
      "tipo_acoplamento": null,
      "sentido_rotacao": null,
      "altura_eixo_mm": null,
      "carcaca_iec": null,
      "tipo_eixo": null,
      "tipo_rolamento": null,
      "peso_kg": null,
      "dimensoes_mm": null
    }},
    "operacionais": {{
      "grau_protecao": null,
      "eficiencia": null,
      "regime_trabalho": null,
      "temp_ambiente_min_c": null,
      "temp_ambiente_max_c": null,
      "temp_ambiente_nominal_c": null,
      "umidade_relativa_max_percent": null,
      "umidade_condensante": null,
      "altitude_max_m": null,
      "tipo_refrigeracao": null,
      "classe_vibracao": null,
      "classe_vibracao_norma": null,
      "nivel_ruido_max_dba": null,
      "nivel_ruido_referencia": null
    }},
    "aplicacao": {{
      "tipo_bomba": null,
      "fabricante_bomba": null,
      "modelo_bomba": null,
      "fluido": null,
      "fluido_descricao": null,
      "vazao_m3h": null,
      "altura_manometrica_m": null,
      "pressao_recalque_bar": null,
      "temperatura_fluido_min_c": null,
      "temperatura_fluido_max_c": null,
      "regime_operacao": null,
      "ambiente": null,
      "ambiente_descricao": null,
      "condicoes_especiais": null,
      "normas": []
    }},
    "protecoes": {{
      "protecao_termica_tipo": null,
      "protecao_termica_quantidade": null,
      "protecao_termica_localizacao": null,
      "caixa_ligacao_posicionamento": null,
      "caixa_ligacao_grau_protecao": null,
      "terminal_aterramento": null
    }},
    "comercial": {{
      "garantia_minima_meses": null,
      "garantia_desejada_meses": null,
      "prazo_entrega_maximo_dias": null,
      "prazo_entrega_desejado_dias": null,
      "orcamento_disponivel_brl": null,
      "certificacao_inmetro": null
    }}
  }},
  "informacoes_faltantes": [],
  "confianca_extracao": {{
    "eletricos": 0.0,
    "mecanicos": 0.0,
    "operacionais": 0.0,
    "aplicacao": 0.0
  }},
  "observacoes": []
}}

═══════════════════════════════════════════════════════════════════════════
INSTRUÇÕES DETALHADAS
═══════════════════════════════════════════════════════════════════════════

1. CONVERSÕES DE UNIDADES:
   - HP → kW: multiplicar por 0.746
   - CV → kW: multiplicar por 0.735
   - kW → CV: dividir por 0.735

2. NORMALIZAÇÃO DE VALORES:
   - Potência: sempre fornecer em kW, CV e HP
   - Rotação: arredondar para número inteiro
   - Temperatura: sempre em Celsius
   - Pressão: sempre em bar (se houver em kgf/cm², converter 1:1 aproximadamente)

3. IDENTIFICAÇÃO DE NORMAS:
   - Procurar por: NBR, IEC, ISO, API, NEMA, ABNT
   - Incluir número completo (ex: "IEC 60034-1")

4. INFORMAÇÕES FALTANTES:
   - Liste APENAS campos importantes que não foram encontrados
   - Seja específico (ex: "certificacao_inmetro", "altitude_maxima_operacao")

5. CONFIANÇA DA EXTRAÇÃO:
   - 1.0 = Informação explícita e clara no documento
   - 0.8-0.9 = Informação presente mas requer interpretação
   - 0.6-0.7 = Informação inferida de contexto
   - 0.3-0.5 = Informação parcial ou ambígua
   - 0.0 = Nenhuma informação encontrada

6. OBSERVAÇÕES:
   - Adicione notas relevantes sobre peculiaridades do documento
   - Mencione se há informações contraditórias
   - Indique se há dados em formatos não padrão

═══════════════════════════════════════════════════════════════════════════

IMPORTANTE: Retorne APENAS o JSON, sem texto adicional antes ou depois.
"""
    
    def processar_pdfs(self, lista_pdfs):
        """Processa múltiplos PDFs e retorna lista de requisitos"""
        
        print(f"\n{'='*80}")
        print(f"🚀 EXTRATOR DE REQUISITOS DE MOTORES ELÉTRICOS")
        print(f"{'='*80}")
        print(f"\n📦 Total de documentos: {len(lista_pdfs)}")
        
        resultados = []
        
        for i, pdf_path in enumerate(lista_pdfs, 1):
            print(f"\n[{i}/{len(lista_pdfs)}] Processando: {pdf_path}")
            
            requisitos = self.extrair_requisitos(pdf_path)
            
            if requisitos:
                resultados.append(requisitos)
                
                # Salva individual
                nome_base = Path(pdf_path).stem
                output_path = f"outputs/{nome_base}_requisitos.json"
                
                Path("outputs").mkdir(exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(requisitos, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Salvo: {output_path}")
                
                # Mostra resumo
                self._mostrar_resumo(requisitos)
        
        return resultados
    
    def _mostrar_resumo(self, requisitos):
        """Mostra resumo dos requisitos extraídos"""
        print(f"\n📊 Resumo da Extração:")
        print(f"   Potência: {requisitos['requisitos']['eletricos'].get('potencia_kw', 'N/A')} kW")
        print(f"   Tensão: {requisitos['requisitos']['eletricos'].get('tensao_v', 'N/A')} V")
        print(f"   Rotação: {requisitos['requisitos']['mecanicos'].get('rotacao_rpm', 'N/A')} rpm")
        print(f"   Eficiência: {requisitos['requisitos']['operacionais'].get('eficiencia', 'N/A')}")
        print(f"   Grau Proteção: {requisitos['requisitos']['operacionais'].get('grau_protecao', 'N/A')}")
        
        # Informações faltantes
        if requisitos.get('informacoes_faltantes'):
            print(f"\n⚠️  Informações Faltantes: {len(requisitos['informacoes_faltantes'])}")
            for info in requisitos['informacoes_faltantes'][:5]:  # Mostra até 5
                print(f"      - {info}")
        
        # Confiança
        confianca_media = sum(requisitos['confianca_extracao'].values()) / len(requisitos['confianca_extracao'])
        print(f"\n✅ Confiança Média: {confianca_media:.1%}")
    
    def consolidar_requisitos(self, lista_requisitos):
        """
        Consolida múltiplos documentos em um único JSON de requisitos
        Mescla valores de todos os PDFs, priorizando informações mais completas
        """
        if not lista_requisitos:
            return None
        
        if len(lista_requisitos) == 1:
            return lista_requisitos[0]
        
        print(f"\n{'='*80}")
        print(f"🔄 Consolidando {len(lista_requisitos)} documentos...")
        print(f"{'='*80}\n")
        
        # Inicializa estrutura consolidada
        consolidado = {
            "documentos_origem": [r['documento_origem'] for r in lista_requisitos],
            "data_extracao": datetime.now().isoformat(),
            "requisitos": {
                "eletricos": {},
                "mecanicos": {},
                "operacionais": {},
                "aplicacao": {},
                "protecoes": {},
                "comercial": {}
            },
            "informacoes_faltantes": [],
            "confianca_extracao": {
                "eletricos": 0.0,
                "mecanicos": 0.0,
                "operacionais": 0.0,
                "aplicacao": 0.0
            },
            "observacoes": [f"Requisitos consolidados de {len(lista_requisitos)} documentos"]
        }
        
        # Consolida cada seção
        for secao in ['eletricos', 'mecanicos', 'operacionais', 'aplicacao', 'protecoes', 'comercial']:
            print(f"\n📋 Consolidando seção: {secao}")
            
            # Coleta todos os campos únicos de todos os documentos
            todos_campos = set()
            for req in lista_requisitos:
                if secao in req['requisitos']:
                    todos_campos.update(req['requisitos'][secao].keys())
            
            # Para cada campo, escolhe o melhor valor
            for campo in todos_campos:
                valores_encontrados = []
                
                # Coleta valores de todos os documentos
                for req in lista_requisitos:
                    if secao in req['requisitos']:
                        valor = req['requisitos'][secao].get(campo)
                        if valor is not None:
                            valores_encontrados.append({
                                'valor': valor,
                                'documento': req['documento_origem'],
                                'confianca': req['confianca_extracao'].get(secao, 0.0)
                            })
                
                # Escolhe o melhor valor
                if valores_encontrados:
                    # Prioriza valor do documento com maior confiança
                    melhor = max(valores_encontrados, key=lambda x: x['confianca'])
                    consolidado['requisitos'][secao][campo] = melhor['valor']
                    
                    # Se houver valores diferentes, registra
                    valores_unicos = set(str(v['valor']) for v in valores_encontrados)
                    if len(valores_unicos) > 1:
                        print(f"   ⚠️  {campo}: valores diferentes encontrados")
                        for v in valores_encontrados:
                            print(f"      • {v['valor']} ({v['documento']})")
                        print(f"      → Escolhido: {melhor['valor']} (maior confiança)")
                    else:
                        print(f"   ✓ {campo}: {melhor['valor']}")
                else:
                    # Nenhum documento tem esse campo
                    consolidado['requisitos'][secao][campo] = None
        
        # Calcula confiança média por seção
        for secao in ['eletricos', 'mecanicos', 'operacionais', 'aplicacao']:
            confiancias = [r['confianca_extracao'].get(secao, 0.0) for r in lista_requisitos]
            consolidado['confianca_extracao'][secao] = sum(confiancias) / len(confiancias) if confiancias else 0.0
        
        # Identifica informações faltantes (campos null em TODOS os documentos)
        for secao, campos in consolidado['requisitos'].items():
            for campo, valor in campos.items():
                if valor is None:
                    consolidado['informacoes_faltantes'].append(f"{secao}.{campo}")
        
        print(f"\n✅ Consolidação concluída!")
        print(f"   📊 {len(consolidado['informacoes_faltantes'])} informações faltantes")
        
        return consolidado
    
    def salvar_consolidado(self, requisitos_consolidados, caminho='outputs/requisitos_consolidados.json'):
        """Salva requisitos consolidados"""
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
        
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(requisitos_consolidados, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Requisitos consolidados salvos: {caminho}")


def main():
    """Função principal"""
    
    # Inicializa extrator
    extrator = ExtratorRequisitos()
    
    # Lista de PDFs para processar
    pdfs = [
        "pdfs/Memorial Descritivo - Motor Bomba Industrial.pdf",
        "pdfs/Datasheet - Motor Industrial.pdf",
        "pdfs/Especificação Técnica - Motor Bomba Centrífuga.pdf"
    ]
    
    # Verifica se PDFs existem
    pdfs_existentes = [p for p in pdfs if Path(p).exists()]
    
    if not pdfs_existentes:
        print("❌ Nenhum PDF encontrado na pasta pdfs/")
        print("   Certifique-se de que os PDFs estão em: pdfs/")
        return
    
    print(f"✅ {len(pdfs_existentes)} PDFs encontrados")
    
    # Processa PDFs
    requisitos_lista = extrator.processar_pdfs(pdfs_existentes)
    
    # Consolida
    if requisitos_lista:
        consolidado = extrator.consolidar_requisitos(requisitos_lista)
        extrator.salvar_consolidado(consolidado)
        
        print(f"\n{'='*80}")
        print(f"✅ EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"{'='*80}")
        print(f"\n📂 Arquivos gerados:")
        print(f"   - outputs/*_requisitos.json (individual por PDF)")
        print(f"   - outputs/requisitos_consolidados.json (consolidado)")
        print(f"\n💡 Próximo passo: python analisador_motores.py")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
