# Pemetaan `oldcode/`

## 1. Tujuan Dokumen

Dokumen ini memetakan seluruh isi aktif, keluaran tersimpan, hubungan antarproses, dependensi, dan risiko yang ditemukan di dalam `oldcode/`. Folder `oldcode/` diperlakukan sebagai referensi baca-saja dan tidak diubah.

Pemetaan dilakukan dari sumber serta keluaran yang tersimpan di notebook. Notebook tidak dijalankan ulang karena lingkungan aktif belum memiliki dependensi machine learning yang diperlukan dan nama/path dataset yang dirujuk kode lama tidak sama dengan file yang saat ini tersedia.

## 2. Ringkasan Sistem Lama

Alur utama sistem lama adalah:

```text
Excel sumber
  -> filter status (hanya pada notebook optimasi)
  -> hapus Status dan Unit Lifetime
  -> konversi 8 sensor + target ke float
  -> split acak train/test 80:20
  -> optimasi hyperparameter dengan ABC atau PSO
  -> validasi silang 5-fold menggunakan MSE
  -> latih model final
  -> evaluasi MSE, RMSE, MAE, dan R²
  -> tampilkan kurva konvergensi dan actual vs predicted
  -> bangun/serialisasi model pada notebook terpisah
```

Walaupun tujuan proyek berfokus pada Random Forest, kode lama menguji dua model:

- `RandomForestRegressor`
- `SVR` dengan kernel RBF

Kedua model masing-masing dioptimasi menggunakan ABC dan PSO. `buildModel.ipynb` kemudian membangun pipeline SVR dan Random Forest dari sebagian hasil optimasi tersebut.

## 3. Inventaris File

| File | Ukuran sekitar | Sel | Fungsi utama |
|---|---:|---:|---|
| `oldcode/ABC_Medium.ipynb` | 216 KB | 12 (10 kode, 2 markdown) | Optimasi Random Forest dan SVR menggunakan ABC |
| `oldcode/pso_algorithm.ipynb` | 324 KB | 10 (9 kode, 1 markdown) | Optimasi Random Forest dan SVR menggunakan PSO |
| `oldcode/buildModel.ipynb` | 104 KB | 25 (22 kode, 3 markdown) | Melatih, menyimpan, memuat, memprediksi, dan memvisualisasikan model |

Versi Python pada metadata notebook berbeda-beda:

- ABC: Python 3.14.7
- PSO: Python 3.13.5
- pembangunan model: Python 3.9.12

Tidak ada file konfigurasi dependensi atau penguncian versi yang dirujuk oleh notebook.

## 4. Kontrak Data Lama

### 4.1 Dataset yang dirujuk notebook

| Notebook | Path literal |
|---|---|
| ABC | `Data_PT. Amanah_Critical_Break.xlsx` |
| PSO | `Data_PT. Amanah_Critical_Break.xlsx` |
| Pembangunan model | `Data_PT. Amanah_Critical_Break - Copy.xlsx` |

Path bersifat relatif terhadap direktori kerja saat notebook dijalankan. Kedua nama tersebut tidak tersedia dalam repositori saat pemetaan dilakukan.

File paling mirip yang tersedia adalah `datas/Data_PT.Amanah_Critical_Break.xlsx`, tetapi memiliki perbedaan direktori serta karakter spasi setelah `PT.`. Kesetaraan isi file belum boleh diasumsikan tanpa validasi.

### 4.2 Skema mentah yang terlihat dari keluaran notebook

| Kolom | Peran lama |
|---|---|
| `Exhaust Gas Temperature LF (Left Front)` | Fitur |
| `Exhaust Gas Temperature LR (Left Rear)` | Fitur |
| `Exhaust Gas Temperature RF (Right Front)` | Fitur |
| `Exhaust Gas Temperature RR (Right Rear)` | Fitur |
| `Blowby Pressure (Kpa)` | Fitur |
| `Boost Pressure (Kpa)` | Fitur |
| `Engine Oil Temp (°C)` | Fitur |
| `Coolant Temp (°C)` | Fitur |
| `Unit Lifetime (Hour)` | Dihapus saat training; dipakai sebagai sumbu grafik prediksi |
| `Status` | Filter pada notebook optimasi; dihapus sebelum training |
| `sisa jam` | Target/RUL |

### 4.3 Profil data dari keluaran tersimpan

- Dataset penuh pada `buildModel.ipynb`: 2.567 baris dan 11 kolom.
- Baris awal dataset penuh memiliki `Status = Normal` dan `sisa jam = 2550`.
- Setelah `Status == "Critical"` pada notebook ABC/PSO: 645 baris.
- Setelah membuang `Status` dan `Unit Lifetime (Hour)`: 8 fitur dan 1 target.
- Pada 645 baris yang ditampilkan oleh `df.info()`, seluruh 9 kolom tidak memiliki nilai null.
- Delapan fitur awalnya terbaca sebagai `object` pada notebook PSO lalu dipaksa menjadi `float`.

### 4.4 Korelasi target pada subset Critical

Korelasi Pearson fitur terhadap `sisa jam` yang tersimpan:

| Fitur | Korelasi |
|---|---:|
| `Boost Pressure (Kpa)` | -0,6731 |
| `Blowby Pressure (Kpa)` | -0,6121 |
| `Exhaust Gas Temperature RR (Right Rear)` | -0,4308 |
| `Engine Oil Temp (°C)` | -0,2404 |
| `Exhaust Gas Temperature LF (Left Front)` | -0,2267 |
| `Coolant Temp (°C)` | -0,1987 |
| `Exhaust Gas Temperature LR (Left Rear)` | -0,1408 |
| `Exhaust Gas Temperature RF (Right Front)` | -0,1108 |

Korelasi ini hanya menggambarkan hubungan linear dan tidak digunakan untuk seleksi fitur pada kode lama.

## 5. Pemetaan `ABC_Medium.ipynb`

### 5.1 Peta per sel

| Sel | Isi dan fungsi |
|---:|---|
| 0 | Contoh ABC sederhana untuk fungsi sphere; seluruh kode dikomentari dan tidak aktif. Probabilitas onlooker pada contoh ini memakai nilai objektif secara langsung. |
| 1 | Contoh ABC yang lebih lengkap: transformasi fitness, employed bee, onlooker bee, scout bee, batas pencarian, dan trial limit; seluruh kode dikomentari. |
| 2 | Membaca Excel, lalu memfilter hanya `Status == "Critical"`. |
| 3 | Sel kosong. |
| 4 | Menghapus `Status` dan `Unit Lifetime (Hour)`. |
| 5 | Memaksa 8 fitur dan `sisa jam` menjadi `float`. |
| 6 | Menampilkan informasi dataframe; keluaran menunjukkan 645 baris lengkap. |
| 7 | Menghitung matriks korelasi numerik, membulatkan dua desimal, dan menampilkannya. Ekspor `hasil_korelasi.xlsx` dinonaktifkan melalui komentar. |
| 8 | Judul bagian Random Forest. |
| 9 | Split data, definisi serta eksekusi ABC untuk Random Forest, evaluasi, kurva konvergensi, dan scatter actual vs predicted. |
| 10 | Judul bagian SVR/SVM. |
| 11 | Pengambilan dataset California yang tidak digunakan untuk model akhir, scaling fitur, ABC untuk SVR, evaluasi, dan dua grafik. |

### 5.2 Implementasi ABC aktif

Representasi solusi Random Forest terdiri dari lima dimensi:

| Hyperparameter | Batas | Perlakuan |
|---|---:|---|
| `n_estimators` | 50–300 | Diubah menjadi integer |
| `max_depth` | 2–30 | Diubah menjadi integer |
| `min_samples_split` | 2–20 | Diubah menjadi integer |
| `min_samples_leaf` | 1–20 | Diubah menjadi integer |
| `max_features` | 0,1–1,0 | Float |

Konfigurasi ABC Random Forest:

- Jumlah food source: 15.
- Trial limit: 5.
- Iterasi: 30.
- Tetangga mengubah satu dimensi dengan rumus `x_j + phi * (x_j - x_kj)`.
- `phi` diambil seragam dari -1 sampai 1.
- Nilai kandidat dijepit ke batas pencarian.
- Fungsi objektif: rata-rata MSE dari 5-fold CV pada data training.
- Fitness: `1 / (1 + MSE)` sehingga fitness lebih besar dianggap lebih baik.
- Random Forest memakai `random_state=42` dan `n_jobs=-1`.

Konfigurasi ABC SVR sama secara konseptual, dengan perbedaan:

- Hyperparameter: `C` 0,1–1000; `epsilon` 0,001–50; `gamma` 0,0001–1.
- Kernel selalu `rbf`.
- Iterasi: 40.
- Fitur distandardisasi sebelum optimasi.

### 5.3 Hasil ABC tersimpan

| Model | CV MSE | CV RMSE | Test MSE | Test RMSE | Test MAE | Test R² |
|---|---:|---:|---:|---:|---:|---:|
| Random Forest | 29.385,1294 | 171,4209 | 23.374,0540 | 152,8858 | 77,2325 | 0,955573 |
| SVR | 12.026,8773 | 109,6671 | 6.538,4420 | 80,8606 | 51,6212 | 0,987572 |

Hyperparameter terbaik Random Forest:

```text
n_estimators=215
max_depth=18
min_samples_split=2
min_samples_leaf=1
max_features=0.5685504664576413
```

Hyperparameter terbaik SVR:

```text
C=1000
epsilon=0.001
gamma=0.2608780517170326
kernel=rbf
```

Kurva Random Forest tidak membaik lagi setelah iterasi 10. Kurva SVR hanya mengalami perbaikan kecil setelah iterasi 21.

## 6. Pemetaan `pso_algorithm.ipynb`

### 6.1 Peta per sel

| Sel | Isi dan fungsi |
|---:|---|
| 0 | Contoh generik PSO untuk fungsi sphere; seluruh kode dikomentari. |
| 1 | Membaca Excel dan memfilter `Status == "Critical"`. |
| 2 | Menghapus `Status` dan `Unit Lifetime (Hour)`. |
| 3 | Menampilkan informasi dataframe sebelum konversi tipe. |
| 4 | Memaksa 8 fitur dan target menjadi `float`. |
| 5 | Menghitung serta menampilkan matriks korelasi. |
| 6 | Membandingkan KDE seluruh kolom sebelum dan setelah `StandardScaler`; hasil scaling hanya digunakan untuk visualisasi. |
| 7 | Split data, PSO untuk Random Forest, evaluasi, kurva konvergensi, dan scatter actual vs predicted. |
| 8 | Judul bagian SVM/SVR. |
| 9 | Scaling, PSO untuk SVR, evaluasi, kurva konvergensi, dan scatter actual vs predicted. |

### 6.2 Implementasi PSO aktif

Ruang pencarian Random Forest sama dengan ABC. Konfigurasi optimasinya:

- Partikel: 20.
- Iterasi: 30.
- Inertia weight `w=0.7`.
- Cognitive coefficient `c1=1.5`.
- Social coefficient `c2=1.5`.
- Kecepatan awal seluruh partikel adalah nol.
- Posisi dijepit ke batas pencarian setelah diperbarui.
- Personal best dan global best meminimalkan MSE 5-fold CV.
- Dua bilangan acak skalar dipakai untuk seluruh dimensi pada setiap pembaruan partikel.

PSO SVR memakai konfigurasi optimasi yang sama dengan tiga dimensi dan batas yang sama seperti ABC SVR.

### 6.3 Hasil PSO tersimpan

| Model | CV MSE | CV RMSE | Test MSE | Test RMSE | Test MAE | Test R² |
|---|---:|---:|---:|---:|---:|---:|
| Random Forest | 29.185,8962 | 170,8388 | 23.842,8419 | 154,4113 | 91,3093 | 0,954682 |
| SVR | 12.049,9722 | 109,7724 | 6.535,0272 | 80,8395 | 51,7628 | 0,987579 |

Hyperparameter terbaik Random Forest yang dicetak:

```text
n_estimators=300
max_depth=30
min_samples_split=2
min_samples_leaf=1
max_features=0.3  # hanya keluaran yang sudah dibulatkan dua desimal
```

Nilai presisi penuh `max_features` PSO Random Forest tidak disimpan pada keluaran teks.

Hyperparameter terbaik SVR:

```text
C=1000.0
epsilon=3.29771289485062
gamma=0.26377672129897395
kernel=rbf
```

Random Forest mencapai nilai terbaik tersimpan pada iterasi 3 dan tidak membaik sampai iterasi 30. SVR hanya mengalami perbaikan sangat kecil setelah iterasi 18.

## 7. Pemetaan `buildModel.ipynb`

### 7.1 Peta per sel

| Sel | Isi dan fungsi |
|---:|---|
| 0 | Mengimpor pandas, joblib, split, Pipeline, StandardScaler, SVR, dan Random Forest. |
| 1 | Membaca dataset `- Copy`; filter status tersedia tetapi dikomentari. |
| 2–5 | Menghapus dua kolom, mengonversi tipe, memilih 8 fitur/target, dan split acak 80:20. |
| 6–9 | Membuat pipeline StandardScaler + SVR dengan parameter ABC, melatihnya, lalu menyimpan `model_svr(new).pkl`. |
| 10–13 | Bagian berjudul `PSO RANDOM FORREST`, membuat dan melatih Random Forest, lalu melakukan serialisasi. Terdapat kesalahan objek yang diserialisasi. |
| 14–16 | Mengimpor kebutuhan grafik dan memuat `model_svr(new).pkl`. |
| 17–20 | Membaca ulang dataset penuh, memilih fitur, dan menambahkan kolom `Predicted RUL` dari model SVR. |
| 21–23 | Menyimpan lalu membaca ulang hasil prediksi dan mengonversi tipe untuk grafik. |
| 24 | Membuat step plot `Predicted RUL` terhadap `Unit Lifetime (Hour)` dan menyimpan PNG. |

### 7.2 Pipeline yang dimaksud

Pipeline SVR:

```text
StandardScaler
  -> SVR(kernel=rbf, C=1000, epsilon=0.001,
         gamma=0.2608780517170326)
```

Nilainya cocok persis dengan hasil ABC SVR.

Pipeline Random Forest:

```text
RandomForestRegressor(
  n_estimators=215,
  max_depth=18,
  min_samples_split=2,
  min_samples_leaf=1,
  max_features=0.5685504664576413
)
```

Nilainya cocok persis dengan hasil ABC Random Forest, bukan hasil PSO, walaupun judul notebook menyebut PSO.

### 7.3 Artefak yang dirujuk atau seharusnya dihasilkan

| Artefak | Maksud | Kondisi saat pemetaan |
|---|---|---|
| `model_svr(new).pkl` | Pipeline SVR | Tidak terdapat di repositori |
| `model_Rf(new).pkl` | Seharusnya pipeline Random Forest | Tidak terdapat di repositori; kode justru menyimpan pipeline SVR |
| `hasil_prediksi_rul_svr_kalimantan.xlsx` | Dataset dengan `Predicted RUL` | Tidak terdapat di repositori |
| `predicted_rul_vs_unit_lifetime.png` | Grafik RUL terhadap lifetime | Tidak terdapat di repositori |
| `hasil_korelasi.xlsx` | Matriks korelasi opsional | Ekspornya dikomentari dan file tidak tersedia |

## 8. Hubungan Antar-Notebook

| Tahap | ABC | PSO | Build Model |
|---|---|---|---|
| Dataset optimasi | Hanya Critical | Hanya Critical | Seluruh status |
| Split | Acak 80:20, seed 42 | Acak 80:20, seed 42 | Acak 80:20, seed 42 |
| Random Forest | Optimasi 5 parameter | Optimasi 5 parameter | Menggunakan parameter ABC |
| SVR | Optimasi 3 parameter | Optimasi 3 parameter | Menggunakan parameter ABC |
| Evaluasi | CV + test | CV + test | Tidak mengevaluasi model yang dibangun |
| Serialisasi | Tidak ada | Tidak ada | Ada, tetapi serialisasi RF salah objek |
| Prediksi akhir | Test subset | Test subset | Dataset penuh menggunakan SVR |

Tidak ada koneksi programatik antar-notebook. Parameter terbaik dipindahkan secara manual ke `buildModel.ipynb`, sehingga asal metode mudah salah label dan hasil sulit dilacak.

## 9. Dependensi

Dependensi yang benar-benar digunakan:

- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scikit-learn`
- `joblib`
- Engine Excel seperti `openpyxl`

Impor atau operasi yang tidak diperlukan:

- `fetch_california_housing` diimpor pada bagian Random Forest ABC tetapi tidak digunakan.
- Pada bagian SVR ABC, `fetch_california_housing()` benar-benar dipanggil tetapi hasilnya tidak digunakan; ini dapat memicu unduhan jaringan yang tidak relevan.
- `MinMaxScaler` diimpor pada PSO Random Forest tetapi tidak digunakan.
- `pandas` diimpor berulang kali di dalam notebook.

Lingkungan aktif saat pemetaan memakai Python 3.14.7 dan belum memiliki seluruh dependensi di atas.

## 10. Temuan dan Risiko

### 10.1 Kesalahan fungsional

1. Pada `buildModel.ipynb` sel 13, kode menjalankan `joblib.dump(svr_pipeline, "model_Rf(new).pkl")`. File bernama Random Forest tersebut sebenarnya akan berisi model SVR.
2. Judul `PSO RANDOM FORREST` pada pembangunan model tidak sesuai dengan parameter yang digunakan; parameter berasal dari ABC.
3. Pesan setelah serialisasi tidak sama dengan nama file sebenarnya, misalnya menyebut `model_svr.pkl` padahal file yang ditulis `model_svr(new).pkl`.
4. Pesan hasil prediksi menyebut `hasil_prediksi_rul.xlsx`, sedangkan file yang ditulis adalah `hasil_prediksi_rul_svr_kalimantan.xlsx`.
5. Nama dataset yang dirujuk tidak cocok dengan struktur dan nama file dataset saat ini.

### 10.2 Validitas evaluasi forecasting

1. Data dibagi secara acak. Untuk data berurutan berdasarkan usia unit, hal ini dapat membuat observasi yang berdekatan muncul di train dan test sehingga skor terlalu optimistis.
2. Validasi silang memakai K-fold biasa, bukan validasi berbasis waktu atau unit.
3. Tidak ada pengurutan eksplisit berdasarkan `Unit Lifetime (Hour)` sebelum evaluasi.
4. `Unit Lifetime (Hour)` dihapus dari fitur, tetapi digunakan kembali sebagai sumbu waktu tanpa pemeriksaan urutan, duplikasi, atau unit kendaraan.
5. Tidak ada validasi eksternal antarkendaraan atau antarlokasi.
6. Kode lebih tepat menggambarkan regresi RUL dari snapshot sensor daripada forecasting deret waktu karena tidak membentuk lag, window, tren, atau fitur temporal.

### 10.3 Ketidakkonsistenan populasi data

1. Optimasi ABC/PSO dilakukan hanya pada 645 baris Critical.
2. `buildModel.ipynb` menonaktifkan filter status dan melatih model pada seluruh 2.567 baris.
3. Hyperparameter hasil subset Critical dengan demikian diterapkan pada distribusi training yang berbeda.
4. Prediksi akhir juga dilakukan pada dataset penuh, termasuk baris Normal.

### 10.4 Kebocoran dan scaling

1. ABC SVR menjalankan `StandardScaler.fit_transform(X_train)` sebelum 5-fold CV. Statistik scaler dari seluruh train sudah terlihat oleh tiap validation fold.
2. PSO SVR juga melakukan scaling seluruh `X_train` sebelum CV, lalu memasukkan `StandardScaler` lagi di dalam pipeline CV. Terjadi scaling ganda serta kebocoran statistik scaling pertama.
3. Model final PSO SVR bukan pipeline; ia menerima matriks yang sudah diskalakan. Scaler dan model tidak disimpan bersama sehingga inferensi baru rawan salah transformasi.

### 10.5 Reproduksibilitas

1. `train_test_split` dan Random Forest memakai seed 42 pada notebook optimasi.
2. Modul `random` untuk ABC dan generator NumPy untuk PSO tidak diberi seed, sehingga hasil optimasi tidak deterministik.
3. Random Forest pada `buildModel.ipynb` tidak memiliki `random_state`.
4. Versi Python berbeda dan versi library tidak dicatat.
5. Notebook memiliki execution count yang tidak berurutan atau null; state yang menghasilkan sebagian output tidak sepenuhnya dapat ditelusuri.

### 10.6 Efisiensi optimasi

1. ABC mengevaluasi kembali seluruh populasi saat menyimpan best pada setiap iterasi, walaupun sebagian nilai objektif sudah dihitung.
2. Tanpa menghitung scout tambahan, ABC Random Forest melakukan sedikitnya 1.365 evaluasi objektif atau 6.825 pelatihan model pada 5-fold CV.
3. Tanpa menghitung scout tambahan, ABC SVR melakukan sedikitnya 1.815 evaluasi objektif atau 9.075 pelatihan model.
4. Masing-masing PSO melakukan 620 evaluasi objektif atau 3.100 pelatihan model.
5. Hyperparameter integer dicari dalam ruang kontinu lalu dipotong dengan `int`, sehingga banyak solusi berbeda dapat mendekode ke konfigurasi yang sama tanpa cache.
6. Tidak ada early stopping walaupun beberapa kurva telah stagnan sejak awal.

### 10.7 Kualitas pipeline dan data

1. Tidak ada pemeriksaan skema, nilai hilang, nilai tak terhingga, duplikasi, outlier, atau kegagalan konversi sebelum training.
2. Konversi menggunakan `astype(float)` akan langsung gagal jika ada string nonnumerik.
3. Tidak ada baseline tanpa optimasi untuk mengukur manfaat ABC atau PSO.
4. Tidak ada interval ketidakpastian, distribusi error, evaluasi per status/unit, atau analisis residual.
5. Tidak ada penyimpanan metadata model seperti fitur, urutan kolom, metrik, seed, versi library, sumber data, dan metode optimasi.
6. Tidak ada pengujian otomatis atau validasi bahwa model yang dimuat memiliki tipe serta fitur yang benar.

## 11. Kesimpulan Perbandingan Hasil Lama

- Pada hasil tersimpan, SVR jauh mengungguli Random Forest untuk split acak yang digunakan.
- Untuk Random Forest, ABC menghasilkan test RMSE dan MAE lebih baik daripada PSO, walaupun PSO memiliki CV MSE sedikit lebih rendah.
- Untuk SVR, PSO memiliki test RMSE dan R² sedikit lebih baik, sedangkan ABC memiliki CV MSE dan test MAE sedikit lebih baik. Perbedaannya sangat kecil dan belum dapat dianggap bermakna tanpa pengulangan beberapa seed.
- Skor tinggi belum membuktikan kemampuan forecasting ke masa depan karena evaluasi menggunakan split acak pada data yang tampaknya berurutan.
- Hasil lama layak dijadikan referensi implementasi ABC/PSO, tetapi evaluasi dan pipeline produksinya tidak boleh disalin tanpa perbaikan.

## 12. Kontrak yang Disarankan untuk `newcode/`

Bagian ini bukan implementasi, melainkan batas rancangan yang diturunkan dari pemetaan:

1. Gunakan satu loader dengan path dataset eksplisit dari `datas/` dan validasi skema.
2. Tetapkan secara eksplisit populasi data yang digunakan: seluruh status atau hanya Critical.
3. Pisahkan preprocessing, pembentukan split, training, optimasi, evaluasi, dan inferensi.
4. Gunakan split berbasis waktu dan/atau unit untuk skenario utama; pertahankan split acak hanya sebagai skenario pembanding terhadap oldcode.
5. Letakkan scaler SVR di dalam pipeline dan lakukan fit hanya di dalam fold training.
6. Gunakan seed terpadu untuk Python, NumPy, split, model, ABC, dan PSO.
7. Simpan hasil setiap percobaan secara terstruktur: konfigurasi, seed, parameter terbaik, kurva konvergensi, metrik CV/test, waktu proses, serta identitas data.
8. Simpan pipeline final beserta schema/feature order dan verifikasi tipe model sebelum digunakan.
9. Buat baseline Random Forest tanpa optimasi agar kontribusi ABC dan PSO dapat diukur.
10. Tempatkan variasi eksperimen secara terpisah di `newcode/scenarios/`.

## 13. Skenario Minimum yang Diturunkan dari Oldcode

| Skenario | Model | Optimasi | Split | Tujuan |
|---|---|---|---|---|
| Baseline lama | Random Forest | Tanpa optimasi | Acak 80:20 | Titik pembanding sederhana |
| Replikasi ABC | Random Forest | ABC | Acak 80:20 | Membandingkan hasil baru dengan notebook lama |
| Replikasi PSO | Random Forest | PSO | Acak 80:20 | Membandingkan hasil baru dengan notebook lama |
| Validasi temporal ABC | Random Forest | ABC | Berbasis waktu | Menguji kemampuan forecasting yang lebih realistis |
| Validasi temporal PSO | Random Forest | PSO | Berbasis waktu | Membandingkan optimizer secara realistis |
| Validasi antarunit | Random Forest | ABC/PSO | Holdout unit | Menguji generalisasi ke kendaraan lain |

SVR dapat dipertahankan sebagai model pembanding karena merupakan bagian nyata dari oldcode, tetapi bukan model utama sesuai arah proyek saat ini.
