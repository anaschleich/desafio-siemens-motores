"""
Analisador de Motores Elétricos - Desafio Siemens Energy
Sistema de matching inteligente usando LLM para comparação de requisitos técnicos
"""

from groq import Groq
import json
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Carrega variáveis de ambiente
load_dotenv()

class AnalisadorMotores:
    """
    Classe para análise de adequação de motores elétricos usando LLM
    Perspectiva: Engenheiro Especialista em Especificação de Motores
    """
    
    def __init__(self):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = "llama-3.3-70b-versatile"
        
    def carregar_requisitos(self, caminho_arquivo):
        """Carrega requisitos do projeto (aceita formato individual ou consolidado)"""
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            requisitos = json.load(f)
        
        # Normaliza formato: converte documento_origem em lista se for string
        if 'documento_origem' in requisitos and isinstance(requisitos['documento_origem'], str):
            requisitos['documentos_origem'] = [requisitos['documento_origem']]
        
        # Se já tem documentos_origem como lista, mantém
        if 'documentos_origem' not in requisitos and 'documento_origem' in requisitos:
            requisitos['documentos_origem'] = [requisitos['documento_origem']]
        
        return requisitos
    
    def carregar_catalogo(self, caminho_arquivo):
        """Carrega catálogo de motores"""
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            catalogo = json.load(f)
        return catalogo['catalogo_motores']['produtos']
    
    def analisar_motor(self, requisitos, motor):
        """
        Analisa um motor específico usando LLM
        Retorna score de adequação e análise detalhada
        """
        
        prompt = self._criar_prompt_analise(requisitos, motor)
        
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
                temperature=0.2,  # Baixa para maior consistência
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            resposta_texto = response.choices[0].message.content.strip()
            
            # Limpa possível markdown
            if '```json' in resposta_texto:
                resposta_texto = resposta_texto.split('```json')[1].split('```')[0]
            elif '```' in resposta_texto:
                resposta_texto = resposta_texto.split('```')[1].split('```')[0]
            
            analise = json.loads(resposta_texto.strip())
            
            # Adiciona informações comerciais
            analise['dados_comerciais'] = {
                'preco_base_brl': motor['comercial']['preco_base_brl'],
                'preco_com_impostos_brl': motor['comercial']['preco_com_impostos_brl'],
                'prazo_entrega_dias': motor['comercial']['prazo_entrega_dias'],
                'disponibilidade': motor['comercial']['disponibilidade'],
                'garantia_meses': motor['comercial']['garantia_meses'],
                'origem': motor['comercial']['origem_produto']
            }
            
            return analise
            
        except Exception as e:
            print(f"   ❌ Erro ao analisar {motor['codigo_produto']}: {e}")
            return None
    
    def _get_system_prompt(self):
        """Retorna o system prompt com persona de engenheiro"""
        return """Você é um Engenheiro Mecânico Sênior especializado em especificação de motores elétricos industriais com 20 anos de experiência.

Sua expertise inclui:
- Análise de requisitos técnicos complexos
- Seleção de equipamentos para aplicações críticas
- Avaliação de trade-offs técnico-comerciais
- Conhecimento profundo de normas IEC, NBR, API, NEMA
- Experiência com bombas centrífugas, compressores, ventiladores

Suas análises são:
- Precisas tecnicamente
- Justificadas com base em normas e boa prática
- Focadas em confiabilidade e TCO (Total Cost of Ownership)
- Conscientes de riscos operacionais e de manutenção

Você sempre retorna JSON válido e estruturado."""
    
    def _criar_prompt_analise(self, requisitos, motor):
        """Cria o prompt de análise detalhado"""
        
        return f"""
TAREFA: Analisar adequação técnica do motor para a aplicação especificada.

═══════════════════════════════════════════════════════════════════════════
REQUISITOS DO PROJETO
═══════════════════════════════════════════════════════════════════════════

PROJETO: {requisitos.get('projeto_info', {}).get('nome', 'N/A')}
APLICAÇÃO: {requisitos['requisitos']['aplicacao'].get('modelo_bomba', 'N/A')}
- Bomba: {requisitos['requisitos']['aplicacao'].get('fabricante_bomba', 'N/A')} {requisitos['requisitos']['aplicacao'].get('modelo_bomba', 'N/A')}
- Vazão: {requisitos['requisitos']['aplicacao'].get('vazao_m3h', 'N/A')} m³/h
- AMT: {requisitos['requisitos']['aplicacao'].get('altura_manometrica_m', 'N/A')} m
- Regime: {requisitos['requisitos']['aplicacao'].get('regime_operacao', 'N/A')}

REQUISITOS CRÍTICOS (NÃO NEGOCIÁVEIS):
- Potência: {requisitos['requisitos']['eletricos'].get('potencia_kw', 'N/A')} kW (exata)
- Tensão: {requisitos['requisitos']['eletricos'].get('tensao_v', 'N/A')}V ±10%
- Grau Proteção: {requisitos['requisitos']['operacionais'].get('grau_protecao', 'N/A')} (mínimo)
- Eficiência: {requisitos['requisitos']['eletricos'].get('eficiencia_minima', 'N/A')} (mínimo), {requisitos['requisitos']['eletricos'].get('eficiencia_desejada', 'N/A')} (desejado)

REQUISITOS IMPORTANTES:
- Rotação: {requisitos['requisitos']['mecanicos'].get('rotacao_rpm', 'N/A')} rpm (±{requisitos['requisitos']['mecanicos'].get('rotacao_tolerancia_percentual', 2.0)}%)
- Corrente máxima: {requisitos['requisitos']['eletricos'].get('corrente_nominal_a', 'N/A')} A @ 380V
- Montagem: {requisitos['requisitos']['mecanicos'].get('tipo_montagem', 'N/A')}
- Altura eixo: {requisitos['requisitos']['mecanicos'].get('altura_eixo_mm', 'N/A')} mm
- Preparado inversor: {'Obrigatório' if requisitos['requisitos']['eletricos'].get('preparado_inversor', False) else 'Não necessário'}

REQUISITOS COMERCIAIS:
- Prazo máximo: {requisitos['requisitos']['comercial'].get('prazo_entrega_maximo_dias', 'N/A')} dias
- Garantia mínima: {requisitos['requisitos']['comercial'].get('garantia_minima_meses', 'N/A')} meses
- Orçamento: até R$ {requisitos['requisitos']['comercial'].get('orcamento_disponivel_brl', 'N/A')}

═══════════════════════════════════════════════════════════════════════════
MOTOR EM ANÁLISE
═══════════════════════════════════════════════════════════════════════════

{json.dumps(motor, indent=2, ensure_ascii=False)}

═══════════════════════════════════════════════════════════════════════════
SISTEMA DE PONTUAÇÃO
═══════════════════════════════════════════════════════════════════════════

TOTAL: 100 pontos

1. POTÊNCIA (20 pontos) - CRÍTICO
   - Exata (15.0 kW): +20 pontos
   - ±5% (14.25-15.75 kW): +15 pontos
   - ±10% (13.5-16.5 kW): +10 pontos
   - Fora: 0 pontos (ELIMINATÓRIO)

2. TENSÃO (15 pontos) - CRÍTICO
   - 380V disponível: +15 pontos
   - Apenas 440V: 0 pontos (ELIMINATÓRIO)

3. EFICIÊNCIA (15 pontos)
   - IE4: +15 pontos (EXCELENTE)
   - IE3: +15 pontos (ATENDE)
   - IE2: +10 pontos (ACEITÁVEL, perdas maiores)
   - IE1: +5 pontos (RUIM, custo operacional alto)

4. GRAU DE PROTEÇÃO (10 pontos)
   - IP55 ou superior: +10 pontos
   - IP54: +5 pontos (INADEQUADO - ambiente úmido)
   - Inferior: 0 pontos (ELIMINATÓRIO)

5. ROTAÇÃO (10 pontos)
   - 1750 rpm ±1% (1733-1767 rpm): +10 pontos
   - 1750 rpm ±2% (1715-1785 rpm): +8 pontos
   - 1750 rpm ±3% (1697-1803 rpm): +5 pontos
   - Fora ±3%: +2 pontos

6. PREPARADO INVERSOR (10 pontos)
   - Sim: +10 pontos
   - Não: +5 pontos (limitação futura)

7. PRAZO ENTREGA (10 pontos)
   - ≤15 dias: +10 pontos (EXCELENTE)
   - 16-30 dias: +8 pontos (ATENDE)
   - 31-45 dias: +5 pontos (ACEITÁVEL)
   - 46-60 dias: +3 pontos (CRÍTICO)
   - >60 dias: +1 ponto (INADEQUADO)

8. DISPONIBILIDADE (5 pontos)
   - Estoque: +5 pontos
   - Nacional (pronta entrega): +4 pontos
   - Importação: +2 pontos

9. GARANTIA (5 pontos)
   - ≥24 meses: +5 pontos
   - 18-23 meses: +4 pontos
   - 12-17 meses: +3 pontos
   - <12 meses: +1 ponto

═══════════════════════════════════════════════════════════════════════════
INSTRUÇÕES DE ANÁLISE
═══════════════════════════════════════════════════════════════════════════

1. CALCULE o score exato somando os pontos de cada critério
2. SEJA RIGOROSO com requisitos críticos (Potência, Tensão, Grau Proteção)
3. CONSIDERE trade-offs reais:
   - IE4 é melhor que IE3, mas pode ter prazo maior
   - Importação tem qualidade superior, mas prazo longo
   - Garantia maior reduz TCO
4. JUSTIFIQUE tecnicamente cada decisão
5. IDENTIFIQUE riscos operacionais
6. COMPARE com especificações da bomba KSB Megabloc

═══════════════════════════════════════════════════════════════════════════
FORMATO DE SAÍDA (JSON)
═══════════════════════════════════════════════════════════════════════════

{{
  "codigo_produto": "...",
  "fabricante": "...",
  "score_adequacao": 87.5,
  "classificacao": "RECOMENDADO",
  "parecer_tecnico": "Resumo executivo em 2-3 linhas",
  
  "analise_pontuacao": {{
    "potencia": {{
      "pontos_obtidos": 20,
      "pontos_maximos": 20,
      "valor_especificado": 15.0,
      "valor_motor": 15.0,
      "atende": true,
      "observacao": "Potência exata conforme especificação"
    }},
    "tensao": {{
      "pontos_obtidos": 15,
      "pontos_maximos": 15,
      "valor_especificado": 380,
      "valor_motor": [380, 440],
      "atende": true,
      "observacao": "Tensão 380V disponível em configuração delta"
    }},
    "eficiencia": {{
      "pontos_obtidos": 15,
      "pontos_maximos": 15,
      "valor_especificado": "IE3",
      "valor_motor": "IE3",
      "atende": true,
      "observacao": "Eficiência IE3 conforme desejado. Economia operacional significativa."
    }},
    "grau_protecao": {{
      "pontos_obtidos": 10,
      "pontos_maximos": 10,
      "valor_especificado": "IP55",
      "valor_motor": "IP55",
      "atende": true,
      "observacao": "IP55 adequado para ambiente úmido com respingos"
    }},
    "rotacao": {{
      "pontos_obtidos": 8,
      "pontos_maximos": 10,
      "valor_especificado": 1750,
      "valor_motor": 1780,
      "variacao_percentual": 1.7,
      "atende": true,
      "observacao": "1780 rpm representa variação de 1.7%, dentro da tolerância de ±2%"
    }},
    "preparado_inversor": {{
      "pontos_obtidos": 10,
      "pontos_maximos": 10,
      "valor_especificado": true,
      "valor_motor": true,
      "atende": true,
      "observacao": "Isolamento reforçado IEC 60034-17 para operação com VFD"
    }},
    "prazo_entrega": {{
      "pontos_obtidos": 3,
      "pontos_maximos": 10,
      "valor_especificado": 30,
      "valor_motor": 60,
      "atende": false,
      "observacao": "Prazo de 60 dias excede o máximo de 30 dias. Requer importação."
    }},
    "disponibilidade": {{
      "pontos_obtidos": 2,
      "pontos_maximos": 5,
      "valor_especificado": "estoque",
      "valor_motor": "importacao",
      "atende": false,
      "observacao": "Produto importado, sem estoque local"
    }},
    "garantia": {{
      "pontos_obtidos": 5,
      "pontos_maximos": 5,
      "valor_especificado": 18,
      "valor_motor": 24,
      "atende": true,
      "observacao": "24 meses de garantia supera o mínimo de 18 meses"
    }}
  }},
  
  "vantagens": [
    "Eficiência IE3 proporciona economia de energia",
    "Garantia estendida de 24 meses",
    "Preparado para operação com inversor de frequência"
  ],
  
  "desvantagens": [
    "Prazo de entrega de 60 dias excede especificação (30 dias)",
    "Produto importado, sem estoque local",
    "Preço acima do orçamento disponível"
  ],
  
  "riscos_tecnicos": [
    "Prazo longo pode impactar cronograma do projeto",
    "Dependência de importação para peças de reposição"
  ],
  
  "recomendacao_engenharia": "ALTERNATIVA | RECOMENDADO | CONDICIONAL | NÃO RECOMENDADO",
  "justificativa_recomendacao": "Explicação técnica da recomendação",
  
  "adequacao_aplicacao": {{
    "bomba_centrifuga": "alta | média | baixa",
    "regime_continuo": "alta | média | baixa",
    "ambiente_umido": "alta | média | baixa"
  }},
  
  "analise_custo_beneficio": {{
    "custo_aquisicao_brl": 10500.00,
    "custo_energia_anual_estimado_brl": 8500.00,
    "economia_vs_ie1_anual_brl": 2400.00,
    "payback_vs_ie2_anos": 1.2,
    "tco_5anos_brl": 53000.00
  }}
}}

═══════════════════════════════════════════════════════════════════════════
CLASSIFICAÇÃO FINAL
═══════════════════════════════════════════════════════════════════════════

- 90-100 pontos: RECOMENDADO (Atende plenamente)
- 75-89 pontos: ALTERNATIVA (Atende com ressalvas)
- 60-74 pontos: CONDICIONAL (Requer aprovação de desvios)
- <60 pontos: NÃO RECOMENDADO (Inadequado)

IMPORTANTE: Seja objetivo, técnico e baseado em fatos. Evite subjetividade.
"""
    
    def processar_catalogo(self, requisitos, catalogo):
        """Processa todo o catálogo e gera ranking"""
        
        print(f"\n{'='*80}")
        print(f"🔧 ANÁLISE DE ADEQUAÇÃO DE MOTORES ELÉTRICOS")
        print(f"{'='*80}")
        
        # Mostra documentos origem
        docs_origem = requisitos.get('documentos_origem', requisitos.get('documento_origem', ['N/A']))
        if isinstance(docs_origem, str):
            docs_origem = [docs_origem]
        
        print(f"\n📋 Documentos Fonte: {len(docs_origem)}")
        for doc in docs_origem:
            print(f"   • {doc}")
        
        print(f"\n🏭 Cliente: {requisitos.get('projeto_info', {}).get('cliente', 'N/A')}")
        print(f"📅 Data Extração: {requisitos.get('data_extracao', 'N/A')[:10]}")
        print(f"\n💡 Aplicação: {requisitos['requisitos']['aplicacao'].get('modelo_bomba', 'N/A')}")
        print(f"   Bomba: {requisitos['requisitos']['aplicacao'].get('fabricante_bomba', 'N/A')} {requisitos['requisitos']['aplicacao'].get('modelo_bomba', 'N/A')}")
        print(f"   Vazão: {requisitos['requisitos']['aplicacao'].get('vazao_m3h', 'N/A')} m³/h")
        print(f"   AMT: {requisitos['requisitos']['aplicacao'].get('altura_manometrica_m', 'N/A')} m")
        
        print(f"\n{'='*80}")
        print(f"📦 Catálogo: {len(catalogo)} motores disponíveis para análise")
        print(f"{'='*80}\n")
        
        resultados = []
        
        for i, motor in enumerate(catalogo, 1):
            codigo = motor['codigo_produto']
            fabricante = motor['fabricante']
            
            print(f"[{i}/{len(catalogo)}] Analisando: {codigo} ({fabricante})... ", end='', flush=True)
            
            analise = self.analisar_motor(requisitos, motor)
            
            if analise:
                resultados.append(analise)
                score = analise['score_adequacao']
                classificacao = analise['classificacao']
                print(f"✅ Score: {score:.1f}% ({classificacao})")
            else:
                print(f"❌ Falha")
        
        # Ordena por score
        resultados.sort(key=lambda x: x['score_adequacao'], reverse=True)
        
        return resultados
    
    def gerar_relatorio(self, requisitos, resultados):
        """Gera relatório final consolidado"""
        
        # Normaliza documentos origem
        docs_origem = requisitos.get('documentos_origem', requisitos.get('documento_origem', ['N/A']))
        if isinstance(docs_origem, str):
            docs_origem = [docs_origem]
        
        relatorio = {
            "metadata": {
                "projeto": requisitos.get('projeto_info', {}).get('nome', 'N/A'),
                "cliente": requisitos.get('projeto_info', {}).get('cliente', 'N/A'),
                "referencia": requisitos.get('projeto_info', {}).get('referencia', 'N/A'),
                "documentos_origem": docs_origem,
                "total_documentos_analisados": len(docs_origem),
                "data_analise": datetime.now().isoformat(),
                "total_motores_analisados": len(resultados),
                "ferramenta": "Analisador Motores Elétricos v1.0",
                "llm_modelo": self.model
            },
            "resumo_executivo": {
                "recomendacao_principal": resultados[0]['codigo_produto'] if resultados else None,
                "score_recomendacao": resultados[0]['score_adequacao'] if resultados else 0,
                "alternativas_viaveis": [
                    r['codigo_produto'] for r in resultados[1:4] if r['score_adequacao'] >= 75
                ],
                "motores_inadequados": len([r for r in resultados if r['score_adequacao'] < 60])
            },
            "requisitos_projeto": requisitos,
            "analises_detalhadas": resultados,
            "ranking": [
                {
                    "posicao": i+1,
                    "codigo_produto": r['codigo_produto'],
                    "fabricante": r['fabricante'],
                    "score": r['score_adequacao'],
                    "classificacao": r['classificacao'],
                    "preco_brl": r['dados_comerciais']['preco_base_brl'],
                    "prazo_dias": r['dados_comerciais']['prazo_entrega_dias']
                }
                for i, r in enumerate(resultados)
            ]
        }
        
        return relatorio
    
    def salvar_relatorio(self, relatorio, caminho_saida):
        """Salva relatório em JSON"""
        
        Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
        
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Relatório salvo: {caminho_saida}")
    
    def imprimir_resumo(self, relatorio):
        """Imprime resumo no console"""
        
        print(f"\n{'='*80}")
        print(f"📊 RESUMO DA ANÁLISE")
        print(f"{'='*80}\n")
        
        print(f"🏆 MOTOR RECOMENDADO:")
        if relatorio['resumo_executivo']['recomendacao_principal']:
            top = relatorio['analises_detalhadas'][0]
            print(f"   {top['codigo_produto']} - {top['fabricante']}")
            print(f"   Score: {top['score_adequacao']:.1f}%")
            print(f"   Classificação: {top['classificacao']}")
            print(f"   Preço: R$ {top['dados_comerciais']['preco_base_brl']:,.2f}")
            print(f"   Prazo: {top['dados_comerciais']['prazo_entrega_dias']} dias")
            print(f"\n   📝 Parecer: {top['parecer_tecnico']}")
        
        print(f"\n{'='*80}")
        print(f"📋 RANKING COMPLETO:")
        print(f"{'='*80}\n")
        
        for item in relatorio['ranking'][:5]:  # Top 5
            print(f"{item['posicao']}. {item['codigo_produto']} ({item['fabricante']})")
            print(f"   Score: {item['score']:.1f}% | {item['classificacao']}")
            print(f"   R$ {item['preco_brl']:,.2f} | {item['prazo_dias']} dias\n")


def main():
    """Função principal"""
    
    print("\n" + "="*80)
    print("🔌 ANALISADOR DE MOTORES ELÉTRICOS - DESAFIO SIEMENS ENERGY")
    print("="*80 + "\n")
    
    # Inicializa analisador
    analisador = AnalisadorMotores()
    
    # Carrega dados
    print("📂 Carregando arquivos...")
    
    # Tenta carregar requisitos consolidados primeiro
    arquivo_requisitos = 'outputs/requisitos_consolidados.json'
    if not Path(arquivo_requisitos).exists():
        # Se não existir, tenta o antigo formato
        arquivo_requisitos = 'requisitos_extraidos.json'
        if not Path(arquivo_requisitos).exists():
            print(f"❌ Arquivo de requisitos não encontrado!")
            print(f"   Execute primeiro: python extrator_requisitos.py")
            return
    
    requisitos = analisador.carregar_requisitos(arquivo_requisitos)
    catalogo = analisador.carregar_catalogo('motor_catalog.json')
    
    print(f"✅ Requisitos carregados: {arquivo_requisitos}")
    print(f"✅ Catálogo carregado ({len(catalogo)} motores)")
    
    # Processa análise
    resultados = analisador.processar_catalogo(requisitos, catalogo)
    
    # Gera relatório
    relatorio = analisador.gerar_relatorio(requisitos, resultados)
    
    # Salva
    analisador.salvar_relatorio(relatorio, 'outputs/analise_matching.json')
    
    # Imprime resumo
    analisador.imprimir_resumo(relatorio)
    
    print(f"\n{'='*80}")
    print(f"✅ Análise concluída com sucesso!")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
