import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np


# Column Data yang tersedia setiap barisnya adalah sum atas semua baris diatasnya (perubahan nilai)
# untuk mencari dosis harian dan drop column awal (yang terdapat data perubahan nilai)
def harian(col):
    new_col = col + " harian"
    statistik_harian_clean[new_col] = statistik_harian_clean[col].diff().fillna(statistik_harian_clean[col])
    statistik_harian_clean.drop(columns=[col], inplace=True)


st.title("Kasus & Vaksinasi Covid-19")
st.sidebar.subheader("Pengaturan Grafik")
#file uploader
uploaded_file = st.sidebar.file_uploader(label='Upload file Covid-19', type=['xlsx'])

# selector untuk cat
cat_select = st.sidebar.selectbox(
    label="Pilih Kategori",
    options=["Kasus Aktif", "Vaksinasi"]
)

if uploaded_file is not None:
    daily_cases = pd.read_excel(uploaded_file, sheet_name = 'Kasus Aktif')
    statistik_harian = pd.read_excel(uploaded_file, sheet_name='Statistik Harian')

try:
    # Handling Missing Value
    daily_cases.fillna(0, inplace=True)
    daily_cases.set_index('Date', inplace=True)
    daily_cases['Indonesia'] = daily_cases.sum(axis=1)

    if cat_select == "Kasus Aktif":
        st.write("Data per 15 Maret 2020 s/d 23 Agustus 2021")
        # selector untuk Chart
        chart_select = st.sidebar.selectbox(
            label="Pilih Chart",
            options=["Perkembangan Kasus Aktif per Hari di Indonesia",
                     "Kasus Aktif per Provinsi"])
        if chart_select == "Perkembangan Kasus Aktif per Hari di Indonesia":
            sns.set_style('whitegrid')
            fig, axes = plt.subplots(figsize=(20, 6))
            ax = sns.lineplot(data=daily_cases, x='Date', y='Indonesia', color='red')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            ax.set_xlabel("")
            ax.set_ylabel("")
            # Set tick font size
            for label in (ax.get_xticklabels() + ax.get_yticklabels()):
                label.set_fontsize(15)
            ax.set_title("Perkembangan Kasus Aktif per Hari di Indonesia", fontsize=20,
                         pad=18)
            fig.tight_layout()
            st.pyplot(plt)
            gel_satu = daily_cases.loc[(daily_cases.index >= '2020-11-01') & (daily_cases.index <= '2021-01-31')]
            gel_dua = daily_cases.loc[(daily_cases.index >= '2021-05-01') & (daily_cases.index <= '2021-07-31')]

            puncak_gel_satu = "{:,.0f}".format(gel_satu['Indonesia'].max())
            puncak_gel_dua = "{:,.0f}".format(gel_dua['Indonesia'].max())

            # dtype tanggalnya adalah Timestamp
            tgl_puncak_satu = gel_satu['Indonesia'].idxmax().strftime('%d-%m-%Y')
            tgl_puncak_dua = gel_dua['Indonesia'].idxmax().strftime('%d-%m-%Y')

            st.write("Pada grafik terlihat bahwa kasus covid-19 aktif per hari di Indonesia mengalami kenaikan"
                     " seiring waktu dimana gelombang pertama terjadi mulai dari November 2020 sampai Januari 2021 "
                     "dengan puncaknya berada di Januari 2020. Gelombang kedua dimulai dari Mei 2021 sampai Juli 2021 "
                     "yang puncaknya adalah pada pertengahan Juli 2021. Pada gelombang kedua terdapat kenaikan yang sangat"
                     " drastis dibandingkan dengan gelombang pertama.")

            st.write(f"Puncak kasus aktif gelombang pertama adalah pada {tgl_puncak_satu}, "
                     f"yaitu sebanyak **{puncak_gel_satu}** kasus.")

            st.write(f"Puncak kasus aktif gelombang kedua adalah pada {tgl_puncak_dua}, yaitu sebanyak "
                     f"**{puncak_gel_dua}** kasus.")

            persen = "{:.2%}".format(gel_dua['Indonesia'].max() / gel_satu['Indonesia'].max())
            st.write(f"Terdapat kenaikan sebanyak **{persen}** pada puncak gelombang ke dua terhadap puncak kasus gelombang satu.")

            st.write("Bertepatan dengan gelombang kedua Covid-19, pemerintah memberlakukan Pembatasan Kegiatan Masyarakat (PPKM) Darurat yang dimulai 3 Juli 2021 "
                     "sampai 25 Juli 2021, laju kasus covid-19 terlihat menurun mulai pada pertengahan bulan Juli. Akan tetapi,"
                     " diperlukan analisis lebih lanjut untuk menentukan apakah PPKM tersebut memang efektif.")
        elif chart_select == "Kasus Aktif per Provinsi":
            #mengubah wide data menjadi long data
            daily_cases_melted = daily_cases.copy()
            daily_cases_melted = daily_cases.melt(var_name='Provinsi', value_name='Kasus', ignore_index=False)
            daily_cases_melted = daily_cases_melted.groupby('Provinsi',
                                                            as_index=False).sum().sort_values('Kasus', ascending=False,
                                                                                              ignore_index=True)
            # overwrite dataframe daily_cases_melted tanpa baris 'Indonesia'
            daily_cases_melted = daily_cases_melted.iloc[1:]

            # checkbox
            show_data = st.sidebar.checkbox("Tampilkan Tabel")

            #slider
            slider = st.sidebar.slider('Pilih Jumlah Provinsi', 1, 34, 1)
            #grafik
            sns.set_style('whitegrid')
            fig, axes = plt.subplots(figsize=(14, 6))
            ax = sns.barplot(data=daily_cases_melted.head(slider), x='Kasus', y='Provinsi', palette=("rocket"))
            ax.set_xlabel("")
            ax.set_ylabel("")
            # Set tick font size
            for label in (ax.get_xticklabels() + ax.get_yticklabels()):
                label.set_fontsize(15)
            ax.set_title("Kasus Aktif per Provinsi", fontsize=20, pad=18)
            fig.tight_layout()
            st.pyplot(plt)

            st.markdown("<p style='text-align: right; color: grey;font-size: 10px;'>*Grafik diurutkan "
                        "berdasarkan kasus terbanyak</p>", unsafe_allow_html=True)

            #table
            if show_data:
                st.write(daily_cases_melted)



    elif cat_select == "Vaksinasi":
        st.write("Data per 13 Januari 2021 s/d 23 Agustus 2021")
        statistik_harian.dropna(subset=['Date'], inplace=True)
        statistik_harian_clean = statistik_harian.iloc[:,[0,42,43,44,53,54,55,58,59,62,63,66,67,68,69,70,71]]
        statistik_harian_clean.fillna(0, inplace=True)
        statistik_harian_clean.set_index('Date', inplace=True)
        # drop row jika semua columns = 0
        statistik_harian_clean = statistik_harian_clean.loc[(statistik_harian_clean != 0).any(axis=1)]

        # Untuk mencari dosis harian dan drop column awal
        for column_name, _ in statistik_harian_clean.iteritems():
            harian(column_name)

        # selector untuk Chart
        chart_vaksin1 = "Perkembangan Vaksinasi di Indonesia"
        chart_vaksin2 = "Perkembangan Vaksinasi SDM Kesehatan di Indonesia"
        chart_vaksin3 = "Perkembangan Vaksinasi Petugas Publik di Indonesia"
        chart_vaksin4 = "Perkembangan Vaksinasi Lansia di Indonesia"
        chart_vaksin5 = "Perkembangan Vaksinasi Warga Umum di Indonesia"
        chart_vaksin6 = "Perkembangan Vaksinasi Remaja di Indonesia"
        chart_vaksin7 = "Perkembangan Vaksinasi Vakgor di Indonesia"

        chart_select = st.sidebar.selectbox(
            label="Pilih Chart",
            options=[chart_vaksin1, chart_vaksin2, chart_vaksin3, chart_vaksin4, chart_vaksin5,
                     chart_vaksin6, chart_vaksin7])
        choice = ""
        if chart_select == chart_vaksin1:
            dosis_satu = 'Dosis pertama harian'
            dosis_dua = 'Dosis kedua harian'
            dosis_tiga = 'Dosis ketiga harian'
            choice = st.sidebar.radio(
                "Pilih Jenis Chart", ["Line Chart", "Pie Chart"]
            )
        elif chart_select == chart_vaksin2:
            dosis_satu = 'Dosis pertama (SDM kesehatan) harian'
            dosis_dua = 'Dosis kedua (SDM kesehatan) harian'
            dosis_tiga = 'Dosis ketiga (SDM kesehatan) harian'
        elif chart_select == chart_vaksin3:
            dosis_satu = 'Dosis pertama (petugas publik) harian'
            dosis_dua = 'Dosis kedua (petugas publik) harian'
        elif chart_select == chart_vaksin4:
            dosis_satu = 'Dosis pertama (lansia) harian'
            dosis_dua = 'Dosis kedua (lansia) harian'
        elif chart_select == chart_vaksin5:
            dosis_satu = 'Dosis pertama (warga umum) harian'
            dosis_dua = 'Dosis kedua (warga umum) harian'
        elif chart_select == chart_vaksin6:
            dosis_satu = 'Dosis pertama (remaja) harian'
            dosis_dua = 'Dosis kedua (remaja) harian'
        elif chart_select == chart_vaksin7:
            dosis_satu = 'Dosis pertama (Vakgor) harian'
            dosis_dua = 'Dosis kedua (Vakgor) harian'

        if choice == "Pie Chart":
            pie, ax = plt.subplots(figsize=[10, 6])
            jlh_penduduk = 272229372
            vaksin_sekali = statistik_harian_clean['Dosis pertama harian'].sum() - statistik_harian_clean[
                'Dosis kedua harian'].sum() - statistik_harian_clean['Dosis ketiga harian'].sum()
            vaksin_duakali = statistik_harian_clean['Dosis kedua harian'].sum() - statistik_harian_clean[
                'Dosis ketiga harian'].sum()
            vaksin_tigakali = statistik_harian_clean['Dosis ketiga harian'].sum()
            belum_vaksin = jlh_penduduk - vaksin_sekali - vaksin_duakali - vaksin_tigakali

            y = [vaksin_sekali, vaksin_duakali, vaksin_tigakali, belum_vaksin]
            mylabels = ["Sudah vaksin sekali", "Sudah vaksin dua kali", "Sudah vaksin tiga kali",
                        "Belum vaksin sama sekali"]
            explode = [0.1, 0, 0, 0]
            color = ["#6b720c", "#968600", "#fa8950", "#ffa600"]
            plt.pie(y, labels=mylabels, autopct="%.2f%%", explode=explode, colors=color, textprops={'fontsize': 14})
            plt.title(chart_select, fontsize=22, pad=18)
            st.pyplot(plt)

            total_penduduk_vaksin = vaksin_sekali + vaksin_duakali + vaksin_tigakali
            persen_total_penduduk_vaksin = total_penduduk_vaksin/jlh_penduduk
            st.write(f"Dari {'{:,.0f}'.format(jlh_penduduk)} penduduk Indonesia setidaknya {'{:,.0f}'.format(total_penduduk_vaksin)} "
                     f"atau {'{:.2%}'.format(persen_total_penduduk_vaksin)} penduduk sudah menerima vaksin sekali.")
            st.markdown("<p style='text-align: left; color: grey;font-size: 10px;'>"
                        "Sumber: https://dukcapil.kemendagri.go.id/berita/baca/809/distribusi-penduduk-indonesia-"
                        "per-juni-2021-jabar-terbanyak-kaltara-paling-sedikit</p>", unsafe_allow_html=True)
        else:
            #grafik
            sns.set_style('whitegrid')
            fig, axes = plt.subplots(figsize=(20, 6))
            ax = sns.lineplot(data=statistik_harian_clean, x='Date', y=dosis_satu, color='red',
                              label='Dosis Pertama', linewidth=3)
            ax = sns.lineplot(data=statistik_harian_clean, x='Date', y=dosis_dua, color='green', label='Dosis Kedua',
                              linewidth=3)
            if chart_select == chart_vaksin1 or chart_select == chart_vaksin2:
                ax = sns.lineplot(data=statistik_harian_clean, x='Date', y=dosis_tiga, color='blue', label='Doses Ketiga',
                              linewidth=3)
            else:
                pass
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            ax.set_xlabel("")
            ax.set_ylabel("")
            # Set tick font size
            for label in (ax.get_xticklabels() + ax.get_yticklabels()):
                label.set_fontsize(15)
            plt.ticklabel_format(style='plain', axis='y')
            ax.set_title(chart_select, fontsize=22, pad=18)
            fig.tight_layout()
            plt.setp(ax.get_legend().get_texts(), fontsize='22')  # for legend text
            st.pyplot(plt)

            #catatan
            # dtype tanggalnya adalah Timestamp
            dosis_max_satu = "{:,.0f}".format(statistik_harian_clean[dosis_satu].max())
            tgl_max_satu = statistik_harian_clean[dosis_satu].idxmax().strftime('%d-%m-%Y')
            dosis_max_dua = "{:,.0f}".format(statistik_harian_clean[dosis_dua].max())
            tgl_max_dua = statistik_harian_clean[dosis_dua].idxmax().strftime('%d-%m-%Y')
            st.write(f"- Pemberian vaksinasi terbanyak untuk dosis satu adalah pada tanggal {tgl_max_satu} sebanyak {dosis_max_satu}")
            st.write(f"- Pemberian vaksinasi terbanyak untuk dosis dua adalah pada tanggal {tgl_max_dua} sebanyak {dosis_max_dua}")
            if chart_select == chart_vaksin1 or chart_select == chart_vaksin2:
                dosis_max_tiga = "{:,.0f}".format(statistik_harian_clean[dosis_tiga].max())
                tgl_max_tiga = statistik_harian_clean[dosis_tiga].idxmax().strftime('%d-%m-%Y')
                st.write(f"- Pemberian vaksinasi terbanyak untuk dosis tiga adalah pada tanggal {tgl_max_tiga} sebanyak {dosis_max_tiga}")
            else:
                pass


            if chart_select == chart_vaksin1:
                st.write(f"Pemberian dosis satu terbanyak pada tanggal {tgl_max_satu} didukung oleh berita yang diliput oleh CNN, "
                         f"namun sayangnya alasan mengapa rekor ini dicapai tidak dijelaskan.")
                st.write("Dalam data ini juga diketahui bahwa satu-satunya kelompok masyarakat yang sudah mendapatkan dosis ketiga adalah SDM Kesehatan")
                st.markdown("<p style='text-align: left; color: grey;font-size: 10px;'>"
                            "Sumber: https://www.cnnindonesia.com/nasional/20210714181248-20-667768/data-"
                            "satgas-vaksinasi-covid-hari-ini-tembus-24-juta</p>", unsafe_allow_html=True)
            elif chart_select == chart_vaksin7:
                st.write("Informasi tambahan:")
                st.write("Vaksin gotong royong atau Vakgor ini adalah pemberian vaksin COVID-19 kepada karyawan dan keluarga yang pendanaanya ditanggung oleh perusahaan."
                         "Menurut Peraturan Menteri Kesehatan RI No. 10 Tahun 2021, vaksinasi mandiri ini bisa dilakukan di fasilitas pelayanan Kesehatan (fasyankes) swasta.")
                st.write("Yang dapat menerima vaksin ini adalah Karyawan/karyawati dan keluarga, Organisasi nirlaba internasional di Indonesia, Perwakilan negara asing di Indonesia")
                st.markdown("<p style='text-align: left; color: grey;font-size: 10px;'>"
                            "Sumber: https://primayahospital.com/vaksin-gotong-royong/</p>", unsafe_allow_html=True)

except Exception as e:
    st.write("Silahkan upload File Anda")
    st.write(e)
