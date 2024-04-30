import pandas as pd
import requests
import yfinance as yf
import warnings
import streamlit as st
warnings.filterwarnings('ignore', category=FutureWarning)

# streamlit title
st.title('Earnings Yield')

# streamlit stock ticker input
company_code = st.sidebar.text_input('Stock tricker',value='AAPL')

df_stock = yf.download(company_code, interval='1d', start='2014-01-01')


#income statement
url = f"https://financialmodelingprep.com/api/v3/income-statement/{company_code}?period=quarter&apikey=e3e1ef68f4575bca8a430996a4e11ed1"
response = requests.get(url)
income = response.json()
income = pd.DataFrame(income)
# Clone the DataFrame to ensure you're working on a copy, not a view
eps = income[["fillingDate", "ebitda", "depreciationAndAmortization", "weightedAverageShsOutDil", "date"]].copy()
eps["ebit"] = eps["ebitda"] - eps["depreciationAndAmortization"]
eps["eps"] = eps["ebit"] / eps["weightedAverageShsOutDil"]
eps.set_index('fillingDate', inplace=True)
eps.index = pd.to_datetime(eps.index)

# Now join the DataFrames
result = df_stock.join(eps, how='left')  # or 'outer', 'left', 'right'
result['eps'] = result['eps'].fillna(method='ffill')
result["ebitda"] = result["ebitda"].fillna(method='ffill')  
result["ebit"] = result["ebit"].fillna(method='ffill')
result["date"] = result["date"].fillna(method='ffill')
result["depreciationAndAmortization"] = result["depreciationAndAmortization"].fillna(method='ffill')
result["weightedAverageShsOutDil"] = result["weightedAverageShsOutDil"].fillna(method='ffill')

result = result.sort_index(ascending=False)
result["E/P"] = result["eps"]*4/ result["Adj Close"]

st.sidebar.text((f"latest financial report:"))
st.sidebar.code({result['date'][0]})
col1, col2 = st.columns([1,1])
with col1:
    st.code(f"last price: {result['Adj Close'][0]:,.2f}")
with col2:
    st.code(f"E/P: {result['E/P'][0]:,.4f}")


with st.expander("Details"):



    st.text("Quarterly")
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
          st.code(f"ebitda: {result['ebitda'][0]:,.0f}")

    with col2:
        st.code(f"DA: {result['depreciationAndAmortization'][0]:,.0f}")

    with col3:
        st.code(f"EBIT: {result['ebit'][0]:,.0f}")
    st.code(f"Share Outstandging (diluted): {result['depreciationAndAmortization'][0]:,.0f}")
    st.code(f"Annually EPS (quarterly x4): {result['eps'][0]*4:,.2f}")

st.line_chart(result['E/P'])

