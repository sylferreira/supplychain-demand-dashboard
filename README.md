# # Inventory Dashboard

Um dashboard interativo em **Python + Plotly Dash** para monitorar **estoques, demanda e performance operacional** em cadeias de suprimentos.

Este projeto foi desenvolvido como parte de um portfólio de análise de dados em Supply Chain, utilizando dados simulados e boas práticas de visualização e storytelling com Python.

---

## Funcionalidades

- **Resumo de inventário** por categoria de produto  
- **Heatmap de desempenho** (Available vs Demand)  
- **Tendência temporal de demanda**  
- **Alertas automáticos** quando a demanda excede a disponibilidade  
- **Design responsivo com Bootstrap**

---

## Stack utilizada

- **Python 3.10+**
- **Plotly Dash**
- **Pandas**
- **Dash Bootstrap Components**

---

## Como executar localmente

```bash
# Clone o repositório
git clone https://github.com/sylfferreira/supplychain-demand-dashboard.git

# Acesse a pasta
cd supplychain-demand-dashboard

# Crie o ambiente virtual (opcional)
python -m venv venv
source venv/bin/activate  # no Linux/Mac
venv\Scripts\activate     # no Windows

# Instale as dependências
pip install -r requirements.txt

# Execute o app
python app.py
