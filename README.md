# Analisador de Motores Elétricos - Desafio Siemens

> Sistema automatizado de extração de requisitos e matching de motores elétricos industriais utilizando LLM

## 📋 Sobre o Projeto

Este projeto foi desenvolvido como parte do processo seletivo para a posição de Bolsista Graduada IEL na Siemens Energy. O objetivo é demonstrar capacidade de:

- Extração automatizada de dados técnicos de documentos PDF
- Análise e comparação de especificações técnicas
- Tomada de decisão baseada em requisitos de engenharia
- Integração com APIs de LLM
- Desenvolvimento de soluções práticas para problemas de negócio

## 🎯 Funcionalidades

### Parte 1: Extração de Requisitos
- ✅ Processa documentos PDF com especificações de motores
- ✅ Extrai dados estruturados (elétricos, mecânicos, operacionais)
- ✅ Gera JSONs padronizados conforme schema fornecido
- ✅ Identifica informações faltantes
- ✅ Calcula score de confiança da extração

### Parte 2: Matching com Catálogo
- ✅ Compara requisitos extraídos com catálogo de motores
- ✅ Calcula score de adequação (0-100%)
- ✅ Classifica motores (RECOMENDADO, ALTERNATIVA, POSSÍVEL, NÃO RECOMENDADO)
- ✅ Identifica requisitos atendidos, parcialmente atendidos e não atendidos
- ✅ Destaca características superiores ao solicitado
- ✅ Gera relatórios detalhados em JSON

## 🏗️ Arquitetura da Solução

```
┌─────────────────┐
│  PDFs Técnicos  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  extrator_groq.py       │
│  • PyPDF2 (texto)       │
│  • Groq API (análise)   │
│  • JSON estruturado     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Requisitos Extraídos   │
│  (JSON por documento)   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  matching_groq.py       │
│  • Groq API (análise)   │
│  • Scoring ponderado    │
│  • Classificação        │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Análises Comparativas  │
│  (JSON com scores)      │
└─────────────────────────┘
```

## 🛠️ Tecnologias Utilizadas

- **Python 3.12** - Linguagem principal
- **Groq API** - LLM para análise de documentos (Llama 3.3 70B)
- **PyPDF2** - Extração de texto de PDFs
- **python-dotenv** - Gerenciamento de variáveis de ambiente

## 📁 Estrutura do Projeto

```
projeto-siemens/
├── README.md                      # Este arquivo
├── requirements.txt               # Dependências Python
├── .env.example                   # Exemplo de configuração
├── .gitignore                     # Arquivos ignorados pelo Git
│
├── extrator_requisitos.py         # Script de extração de requisitos
├── analisador_motores.py          # Script de matching com catálogo
│
├── pdfs/                          # PDFs de entrada (incluídos)
│   ├── Memorial Descritivo - Motor Bomba Industrial.pdf
│   ├── Datasheet - Motor Industrial.pdf
│   └── Especificação Técnica - Motor Bomba Centrífuga.pdf
│
├── outputs/                             # Resultados gerados
│   ├── *_requisitos.json                # Requisitos extraídos de cada arquivo
│   └── analise_matching.json            # Análises de matching
│   └── requisitos_consolidados.json     # Todos os requisitos consolidados em um json
│
└── motor_catalog.json                   # Catálogo de motores disponíveis
```

## 🚀 Como Executar

### Pré-requisitos

- Python 3.12+
- Conta Groq (gratuita) - https://console.groq.com

### Instalação

1. **Clone o repositório**
```bash
git clone <seu-repositorio>
cd projeto-siemens
```

2. **Crie e ative ambiente virtual**
```bash
python -m venv venv

# Windows (Git Bash)
source venv/Scripts/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure a API Key**
```bash
# Crie um arquivo .env na raiz do projeto
cp .env.example .env

# Edite o .env e adicione sua chave:
GROQ_API_KEY=sua_chave_aqui
```

### Execução

**1. Extração de Requisitos**
```bash
python extrator_requisitos.py
```
Isso vai processar os 3 PDFs e gerar arquivos JSON em `outputs/`

**2. Matching com Catálogo**
```bash
python analisador_motores.py
```
Isso vai analisar cada requisito contra os 6 motores do catálogo*

### Resultados

Após a execução, você encontrará em `outputs/`:

- `Memorial Descritivo - Motor Bomba Industrial_requisitos.json`
- `Datasheet - Motor Industrial_requisitos.json`
- `Especificação Técnica - Motor Bomba Centrífuga_requisitos.json`
- `Memorial Descritivo - Motor Bomba Industrial_analise.json`
- `Datasheet - Motor Industrial_analise.json`
- `Especificação Técnica - Motor Bomba Centrífuga_analise.json`
- `requisitos_consolidados.json `

## 🧠 Decisões Técnicas e Justificativas

### Por que Groq?

**Problema**: Precisava de uma API LLM gratuita e confiável.

**Alternativas consideradas**:
- ❌ Google Gemini - Cota gratuita muito limitada (esgotada rapidamente)
- ❌ DeepSeek - Requer créditos mesmo na versão "gratuita"
- ❌ OpenAI - Requer cartão de crédito para validação

**Decisão**: Groq API com modelo Llama 3.3 70B

**Justificativa**:
- ✅ **100% gratuita** sem necessidade de cartão
- ✅ **Cota generosa** para desenvolvimento e testes
- ✅ **Muito rápida** (inferência otimizada por hardware)
- ✅ **Qualidade comparável** a modelos comerciais
- ✅ **Suporte a JSON estruturado** nativo (`response_format`)
- ✅ **Documentação clara** e interface compatível com OpenAI

**Impacto no negócio**: Permite desenvolvimento ágil sem custos, viabilizando iterações rápidas e testes extensivos.

---

### Por que PyPDF2 para extração de texto?

**Problema**: Groq não processa PDFs diretamente.

**Alternativas consideradas**:
- ❌ Claude API - Processa PDFs nativamente mas requer cartão
- ❌ OCR (Tesseract) - Complexidade desnecessária para PDFs com texto

**Decisão**: PyPDF2 para extração + Groq para análise

**Justificativa**:
- ✅ **Leve e eficiente** para PDFs com texto nativo
- ✅ **Sem dependências externas** pesadas
- ✅ **Código simples** e manutenível
- ✅ **Separação de responsabilidades** clara (extração vs. análise)

**Impacto no negócio**: Solução robusta e de baixo custo operacional, adequada para documentos técnicos padronizados.

---

### Por que análise com LLM no matching?

**Problema**: Matching puramente algorítmico seria muito rígido.

**Alternativas consideradas**:
- ❌ Regras hardcoded - Inflexível, não captura nuances
- ❌ Machine Learning tradicional - Requer dataset de treinamento

**Decisão**: LLM para análise contextual de compatibilidade

**Justificativa**:
- ✅ **Entende nuances técnicas** (ex: "variação de 2% é aceitável")
- ✅ **Flexibilidade** para diferentes tipos de requisitos
- ✅ **Justificativas em linguagem natural** para decisões
- ✅ **Considera trade-offs** (custo vs. eficiência)
- ✅ **Adaptável** sem reprogramação

**Impacto no negócio**: Mimifica análise de um engenheiro experiente, gerando recomendações com contexto e justificativa técnica.

---

### Por que JSON estruturado?

**Problema**: Saída precisa ser padronizada e processável.

**Decisão**: Schemas JSON rígidos com validação

**Justificativa**:
- ✅ **Integrável** com sistemas legados
- ✅ **Versionável** e rastreável
- ✅ **Validável** programaticamente
- ✅ **Legível** para humanos e máquinas
- ✅ **Padrão da indústria** para APIs

**Impacto no negócio**: Facilita integração futura com ERP, CRM ou sistemas de cotação automatizada.

---

### Por que incluir PDFs no repositório?

**Problema**: Reprodutibilidade vs. tamanho do repositório.

**Decisão**: Incluir PDFs e outputs

**Justificativa**:
- ✅ **Reprodutibilidade completa** - avaliadores podem testar
- ✅ **Validação cruzada** - comparar saídas com entradas
- ✅ **Documentação viva** - exemplos reais de uso
- ✅ **Tamanho aceitável** - PDFs são pequenos (~500KB cada)

**Impacto no negócio**: Demonstra transparência e facilita validação técnica pela equipe avaliadora.

---

## 📊 Exemplo de Resultado

### Extração de Requisitos
```json
{
  "documento_origem": "Memorial_Descritivo_-_Motor_Bomba_Industrial.pdf",
  "requisitos": {
    "eletricos": {
      "potencia_kw": 15.0,
      "tensao_v": 380,
      "eficiencia": "IE3"
    },
    "operacionais": {
      "grau_protecao": "IP55",
      "regime_trabalho": "S1"
    }
  },
  "confianca_extracao": {
    "eletricos": 0.95,
    "mecanicos": 0.90
  }
}
```

### Análise de Matching
```json
{
  "analise_catalogo": {
    "recomendacao_principal": "WEG-00158ET3EM160M-W22",
    "resultados": [
      {
        "codigo_produto": "WEG-00158ET3EM160M-W22",
        "score_adequacao": 95.5,
        "classificacao": "RECOMENDADO",
        "analise_detalhada": {
          "atendidos": ["potencia_exata", "tensao_compativel", "eficiencia_ie3"],
          "superiores": ["garantia_24_meses"]
        }
      }
    ]
  }
}
```
## 🖥️ Interface Streamlit - Funcionalidades

A interface web desenvolvida com Streamlit proporciona uma experiência visual e interativa para exploração dos resultados da análise.

### Requisitos Extraídos

- **Visualização Consolidada:** Mostra requisitos extraídos dos 3 PDFs
- **Rastreabilidade:** Lista todos os documentos fonte utilizados
- **Informações Faltantes:** Lista clara de campos não encontrados
- **Visualizador JSON:** Acesso ao JSON completo para conferência

### Como Executar a Interface

```bash
streamlit run app_streamlit.py
```

**Requisitos:** 
- Execução prévia de `extrator_requisitos.py` e `analisador_motores.py`
- Arquivos `requisitos_consolidados.json` e `analise_matching.json` em `outputs/`

## 🛠️ Relatório Técnico: Saneamento do Catálogo de Motores

### Contexto do Problema
O arquivo original apresentava erros de sintaxe que impediam o carregamento por meio da biblioteca padrão json do Python. Os principais problemas foram:

1. **Ausência de Delimitadores:** Vários objetos de fabricantes (WEG, Siemens, SEW, etc.) estavam listados sequencialmente sem a separação obrigatória por vírgulas ,.

**Truncamento de Arquivo (EOF):** O arquivo terminava abruptamente antes do fechamento das chaves principais }, resultando em um JSON inválido.

**Duplicação de Chaves:** Existência de chaves duplicadas dentro do mesmo escopo de fabricante.

2. **Ações Corretivas**
Para viabilizar o projeto, foram realizadas as seguintes etapas de Data Cleaning:

**Normalização Estrutural:** Reconstrução da árvore do JSON, garantindo que cada fabricante fosse um objeto dentro de uma lista mestre.

**Fechamento de Escopo:** Reestruturação das chaves de fechamento para garantir que o interpretador Python (json.load()) pudesse ler o arquivo do início ao fim sem erros de JSONDecodeError.

**Em caso real:** Eu notificaria a equipe responsável pelo catálogo para a correção do problema ser feita antes das análises serem finalizadas, sem comprometer o catálogo.

## 🎓 Aprendizados e Melhorias Futuras

### O que funcionou bem
- ✅ Integração com Groq foi estável e rápida
- ✅ PyPDF2 extraiu texto com boa qualidade
- ✅ Estrutura JSON facilitou debugging
- ✅ Separação extração/matching facilitou testes

### Desafios enfrentados
- ⚠️ Limitações de cota em outras APIs (Gemini, DeepSeek)
- ⚠️ Formatação inconsistente entre os PDFs
- ⚠️ Necessidade de prompts bem estruturados
- ⚠️ Visualização no Streamlit

### Melhorias futuras
- 🔄 Interface web com Streamlit mais completa (código atual precisa de ajustes)
- 🔄 Validação de schemas com Pydantic
- 🔄 Testes unitários com pytest
- 🔄 CI/CD com GitHub Actions
- 🔄 Containerização com Docker
- 🔄 API REST com FastAPI
- 🔄 Dashboard de visualização de resultados
- 🔄 Suporte a múltiplos idiomas

## 📝 Documentação de Prompts

Os prompts utilizados foram estruturados seguindo boas práticas:

1. **Contexto claro** - "Você é um engenheiro especializado..."
2. **Formato de saída explícito** - Schema JSON detalhado
3. **Regras específicas** - "Use null para valores não encontrados"
4. **Exemplos** - Template preenchido no prompt
5. **Restrições** - "Retorne APENAS JSON, sem markdown"

Prompts completos disponíveis nos arquivos `extrator_requisitos.py` e `analisador_motores.py`.

## 🤝 Contribuindo

Este é um projeto acadêmico para processo seletivo, mas sugestões são bem-vindas!

## 📄 Licença

Este projeto foi desenvolvido como parte de um desafio técnico para a Siemens Energy.

## 👤 Autora

**Ana Luíza Righi Schleich** - Candidata a Bolsista IEL Siemens Energy
- Formação: Ciência da Computação
- GitHub: [(https://github.com/anaschleich)]
- LinkedIn: [(https://www.linkedin.com/in/anaschleich)]

---

**Desenvolvido com ❤️ para o desafio Siemens Energy - Janeiro 2026**
