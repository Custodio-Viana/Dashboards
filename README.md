# 🌱 Comparador de Fertilizantes – Dashboard Interativo

Dashboard desenvolvido em Streamlit + Plotly para análise comparativa de fertilizantes, com foco em:

Composição N-P-K

Custo por hectare

Eficiência econômica (Custo por Unidade de Azoto)

Segmentação por Categoria, Fabricante e Tecnologia

## 🎯 Objetivo do Projeto

Criar uma ferramenta visual para apoiar decisões técnicas e econômicas na escolha de fertilizantes, permitindo comparar:

Produtos Premium vs Econômicos

Tecnologias (CRF, Nitrogenados Puros, Equilibrados, etc.)

Custo real por unidade de nutriente aplicado

## 📊 Principais Métricas
🔹 Composição N-P-K

Visualização comparativa da concentração de Nitrogênio (N), Fósforo (P) e Potássio (K) por produto.

🔹 Custo por Hectare

Análise direta do custo total de aplicação por hectare.

🔹 Eficiência Econômica

Cálculo estratégico:

Unidades de N por Ha = KG_por_Ha × (N / 100)

Custo por Unidade de N = Custo_por_Ha / Unidades_N_Ha


Isso permite identificar:
✔ Qual produto entrega mais nitrogênio por euro investido
✔ Ranking do fertilizante mais eficiente

## 🛠 Tecnologias Utilizadas

- Python
- Streamlit
- Pandas
- Plotly Express
- Plotly Graph Objects

## 📂 Estrutura do Projeto
Dashboards/
│
├── dashboard_fertilizantes.py
├── Fertilizante.csv
├── requirements.txt
└── README.md

# 🚀 Como Executar o Projeto
1️⃣ Clonar repositório
git clone https://github.com/Custodio-Viana/Dashboards.git
cd Dashboards

2️⃣ Criar ambiente virtual
python -m venv venv
venv\Scripts\activate   # Windows

3️⃣ Instalar dependências
pip install -r requirements.txt

4️⃣ Executar
streamlit run dashboard_fertilizantes.py

# 📈 Diferencial do Projeto

Este projeto vai além de visualização básica:
- Implementa limpeza automática de colunas
- Trata múltiplos encodings
- Aplica cache de dados
- Calcula métrica de eficiência real por nutriente
- Permite filtros dinâmicos via sidebar

👨‍💻 Autor

Custódio Viana

[LinkedIn](https://www.linkedin.com/in/custodio-viana/)  /  [GitHub](https://github.com/Custodio-Viana)