import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Mengatur tema visualisasi
sns.set_theme(style="darkgrid")

# Menyiapkan Judul Dashboard
st.set_page_config(page_title="Air Quality Dashboard", page_icon="☁️", layout="wide")
st.title("☁️ Dashboard Analisis Kualitas Udara")
st.markdown("**Studi Kasus:** 5 Stasiun di Beijing (Aotizhongxin, Changping, Dingling, Dongsi, Guanyuan)")

# ----------------------------------------------------------------
# FUNGSI UNTUK MEMUAT DATA
# ----------------------------------------------------------------
@st.cache_data
def load_data():
    # Membaca data yang sudah dibersihkan dari Jupyter Notebook
    df = pd.read_csv("main_data.csv")
    
    # Mengembalikan kolom 'datetime' menjadi tipe data datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

air_quality_df = load_data()

# ----------------------------------------------------------------
# SIDEBAR UNTUK FILTER INTERAKTIF
# ----------------------------------------------------------------
st.sidebar.header("Filter Analisis ⚙️")

# Filter Tahun untuk Analisis 1
tahun_pilihan = st.sidebar.selectbox(
    "Pilih Tahun (Untuk Analisis PM2.5):",
    options=air_quality_df['year'].unique(),
    index=1 # Default ke tahun 2014
)

# Filter Stasiun untuk Analisis 2
stasiun_pilihan = st.sidebar.selectbox(
    "Pilih Stasiun (Untuk Analisis Dampak Angin):",
    options=air_quality_df['station'].unique(),
    index=0 # Default ke Aotizhongxin
)

st.sidebar.markdown("---")
st.sidebar.markdown("Dibuat oleh: **RIZAL FATHURRAHMAN**") # Jangan lupa ganti nama kamu!

# ----------------------------------------------------------------
# VISUALISASI 1: PERBANDINGAN PM2.5 ANTAR STASIUN
# ----------------------------------------------------------------
st.subheader(f"📊 Perbandingan Rata-rata PM2.5 Antar Stasiun (Tahun {tahun_pilihan})")

# Memfilter data sesuai tahun pilihan pengguna di sidebar
df_tahun = air_quality_df[air_quality_df['year'] == tahun_pilihan]
mean_pm25 = df_tahun.groupby('station')['PM2.5'].mean().sort_values(ascending=False).reset_index()

# Membuat Canvas Grafik 1
fig1, ax1 = plt.subplots(figsize=(10, 5))
colors = ['#D32F2F' if i == 0 else '#388E3C' if i == len(mean_pm25)-1 else '#BDBDBD' for i in range(len(mean_pm25))]

sns.barplot(
    x='PM2.5', 
    y='station', 
    data=mean_pm25, 
    palette=colors,
    hue='station',
    legend=False,
    ax=ax1
)
ax1.set_xlabel('Konsentrasi PM2.5 (µg/m³)')
ax1.set_ylabel('Nama Stasiun')

# Menampilkan grafik 1 di Streamlit
st.pyplot(fig1)

with st.expander("Lihat Penjelasan Grafik 1"):
    st.write(f"Grafik di atas menunjukkan perbandingan tingkat polusi udara (PM2.5) pada tahun {tahun_pilihan}. Warna **merah** menandakan stasiun dengan polusi tertinggi, sedangkan warna **hijau** adalah stasiun dengan udara terbersih.")

st.markdown("---")

# ----------------------------------------------------------------
# VISUALISASI 2: DAMPAK ANGIN TERHADAP PM10 (BINNING/CLUSTERING)
# ----------------------------------------------------------------
st.subheader(f"🌬️ Dampak Kecepatan Angin Terhadap PM10 di {stasiun_pilihan} (Musim Dingin)")

# Memfilter data untuk stasiun pilihan pengguna dan khusus musim dingin
winter_months = [12, 1, 2]
winter_data = air_quality_df[(air_quality_df['station'] == stasiun_pilihan) & 
                             (air_quality_df['month'].isin(winter_months))].copy()

# Melakukan Binning
batas_kecepatan = [0, 1.5, 3.0, winter_data['WSPM'].max()]
label_kategori = ['Pelan', 'Sedang', 'Kencang']
winter_data['kategori_angin'] = pd.cut(winter_data['WSPM'], bins=batas_kecepatan, labels=label_kategori, include_lowest=True)

# Menghitung rata-rata
pm10_by_wind = winter_data.groupby('kategori_angin', observed=True)['PM10'].mean().reset_index()

# Membuat Canvas Grafik 2
fig2, ax2 = plt.subplots(figsize=(8, 5))
sns.barplot(
    x='kategori_angin', 
    y='PM10', 
    data=pm10_by_wind,
    palette='Blues_r',
    hue='kategori_angin',
    legend=False,
    ax=ax2
)
ax2.set_xlabel('Kategori Kecepatan Angin')
ax2.set_ylabel('Rata-rata Konsentrasi PM10 (µg/m³)')

# Menampilkan grafik 2 di Streamlit
st.pyplot(fig2)

with st.expander("Lihat Penjelasan Grafik 2"):
    st.write(f"Grafik ini menerapkan teknik **Clustering (Binning)** pada kecepatan angin di stasiun {stasiun_pilihan}. Dapat dilihat bahwa semakin kencang angin bertiup di musim dingin, konsentrasi partikel PM10 cenderung menurun karena tersapu oleh hembusan angin.")