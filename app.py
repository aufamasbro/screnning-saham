import streamlit as st
import yfinance as yf
import pandas as habib
import mplfinance as auf

st.set_page_config(page_title="Screener Saham AUF", layout="centered")

st.subheader(" SCREENER SAHAM GAIN 7% - 15%")
st.caption("by AUF")

kode_saham = st.text_input("Masukkan Kode Saham:", "BRMS.JK").upper()

if st.button("Analisa"):
    data = yf.download(kode_saham, start="2024-01-01")

    if data.empty:
        st.error("tingkatkan lagi ketelitian anda!")
    else:
        if isinstance(data.columns, habib.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data['MA20'] = data['Close'].rolling(20).mean()
        data['MA50'] = data['Close'].rolling(50).mean()
        data['MA5'] = data['Close'].rolling(5).mean()
        data['Vol_MA50'] = data['Volume'].rolling(50).mean()
        data['Typical_Price'] = (data['High'] + data['Low'] + data['Close']) / 3
        data['VP'] = data['Typical_Price'] * data['Volume']
        data['VWAP60'] = data['VP'].rolling(60).sum() / data['Volume'].rolling(60).sum()

        df_plot = data.tail(180).copy()
        garis_tambahan = [
            auf.make_addplot(df_plot['MA20'], color='blue', width=1.2),
            auf.make_addplot(df_plot['MA50'], color='orange', width=1.2),
            auf.make_addplot(df_plot['MA5'], color='purple', width=1.2),
            auf.make_addplot(df_plot['Vol_MA50'], panel=1, color='pink', width=1.2),
            auf.make_addplot(df_plot['VWAP60'], color='white', width=1.5)
        ]

        warna_lilin = auf.make_marketcolors(up='green', down='red', edge='inherit', wick='inherit', volume={'up': 'green', 'down': 'red'})

        Hb = auf.make_mpf_style(marketcolors=warna_lilin, facecolor='#1e222d', figcolor='white', gridcolor='grey', gridstyle='--')

        fig, _ = auf.plot(
            df_plot, type='candle',
            volume=True,
            addplot=garis_tambahan,
            style=Hb,
            title=f"\nCHART BY AUF - {kode_saham}",
            figsize=(12, 7),
            panel_ratios=(3, 1), returnfig=True
        )

        st.pyplot(fig)

        data_clean = data.dropna(subset=['MA5', 'MA20', 'MA50', 'VWAP60'])
        hari_ini = data_clean.iloc[-1]

        ma20_hari_ini = hari_ini['MA20'].item()
        ma50_hari_ini = hari_ini['MA50'].item()
        ma5_hari_ini = hari_ini['MA5'].item()
        vol_hari_ini = hari_ini['Volume'].item()
        vol_rata_rata = hari_ini['Vol_MA50'].item()
        move_bandar = hari_ini['Close'].item() > hari_ini['VWAP60'].item()

        ma5 = hari_ini['MA5'].item()
        ma20 = hari_ini['MA20'].item()
        ma50 = hari_ini['MA50'].item()
        is_uptrend = ma5 > ma20 > ma50

        st.markdown(f"📊 ANALISIS UNTUK {kode_saham}:")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lonjakan Volume", f"{'✅ Ada Breakout' if vol_hari_ini > (vol_rata_rata * 2.0) else '❌ Normal/Sepi'}")
            st.metric("Akumulasi ", f"{'✅ (Akumulasi)' if move_bandar else '❌ Di Bawah Bandar Line (Distribusi)'}")
        with col2:
            st.metric("TRIPLE MA CROSSING", f"{'✅ Uptrend' if is_uptrend else '❌ Downtrend'}")
            
        with st.expander("DETAIL Angka MA"):
            st.write(f"- **MA5**: {ma5:.2f}")
            st.write(f"- **MA20**: {ma20:.2f}")
            st.write(f"- **MA50**: {ma50:.2f}")
            
        st.markdown("---")
        if is_uptrend and vol_hari_ini > (vol_rata_rata * 2.0) and move_bandar:
            st.success("SINYAL: VERY BUY 7% - 15%")
        elif is_uptrend and vol_hari_ini > (vol_rata_rata * 2.0):
            st.info("SINYAL: BUY 1% - 5%")
        elif vol_hari_ini > (vol_rata_rata * 2.0) and move_bandar:
            st.info("SINYAL: BUY 1% - 5%")
        else:
            st.error("SINYAL: SELL or DON'T ENTRY")
    
