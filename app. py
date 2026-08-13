import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Simulador Imobiliário Bauru", layout="wide")

st.title("🏆 Simulador Imobiliário Master - Bauru")
st.markdown("Altere os dados no painel abaixo para ver o resultado e o gráfico mudarem em tempo real no seu celular.")

# --- 📱 PAINEL INTERATIVO DE ENTRADA DE DADOS ---
st.subheader("💰 Seu Capital Inicial")
dinheiro_total_guardado = st.number_input("Capital total que você tem guardado hoje (R$)", value=250000, step=5000)

st.subheader("🏡 Condições de Compra do Imóvel")
col_compra1, col_compra2 = st.columns(2)
with col_compra1:
    v_imovel_anuncio = st.number_input("Valor de anúncio do imóvel (R$)", value=250000, step=5000)
    desconto_a_vista = st.slider("Desconto negociado à vista (%)", 0.0, 20.0, 8.0, 0.5)
with col_compra2:
    v_condominio_inicial = st.number_input("Taxa de Condomínio mensal (R$)", value=420, step=10)
    valor_venal_exato = st.number_input("Valor Venal para cálculo de IPTU (R$)", value=130000, step=5000)

st.subheader("📈 Condições de Aluguel")
v_aluguel_mensal_inicial = st.number_input("Aluguel mensal inicial sugerido (R$)", value=1000, step=50)

st.subheader("🔮 Cenário Econômico do Brasil")
col_eco1, col_eco2 = st.columns(2)
with col_eco1:
    periodo_simulacao_meses = st.slider("Prazo de análise da simulação (Meses)", 1, 120, 60, 1)
    tendencia_da_selic = st.selectbox("Tendência futura da Taxa Selic", ["Queda Gradual", "Alta Gradual", "Estável"])
with col_eco2:
    taxa_selic_hoje = st.slider("Taxa Selic atual do país (% a.a.)", 2.0, 20.0, 14.0, 0.25) / 100
    cdi_performance = st.slider("Rentabilidade da sua Renda Fixa (% do CDI)", 90.0, 120.0, 105.0, 1.0) / 100

val_imovel_ano = 0.06 # Média padrão de Bauru
inflacao_ano = 0.04   # Meta padrão de inflação

# --- 🧮 PROCESSAMENTO MATEMÁTICO CONTÍNUO ---
v_imovel_venda = v_imovel_anuncio * (1 - (desconto_a_vista / 100))
v_iptu_mes_inicial = (valor_venal_exato * 0.01) / 12
total_custos_atrito = (v_imovel_venda * 0.02) + (v_imovel_venda * 0.018)
remanente_entrada_compra = v_imovel_venda + total_custos_atrito

val_mensal_imovel = (1 + val_imovel_ano)**(1/12) - 1
inflacao_mensal = (1 + inflacao_ano)**(1/12) - 1

dados = []
saldo_banco_pos_compra = dinheiro_total_guardado - remanente_entrada_compra
imovel_fisico = v_imovel_venda
saldo_banco_alugar = dinheiro_total_guardado

aluguel_vigente = v_aluguel_mensal_inicial
condominio_vigente = v_condominio_inicial
iptu_vigente = v_iptu_mes_inicial

for mes in range(0, periodo_simulacao_meses + 1):
    if mes == 0:
        selic_atual = taxa_selic_hoje
    else:
        if tendencia_da_selic == "Queda Gradual":
            selic_atual = max(0.10, taxa_selic_hoje - (mes * 0.0011))
        elif tendencia_da_selic == "Alta Gradual":
            selic_atual = min(0.18, taxa_selic_hoje + (mes * 0.0008))
        else:
            selic_atual = taxa_selic_hoje
            
        if mes % 12 == 1 and mes > 1:
            aluguel_vigente *= (1 + inflacao_ano)
            condominio_vigente *= (1 + inflacao_ano)
            iptu_vigente *= (1 + inflacao_ano)
            
        imovel_fisico *= (1 + val_mensal_imovel)
        custo_manutencao_mes = (imovel_fisico * 0.005) / 12
        
        rend_mensal_cdi_liq = (((1 + (selic_atual * cdi_performance))**(1/12)) - 1) * 0.85
        
        custo_comprar_mes = condominio_vigente + iptu_vigente + custo_manutencao_mes
        custo_alugar_mes = aluguel_vigente + condominio_vigente + iptu_vigente
        
        saldo_banco_pos_compra = (saldo_banco_pos_compra * (1 + rend_mensal_cdi_liq)) - custo_comprar_mes
        saldo_banco_alugar = (saldo_banco_alugar * (1 + rend_mensal_cdi_liq)) - custo_alugar_mes

    patrimonio_comprar_total = imovel_fisico + saldo_banco_pos_compra
    dados.append({"Mês": mes, "COMPRAR": patrimonio_comprar_total, "ALUGAR": saldo_banco_alugar})

df = pd.DataFrame(dados)
patr_final_comprar = dados[-1]["COMPRAR"]
patr_final_alugar = dados[-1]["ALUGAR"]

# --- 🖥️ EXIBIÇÃO EM TEMPO REAL ---
st.markdown("---")
st.subheader("📊 Patrimônio Acumulado no Final do Prazo:")
res_col1, res_col2 = st.columns(2)
with res_col1:
    st.metric("🏡 Cenário Comprar Imóvel", f"R$ {patr_final_comprar:,.2f}")
with res_col2:
    st.metric("📈 Cenário Alugar e Investir", f"R$ {patr_final_alugar:,.2f}")

if patr_final_comprar > patr_final_alugar:
    st.success(f"🌟 VEREDITO FINANCEIRO: **COMPRAR** é melhor por R$ {patr_final_comprar - patr_final_alugar:,.2f}!")
else:
    st.info(f"🌟 VEREDITO FINANCEIRO: **ALUGAR E INVESTIR** é melhor por R$ {patr_final_alugar - patr_final_comprar:,.2f}!")

# --- 📈 GRÁFICO INTERATIVO ---
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["Mês"], df["COMPRAR"], label="Se Comprar (Imóvel + Sobras)", color="green", linewidth=2.5)
ax.plot(df["Mês"], df["ALUGAR"], label="Se Alugar (Dinheiro no Banco)", color="blue", linewidth=2.5)
ax.set_xlabel("Meses de Simulação")
ax.set_ylabel("Patrimônio Líquido (R$)")
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
st.pyplot(fig)
