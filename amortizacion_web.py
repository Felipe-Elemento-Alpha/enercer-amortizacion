import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf


st.set_page_config(page_title="Amortizacion", layout="wide")
st.title("Amortizacion")

def fmt_money(x: float) -> str:
    try:
        return "${:,.2f}".format(float(x))
    except Exception:
        return ""

with st.form("tabla_inicial"):
    col_left, col_right = st.columns([1.3, 1])

    with col_left:

        inversion_total = st.number_input("Inversión Total", min_value=0.0, value=0.0, step=1_000_000.0, format="%.2f")
        
        porcentaje_cuota_incial = st.number_input("Porcentaje Cuota Incial", min_value=0.0, max_value=1.0, value=0.0, step=0.1, format="%.2f")
        
        num_cuotas = st.number_input("Número de Cuotas", min_value=1, value=12, step=1)
        
        forma_pago = st.selectbox("Forma de Pago", options=[
            "Mensual", "Bimestral", "Trimestral", "Cuatrimestral", "Semestral", "Anual"
        ], index=0)

        tem =  st.number_input("%TEM", min_value=0.0, max_value=1.0, value=0.0, step=0.1, format="%.3f",help="Ejemplo: 0.015 = 1.5%")    
        
        if forma_pago == "Anual":
            tasa_aplicar = ((1 + tem) ** 12) - 1
        elif forma_pago == "Semestral":
            tasa_aplicar = ((1 + tem) ** 6) - 1
        elif forma_pago == "Cuatrimestral":
            tasa_aplicar = ((1 + tem) ** 4) - 1
        elif forma_pago == "Trimestral":
            resultado = ((1 + tem) ** 3) - 1
        elif forma_pago == "Bimestral":
            tasa_aplicar = ((1 + tem) ** 2) - 1
        else:
            tasa_aplicar = tem

    with col_right:

        cuota_inicial = inversion_total * porcentaje_cuota_incial
        valor_financiar = inversion_total - cuota_inicial
    
        if abs(valor_financiar) < 1e-9:
            valor_financiar = 0.0

        pago = npf.pmt(tasa_aplicar, num_cuotas, -valor_financiar)

        st.metric("Cuota Incial", fmt_money(cuota_inicial))
        st.metric("Valor a Financiar", fmt_money(valor_financiar))
        st.metric("Tasa Aplicar", f"{tasa_aplicar:.2%}")
        st.metric("PAGO", fmt_money(pago))

    submitted = st.form_submit_button("Calcular / Actualizar")

st.subheader("Tabla de resultados (flujo)")

factor_periodicidad = {
    "Mensual": 1,
    "Bimestral": 2,
    "Trimestral": 3,
    "Cuatrimestral": 4,
    "Semestral": 6,
    "Anual": 12,
}
k = factor_periodicidad.get(forma_pago, 1)

cuotas = list(range(0, int(num_cuotas) + 1))


valor_cuota = []
saldo_series = []
interese_series = []
capital_series =[]



for idx, t in enumerate(cuotas):
    if t == 0:
        valor_t = 0.0
        interes_t= 0.0
        capital_t= 0.0
        saldo_t = valor_financiar

    else:
        valor_t = pago
        saldo_t_prev = saldo_series[-1]
        interes_t = saldo_t_prev * tasa_aplicar
        capital_t = valor_t - interes_t

        saldo_t = max(saldo_t_prev - capital_t, 0.0)

    valor_cuota.append(valor_t)
    saldo_series.append(saldo_t)
    interese_series.append(interes_t)
    capital_series.append(capital_t)


df_res = pd.DataFrame({
    "# Cuota": cuotas,
    "Valor de Cuota": [fmt_money(x) if t>=1 else "" for t,x in zip(cuotas, valor_cuota)],
    "Intereses": [fmt_money(x) for x in interese_series],
    "Capital": [fmt_money(x) for x in capital_series],
    "Saldo": [fmt_money(x) for x in saldo_series]

})

st.dataframe(df_res, use_container_width=True, hide_index=True)