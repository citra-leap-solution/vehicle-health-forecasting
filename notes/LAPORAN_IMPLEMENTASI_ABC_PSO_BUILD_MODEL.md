# Laporan Implementasi Optimasi Random Forest Menggunakan ABC dan PSO

## Informasi Dokumen

| Item | Keterangan |
|---|---|
| Proyek | Vehicle Health – Forecasting Remaining Useful Life |
| Model utama | Random Forest Regression |
| Metode optimasi | Artificial Bee Colony dan Particle Swarm Optimization |
| Dataset awal | Data PT Amanah Critical Break |
| Tanggal laporan | 14 September 2026 |
| Implementasi | `newcode/ABC_RF.ipynb`, `newcode/PSO_RF.ipynb`, dan `newcode/Build_RF.ipynb` |
| Referensi | Notebook pada folder `oldcode/` |

## 1. Ringkasan Eksekutif

Proyek ini bertujuan membangun model machine learning untuk memperkirakan Remaining Useful Life (RUL) kendaraan berdasarkan delapan parameter sensor. Model yang digunakan adalah `RandomForestRegressor`, sedangkan pemilihan hyperparameter dilakukan menggunakan dua metode metaheuristik, yaitu Artificial Bee Colony (ABC) dan Particle Swarm Optimization (PSO).

Implementasi pada `newcode/` dikembangkan dengan tetap mengacu pada proses dalam `oldcode/`, tetapi beberapa bagian diperbarui agar lebih konsisten, generik, dapat direproduksi, dan lebih mudah digunakan kembali. Pembaruan mencakup validasi schema, pembentukan target otomatis, random split dengan seed tetap, K-fold acak, cache evaluasi, early stopping, penyimpanan artefak terstruktur, serta validasi model setelah serialisasi.

Hasil utama menunjukkan:

- ABC memperoleh CV MSE sebesar 41.447,12 dan test R² sebesar 0,9128.
- PSO memperoleh CV MSE sebesar 40.289,39 dan test R² sebesar 0,9119.
- PSO mempunyai CV MSE sekitar 2,79% lebih rendah daripada ABC.
- Waktu optimasi PSO sekitar 30,23% lebih singkat daripada ABC.
- ABC sedikit lebih baik pada test RMSE dan R².
- PSO sedikit lebih baik pada test MAE.
- PSO dipilih sebagai sumber model utama karena pemilihan ditetapkan berdasarkan CV MSE terkecil, bukan berdasarkan data test.

Notebook build tetap menghasilkan dan menyimpan kedua model. Dengan demikian, hasil ABC tidak dibuang dan masih dapat digunakan untuk analisis atau pembandingan lanjutan.

## 2. Tujuan Implementasi

Tujuan implementasi newcode adalah:

1. Menghasilkan pipeline optimasi Random Forest menggunakan ABC.
2. Menghasilkan pipeline optimasi Random Forest menggunakan PSO.
3. Membuat proses pengolahan data yang sama untuk kedua optimizer.
4. Membandingkan kedua metode menggunakan data dan metode evaluasi yang konsisten.
5. Melatih ulang model final menggunakan seluruh data yang sesuai dengan kontrak optimasi.
6. Menyimpan model beserta metadata yang dibutuhkan saat digunakan kembali.
7. Memperbaiki ketidakkonsistenan dan kesalahan fungsional pada build model lama.
8. Menyediakan notebook yang generik agar dapat digunakan pada dataset kendaraan lain.

## 3. Struktur Implementasi

### 3.1 Notebook utama

| Notebook | Fungsi |
|---|---|
| `newcode/ABC_RF.ipynb` | Optimasi hyperparameter Random Forest menggunakan ABC |
| `newcode/PSO_RF.ipynb` | Optimasi hyperparameter Random Forest menggunakan PSO |
| `newcode/Build_RF.ipynb` | Melatih ulang, membandingkan, memilih, menyimpan, dan memverifikasi model final |

### 3.2 Catatan pendukung

| Dokumen | Fungsi |
|---|---|
| `notes/MAPPING_OLDCODE.md` | Pemetaan seluruh proses lama |
| `notes/README_ABC.md` | Petunjuk penggunaan notebook ABC |
| `notes/README_PSO.md` | Petunjuk penggunaan notebook PSO |
| `notes/README_BUILD_MODEL.md` | Petunjuk penggunaan notebook build model |
| `notes/LAPORAN_IMPLEMENTASI_ABC_PSO_BUILD_MODEL.md` | Laporan implementasi lengkap |

### 3.3 Alur umum

```text
Dataset kendaraan
        │
        ▼
Validasi schema dan pembersihan data
        │
        ▼
Pembentukan target Remaining Useful Life
        │
        ▼
Filter data berstatus Critical
        │
        ▼
Random holdout 80:20 dengan seed 42
        │
        ├───────────────┐
        ▼               ▼
 Optimasi ABC       Optimasi PSO
        │               │
        ▼               ▼
Parameter terbaik  Parameter terbaik
        │               │
        └───────┬───────┘
                ▼
       Perbandingan CV MSE
                │
                ▼
 Training ulang pada seluruh data Critical
                │
                ▼
 Penyimpanan dan verifikasi model final
```

## 4. Dataset dan Pembentukan Target

### 4.1 Profil dataset

Dataset yang digunakan pada konfigurasi awal adalah:

```text
datas/Data_PT.Amanah_Critical_Break.xlsx
```

Hasil pemeriksaan data:

| Informasi | Nilai |
|---|---:|
| Baris mentah yang dibaca | 2.569 |
| Baris tidak valid/header duplikat | 1 |
| Baris valid seluruh status | 2.568 |
| Status Normal | 1.847 |
| Status Critical | 720 |
| Status Break | 1 |
| Baris yang digunakan optimizer | 720 Critical |
| Lifetime minimum data Critical | 76.113 jam |
| Lifetime maksimum data Critical | 78.636 jam |
| Failure hour | 78.637 jam |
| RUL minimum data Critical | 1 jam |
| RUL maksimum data Critical | 2.524 jam |

### 4.2 Fitur

Delapan fitur sensor yang digunakan:

1. Exhaust Gas Temperature LF (Left Front).
2. Exhaust Gas Temperature LR (Left Rear).
3. Exhaust Gas Temperature RF (Right Front).
4. Exhaust Gas Temperature RR (Right Rear).
5. Blowby Pressure (Kpa).
6. Boost Pressure (Kpa).
7. Engine Oil Temp (°C).
8. Coolant Temp (°C).

`Unit Lifetime (Hour)` digunakan untuk membentuk target dan menyusun visualisasi, tetapi tidak digunakan sebagai fitur Random Forest. `Status` digunakan sebagai filter data, tetapi juga tidak menjadi fitur model.

### 4.3 Pembentukan target

Dataset aktual tidak memiliki kolom `sisa jam`. Target RUL dibentuk berdasarkan lifetime saat kendaraan berstatus Break:

```text
RUL = min(max_rul, max(0, failure_hour - unit_lifetime))
```

Konfigurasi PT Amanah menggunakan:

```text
failure_hour = 78637
max_rul = 2550
```

Contoh:

```text
Unit Lifetime = 76473
RUL = 78637 - 76473
RUL = 2164 jam
```

Rumus tersebut konsisten dengan nilai `sisa jam` yang tersimpan pada keluaran oldcode.

### 4.4 Pembersihan dan validasi

Newcode melakukan validasi berikut:

- Menerima file Excel atau CSV.
- Memastikan seluruh fitur, lifetime, dan status tersedia.
- Menormalisasi kapitalisasi nama status.
- Menoleransi nama kolom temperatur dengan atau tanpa akhiran `(°C)`.
- Mengubah nilai fitur dan lifetime menjadi numerik menggunakan coercion.
- Menghapus baris yang tidak mempunyai nilai numerik lengkap.
- Menghapus header duplikat yang terbaca sebagai baris data.
- Memastikan target atau failure hour dapat ditentukan.
- Memastikan masih ada data setelah filter status.

### 4.5 Pembagian data

Data dibagi secara acak karena observasi dataset dinyatakan diperoleh secara acak. Pembagian yang digunakan:

```text
Training = 80%
Test = 20%
shuffle = True
random_state = 42
```

Dari 720 data Critical diperoleh:

| Bagian | Jumlah baris |
|---|---:|
| Training | 576 |
| Test | 144 |

Random split menghasilkan rentang target yang saling tumpang tindih:

| Bagian | Rentang RUL |
|---|---:|
| Training | 1–2.524 jam |
| Test | 4–2.520 jam |

Seed 42 digunakan agar pembagian data ABC dan PSO sama serta dapat diulang.

## 5. Random Forest Regression

Random Forest merupakan ensemble beberapa decision tree. Setiap tree dilatih menggunakan variasi sampel dan fitur, kemudian prediksi akhir regresi dihitung dari rata-rata prediksi seluruh tree.

Hyperparameter yang dioptimasi:

| Hyperparameter | Fungsi | Batas pencarian |
|---|---|---:|
| `n_estimators` | Jumlah decision tree | 50–300 |
| `max_depth` | Kedalaman maksimum tree | 2–30 |
| `min_samples_split` | Sampel minimum untuk membagi node | 2–20 |
| `min_samples_leaf` | Sampel minimum pada leaf | 1–20 |
| `max_features` | Proporsi fitur saat split | 0,1–1,0 |

Empat parameter pertama didekode sebagai integer, sedangkan `max_features` dipertahankan sebagai float.

## 6. Fungsi Objektif dan Evaluasi

### 6.1 Cross-validation

Fungsi objektif ABC dan PSO menggunakan K-fold acak:

```text
n_splits = 5
shuffle = True
random_state = 42
scoring = negative mean squared error
```

Setiap kandidat hyperparameter dinilai dengan membangun Random Forest pada lima fold. Nilai negatif dari scikit-learn dibalik kembali menjadi MSE positif dan kemudian diminimalkan oleh optimizer.

### 6.2 Metrik

Mean Squared Error:

```text
MSE = (1/n) × Σ(actual - predicted)²
```

Root Mean Squared Error:

```text
RMSE = √MSE
```

Mean Absolute Error:

```text
MAE = (1/n) × Σ|actual - predicted|
```

Coefficient of Determination:

```text
R² = 1 - (jumlah kuadrat residual / jumlah kuadrat total)
```

Interpretasi umum:

- MSE, RMSE, dan MAE yang lebih kecil menunjukkan error lebih rendah.
- R² yang semakin mendekati 1 menunjukkan semakin banyak variasi target yang dapat dijelaskan model.
- CV MSE menjadi dasar pemilihan optimizer karena berasal dari beberapa fold training.
- Data test hanya digunakan untuk evaluasi akhir, bukan untuk memilih model utama.

## 7. Implementasi Artificial Bee Colony

### 7.1 Konsep ABC

ABC meniru cara koloni lebah mencari sumber makanan. Pada optimasi model, satu sumber makanan merepresentasikan satu kombinasi hyperparameter. Kualitas sumber makanan ditentukan oleh MSE hasil cross-validation.

Tiga fase utama ABC:

1. Employed bee mengeksplorasi tetangga dari sumber makanan saat ini.
2. Onlooker bee memilih sumber makanan berdasarkan kualitas fitness.
3. Scout bee mengganti sumber makanan yang tidak membaik setelah melewati batas trial.

### 7.2 Representasi solusi

```text
solution = [
    n_estimators,
    max_depth,
    min_samples_split,
    min_samples_leaf,
    max_features
]
```

### 7.3 Pembentukan tetangga

Satu dimensi dipilih secara acak, kemudian nilainya diperbarui:

```text
neighbor[j] = solution[j] + phi × (solution[j] - other[j])
```

Dengan:

- `j` adalah dimensi yang dipilih.
- `other` adalah solusi lain dalam populasi.
- `phi` adalah angka acak antara -1 dan 1.
- Nilai akhir dijepit agar tetap berada di dalam batas pencarian.

### 7.4 Fitness

ABC mengubah MSE menjadi fitness:

```text
fitness = 1 / (1 + MSE)
```

MSE lebih kecil menghasilkan fitness lebih besar.

### 7.5 Konfigurasi ABC

| Parameter | Nilai | Fungsi |
|---|---:|---|
| `food_number` | 15 | Jumlah sumber makanan |
| `limit` | 5 | Batas kegagalan sebelum menjadi scout |
| `max_iter` | 30 | Batas maksimum iterasi |
| `patience` | 8 | Batas stagnasi global untuk early stopping |
| `seed` | 42 | Menjamin reproduksibilitas |

### 7.6 Pseudocode ABC

```text
Inisialisasi populasi secara acak
Evaluasi MSE setiap solusi
Simpan solusi global terbaik

Untuk setiap iterasi:
    Untuk setiap employed bee:
        Bentuk neighbor
        Evaluasi MSE neighbor
        Pertahankan solusi yang lebih baik
        Perbarui trial

    Hitung probabilitas dari fitness

    Untuk setiap onlooker bee:
        Pilih sumber makanan berdasarkan probabilitas
        Bentuk dan evaluasi neighbor
        Pertahankan solusi yang lebih baik

    Untuk setiap sumber dengan trial >= limit:
        Buat solusi scout baru secara acak

    Perbarui solusi global terbaik
    Simpan kurva konvergensi

    Jika tidak ada perbaikan selama patience:
        Hentikan optimasi
```

### 7.7 Pembaruan ABC pada newcode

- Generator random memakai seed tetap.
- Nilai objektif disimpan di dalam cache.
- Kandidat dengan parameter yang sama tidak dilatih ulang.
- Solusi terbaik diinisialisasi sebelum iterasi pertama.
- Early stopping diterapkan berdasarkan stagnasi global.
- Batas parameter divalidasi.
- Seluruh keluaran dicatat dalam JSON dan CSV.
- Model hasil optimasi disimpan bersama fitur dan metadata target.

### 7.8 Hasil ABC

Hyperparameter terbaik:

| Hyperparameter | Nilai |
|---|---:|
| `n_estimators` | 251 |
| `max_depth` | 18 |
| `min_samples_split` | 2 |
| `min_samples_leaf` | 1 |
| `max_features` | 0,659708 |

Metrik:

| Metrik | Nilai |
|---|---:|
| CV MSE | 41.447,1186 |
| CV RMSE | 203,5857 |
| Test MSE | 55.487,7615 |
| Test RMSE | 235,5584 |
| Test MAE | 123,1763 |
| Test R² | 0,912811 |
| Evaluasi objektif unik | 565 |
| Iterasi aktual | 21 |
| Waktu proses | 205,03 detik |

Feature importance:

| Fitur | Importance |
|---|---:|
| Blowby Pressure | 29,79% |
| Boost Pressure | 26,04% |
| Coolant Temperature | 10,92% |
| Exhaust Gas Temperature LR | 8,33% |
| Exhaust Gas Temperature LF | 6,71% |
| Engine Oil Temperature | 6,66% |
| Exhaust Gas Temperature RR | 6,53% |
| Exhaust Gas Temperature RF | 5,01% |

Blowby Pressure dan Boost Pressure menyumbang sekitar 55,83% total importance model ABC.

### 7.9 Grafik ABC

![Kurva konvergensi ABC](../newcode/artifacts/abc_pt_amanah_random/convergence.png)

![Actual vs Predicted ABC](../newcode/artifacts/abc_pt_amanah_random/actual_vs_predicted.png)

## 8. Implementasi Particle Swarm Optimization

### 8.1 Konsep PSO

PSO meniru pergerakan kelompok partikel. Setiap partikel merepresentasikan kombinasi hyperparameter dan bergerak di dalam ruang pencarian berdasarkan pengalaman terbaiknya sendiri serta pengalaman terbaik seluruh swarm.

Komponen utama:

- Position: kombinasi hyperparameter saat ini.
- Velocity: arah dan besar perpindahan partikel.
- Personal best (`pbest`): posisi terbaik yang pernah dicapai partikel.
- Global best (`gbest`): posisi terbaik yang pernah dicapai seluruh swarm.

### 8.2 Pembaruan velocity dan position

```text
velocity =
    w × velocity
    + c1 × r1 × (pbest - position)
    + c2 × r2 × (gbest - position)

position = position + velocity
```

Keterangan:

- `w` mempertahankan momentum partikel.
- `c1` mengatur tarikan menuju pengalaman terbaik partikel.
- `c2` mengatur tarikan menuju solusi terbaik swarm.
- `r1` dan `r2` adalah angka acak antara 0 dan 1.

Newcode membentuk `r1` dan `r2` secara independen untuk setiap partikel dan dimensi. Hal ini memberikan variasi pergerakan yang lebih baik daripada satu nilai acak skalar untuk seluruh dimensi.

### 8.3 Konfigurasi PSO

| Parameter | Nilai | Fungsi |
|---|---:|---|
| `n_particles` | 20 | Jumlah partikel |
| `max_iter` | 30 | Batas maksimum iterasi |
| `w` | 0,7 | Inertia weight |
| `c1` | 1,5 | Cognitive coefficient |
| `c2` | 1,5 | Social coefficient |
| `patience` | 8 | Batas stagnasi untuk early stopping |
| `seed` | 42 | Menjamin reproduksibilitas |

### 8.4 Pseudocode PSO

```text
Inisialisasi position partikel secara acak
Inisialisasi velocity dengan nol
Evaluasi MSE seluruh partikel
Simpan pbest setiap partikel
Simpan gbest seluruh swarm

Untuk setiap iterasi:
    Buat r1 dan r2 untuk setiap partikel dan dimensi

    Perbarui velocity menggunakan:
        inertia + cognitive + social

    Perbarui position
    Jepit position ke batas pencarian
    Evaluasi MSE setiap position

    Jika position lebih baik:
        Perbarui pbest

    Jika pbest terbaik lebih baik dari gbest:
        Perbarui gbest

    Simpan kurva konvergensi

    Jika gbest tidak membaik selama patience:
        Hentikan optimasi
```

### 8.5 Perbedaan PSO dari ABC

PSO tidak memakai:

- Employed bee.
- Onlooker bee.
- Scout bee.
- Trial limit.
- Fitness probability.
- Pembentukan neighbor milik ABC.

PSO langsung membandingkan MSE. Random tetap diperlukan untuk inisialisasi position serta nilai `r1` dan `r2`. Seed membuat proses tersebut dapat diulang, tetapi tidak menghilangkan sifat stochastic PSO.

### 8.6 Pembaruan PSO pada newcode

- Position dan velocity disimpan terpisah.
- Personal best dan global best diperbarui secara eksplisit.
- `r1` dan `r2` berbentuk matrix per partikel dan dimensi.
- Boundary clipping dilakukan setelah perubahan position.
- Generator random menggunakan seed tetap.
- Evaluasi kandidat menggunakan cache.
- Early stopping diterapkan pada stagnasi global best.
- Artefak model dan metrik disimpan secara terstruktur.

### 8.7 Hasil PSO

Hyperparameter terbaik:

| Hyperparameter | Nilai |
|---|---:|
| `n_estimators` | 124 |
| `max_depth` | 20 |
| `min_samples_split` | 2 |
| `min_samples_leaf` | 1 |
| `max_features` | 0,709165 |

Metrik:

| Metrik | Nilai |
|---|---:|
| CV MSE | 40.289,3943 |
| CV RMSE | 200,7222 |
| Test MSE | 56.098,4115 |
| Test RMSE | 236,8510 |
| Test MAE | 122,5144 |
| Test R² | 0,911852 |
| Evaluasi objektif unik | 379 |
| Iterasi aktual | 18 |
| Waktu proses | 143,05 detik |

Feature importance:

| Fitur | Importance |
|---|---:|
| Blowby Pressure | 30,87% |
| Boost Pressure | 25,44% |
| Coolant Temperature | 10,69% |
| Exhaust Gas Temperature LR | 8,28% |
| Exhaust Gas Temperature LF | 6,83% |
| Exhaust Gas Temperature RR | 6,54% |
| Engine Oil Temperature | 6,30% |
| Exhaust Gas Temperature RF | 5,05% |

Blowby Pressure dan Boost Pressure menyumbang sekitar 56,31% total importance model PSO.

### 8.8 Grafik PSO

![Kurva konvergensi PSO](../newcode/artifacts/pso_pt_amanah_random/convergence.png)

![Actual vs Predicted PSO](../newcode/artifacts/pso_pt_amanah_random/actual_vs_predicted.png)

## 9. Perbandingan ABC dan PSO

### 9.1 Perbandingan metrik

| Aspek | ABC | PSO | Hasil lebih baik |
|---|---:|---:|---|
| CV MSE | 41.447,12 | 40.289,39 | PSO |
| CV RMSE | 203,59 | 200,72 | PSO |
| Test MSE | 55.487,76 | 56.098,41 | ABC |
| Test RMSE | 235,56 | 236,85 | ABC |
| Test MAE | 123,18 | 122,51 | PSO |
| Test R² | 0,912811 | 0,911852 | ABC |
| Evaluasi objektif unik | 565 | 379 | PSO |
| Iterasi aktual | 21 | 18 | PSO |
| Waktu | 205,03 detik | 143,05 detik | PSO |

### 9.2 Selisih relatif

- CV MSE PSO sekitar 2,79% lebih rendah daripada ABC.
- CV RMSE PSO sekitar 1,41% lebih rendah daripada ABC.
- PSO memakai sekitar 32,92% lebih sedikit evaluasi objektif unik.
- PSO selesai sekitar 30,23% lebih cepat.
- Test RMSE ABC sekitar 0,55% lebih rendah daripada PSO.
- Test MAE PSO sekitar 0,54% lebih rendah daripada ABC.
- Test R² ABC lebih tinggi sekitar 0,00096 atau 0,096 poin persentase.

### 9.3 Interpretasi

Performa test ABC dan PSO sangat berdekatan. Tidak ada optimizer yang mengungguli seluruh metrik sekaligus. ABC sedikit unggul pada error kuadrat dan R² test, sedangkan PSO unggul pada CV, MAE, efisiensi evaluasi, dan waktu proses.

PSO dipilih sebagai sumber `random_forest_best.joblib` karena:

1. Kriteria seleksi ditetapkan sebelum build sebagai CV MSE terkecil.
2. CV menggunakan lima fold sehingga penilaian tidak bergantung pada satu test subset.
3. Data test tetap dipertahankan sebagai evaluasi dan tidak digunakan untuk memilih model.
4. PSO mencapai hasil CV lebih baik dengan waktu dan evaluasi lebih sedikit.

Pemilihan PSO tidak berarti model ABC buruk. Kedua model tetap disimpan karena perbedaan test sangat kecil dan dapat dibandingkan kembali pada dataset eksternal.

## 10. Build Model Final

### 10.1 Tujuan build

Notebook optimasi melatih model pada 576 data training dan mengevaluasi pada 144 data test. Setelah hyperparameter dipilih, model final dibangun ulang menggunakan seluruh 720 data Critical agar seluruh informasi yang relevan dapat digunakan.

### 10.2 Alur build

```text
Baca metrics.json ABC dan PSO
        │
        ▼
Validasi kelengkapan hyperparameter
        │
        ▼
Validasi kontrak data, fitur, target, split, dan seed
        │
        ▼
Pilih optimizer berdasarkan CV MSE
        │
        ▼
Muat dan bersihkan dataset
        │
        ▼
Latih ulang model ABC pada 720 data Critical
        │
        ▼
Latih ulang model PSO pada 720 data Critical
        │
        ▼
Simpan kedua bundle dan alias model terbaik
        │
        ▼
Muat ulang dan verifikasi prediksi
```

### 10.3 Validasi kontrak

Build dihentikan apabila hasil ABC dan PSO berbeda dalam:

- Dataset.
- Urutan fitur.
- Aturan target.
- Metode split.
- Seed.

Validasi tersebut mencegah perbandingan dua optimizer yang sebenarnya menggunakan eksperimen berbeda.

### 10.4 Training final

Dua model dibangun:

- Model ABC menggunakan 251 tree dan parameter hasil ABC.
- Model PSO menggunakan 124 tree dan parameter hasil PSO.

Metrik pada data training final:

| Model | Training MSE | Training RMSE | Training MAE | Training R² |
|---|---:|---:|---:|---:|
| ABC | 4.200,9870 | 64,8150 | 34,5990 | 0,993532 |
| PSO | 4.441,5292 | 66,6448 | 35,0280 | 0,993162 |

Metrik ini hanya bersifat diagnostik karena dihitung pada data yang digunakan untuk melatih model. Nilainya tidak boleh dianggap sebagai kemampuan generalisasi. Kemampuan generalisasi tetap mengacu pada metrik test dari notebook ABC dan PSO.

### 10.5 Bundle model

Setiap bundle `joblib` berisi:

- Objek `RandomForestRegressor`.
- Nama optimizer asal.
- Urutan fitur.
- Hyperparameter.
- Aturan pembentukan target.
- Metadata data.
- Seed.

Build memuat ulang seluruh file model dan memastikan:

- Label optimizer di dalam bundle sesuai nama file.
- Prediksi sebelum dan sesudah serialisasi identik.
- Alias model terbaik menunjuk optimizer yang benar.

### 10.6 Artefak build

Direktori:

```text
newcode/models/pt_amanah_critical/
```

File:

| File | Isi |
|---|---|
| `random_forest_abc.joblib` | Model final berdasarkan ABC |
| `random_forest_pso.joblib` | Model final berdasarkan PSO |
| `random_forest_best.joblib` | Alias model PSO sebagai pemenang CV |
| `build_summary.json` | Ringkasan pemilihan, metrik, versi, dan metadata |
| `training_predictions.csv` | Prediksi diagnostik seluruh data training |
| `model_comparison.png` | Grafik perbandingan kedua model |

### 10.7 Grafik build model

![Perbandingan model final](../newcode/models/pt_amanah_critical/model_comparison.png)

## 11. Perbandingan Oldcode dan Newcode

### 11.1 Ringkasan perubahan

| Aspek | Oldcode | Newcode |
|---|---|---|
| Format | Notebook eksperimen | Notebook terstruktur dan mandiri |
| Path data | Nama relatif yang tidak tersedia | Path eksplisit dari root proyek |
| Target | Mengharapkan `sisa jam` tersedia | Menggunakan target atau membentuknya dari Break |
| Validasi schema | Tidak ada | Validasi fitur, target, lifetime, dan status |
| Konversi numerik | `astype(float)` | `to_numeric(errors="coerce")` |
| Header duplikat | Tidak ditangani | Dideteksi dan dibuang |
| Status | Pencocokan case-sensitive | Dinormalisasi dengan casefold |
| Split | Acak 80:20 | Acak 80:20 dengan konfigurasi eksplisit |
| Cross-validation | `cv=5` default | K-fold acak dengan shuffle dan seed |
| Seed optimizer | Tidak ditetapkan | Seed 42 untuk ABC dan PSO |
| Cache objektif | Tidak ada | Ada |
| Early stopping | Tidak ada | Ada |
| Pencatatan hasil | Output notebook | JSON, CSV, gambar, dan model bundle |
| Build | Parameter dipindah manual | Parameter dibaca dari artefak optimizer |
| Validasi model | Tidak ada | Reload dan verifikasi prediksi |
| Generalisasi | Terikat nama file lama | Konfigurasi dapat diganti untuk dataset lain |

### 11.2 Perubahan data

Oldcode dan newcode tidak memakai versi dataset yang sepenuhnya sama:

| Informasi | Oldcode | Newcode |
|---|---:|---:|
| Data Critical | 645 | 720 |
| Kolom target | Sudah tersedia | Dibentuk saat runtime |
| File yang dirujuk | `Data_PT. Amanah_Critical_Break.xlsx` | `datas/Data_PT.Amanah_Critical_Break.xlsx` |

Karena populasi data berubah, hasil metrik lama dan baru tidak dapat dibandingkan sebagai pengaruh algoritma saja.

### 11.3 Perubahan ABC

Oldcode melakukan evaluasi objektif berulang, termasuk mengevaluasi ulang seluruh populasi untuk mencari best pada setiap iterasi. Newcode menyimpan hasil kandidat dalam cache dan memelihara global best sehingga evaluasi yang sama tidak perlu diulang.

Pembaruan lain:

- Seed eksplisit.
- Early stopping.
- Validasi konfigurasi.
- Pencatatan jumlah evaluasi unik.
- Penyimpanan parameter, metrik, kurva, prediksi, dan model.

### 11.4 Perubahan PSO

Oldcode menggunakan satu nilai `r1` dan `r2` untuk seluruh dimensi dalam satu partikel. Newcode menggunakan matrix random sehingga setiap dimensi mempunyai faktor cognitive dan social independen.

Pembaruan lain:

- Generator random dengan seed.
- Personal best dan global best yang eksplisit.
- Cache fungsi objektif.
- Early stopping.
- Metadata serta artefak terstruktur.

### 11.5 Perbaikan build model lama

Pada oldcode terdapat kesalahan berikut:

```python
joblib.dump(
    svr_pipeline,
    "model_Rf(new).pkl"
)
```

Kode tersebut menyimpan model SVR ke file yang diberi nama Random Forest. Selain itu, bagian berjudul PSO memakai parameter Random Forest hasil ABC.

Newcode memperbaikinya dengan:

- Membaca parameter langsung dari artefak ABC dan PSO.
- Melatih objek Random Forest yang benar.
- Menyimpan optimizer asal di dalam bundle.
- Menghasilkan nama file yang konsisten.
- Memuat ulang file dan memverifikasi tipe optimizer serta prediksi.

### 11.6 Perbandingan hasil Random Forest lama dan baru

| Hasil | Old ABC RF | New ABC RF | Old PSO RF | New PSO RF |
|---|---:|---:|---:|---:|
| CV MSE | 29.385,13 | 41.447,12 | 29.185,90 | 40.289,39 |
| Test RMSE | 152,89 | 235,56 | 154,41 | 236,85 |
| Test MAE | 77,23 | 123,18 | 91,31 | 122,51 |
| Test R² | 0,9556 | 0,9128 | 0,9547 | 0,9119 |

Penurunan angka pada newcode tidak boleh langsung disimpulkan sebagai penurunan kualitas implementasi karena:

1. Oldcode memakai 645 data Critical, sedangkan newcode memakai 720.
2. Target pada file lama sudah tersedia, sedangkan newcode membentuk target dari failure hour.
3. K-fold newcode mengaktifkan shuffle dan seed secara eksplisit.
4. Parameter terbaik dipengaruhi populasi data dan urutan random optimizer.

Perbandingan yang valid harus menggunakan dataset, target, split, fold, seed, dan ruang pencarian yang benar-benar identik.

## 12. Urutan Pengerjaan

### 12.1 Menyiapkan environment

Aktifkan virtual environment:

```bash
source .venv/bin/activate
```

Pasang dependensi jika belum tersedia:

```bash
python -m pip install -r newcode/requirements.txt
```

Pilih `.venv/bin/python` sebagai kernel Jupyter.

### 12.2 Menjalankan ABC

1. Buka `newcode/ABC_RF.ipynb`.
2. Periksa cell konfigurasi dataset dan target.
3. Jalankan seluruh cell menggunakan **Run All**.
4. Pastikan `metrics.json` dan `model.joblib` terbentuk pada folder artefak ABC.

### 12.3 Menjalankan PSO

1. Buka `newcode/PSO_RF.ipynb`.
2. Pastikan kontrak data sama dengan notebook ABC.
3. Jalankan seluruh cell menggunakan **Run All**.
4. Pastikan `metrics.json` dan `model.joblib` terbentuk pada folder artefak PSO.

### 12.4 Menjalankan build model

1. Pastikan hasil ABC dan PSO sudah tersedia.
2. Buka `newcode/Build_RF.ipynb`.
3. Jalankan seluruh cell menggunakan **Run All**.
4. Periksa optimizer yang dipilih berdasarkan CV MSE.
5. Pastikan tiga file model dan metadata build terbentuk.
6. Pastikan cell terakhir menyatakan seluruh model berhasil diverifikasi.

### 12.5 Keluar dari environment

```bash
deactivate
```

## 13. Cara Menggunakan Model Terbaik

Bundle model utama tersedia pada:

```text
newcode/models/pt_amanah_critical/random_forest_best.joblib
```

Contoh konsep pemuatan:

```python
import joblib

bundle = joblib.load(
    "newcode/models/pt_amanah_critical/random_forest_best.joblib"
)

model = bundle["model"]
features = bundle["features"]
optimizer = bundle["optimizer"]

prediction = model.predict(new_data[features])
```

Urutan dan nama fitur wajib mengikuti `bundle["features"]`. Data input juga harus melalui validasi dan konversi numerik yang sama seperti data training.

## 14. Keterbatasan

1. Dataset awal hanya merepresentasikan satu rangkaian kendaraan PT Amanah.
2. Model final dilatih hanya menggunakan status Critical.
3. Target RUL dibentuk dari satu failure hour, bukan dari banyak siklus kerusakan.
4. Unit Lifetime tidak digunakan sebagai fitur model.
5. Belum ada evaluasi pada kendaraan atau lokasi yang benar-benar berbeda.
6. Random split dapat menempatkan observasi dengan kondisi serupa pada train dan test.
7. Feature importance Random Forest tidak menunjukkan hubungan sebab-akibat.
8. Nilai optimal ABC dan PSO dapat berubah apabila seed, populasi, atau dataset berubah.
9. Pemilihan PSO berdasarkan satu rangkaian optimasi belum membuktikan keunggulan statistik secara umum.
10. Model belum dilengkapi interface inferensi untuk data produksi.

## 15. Rekomendasi Pengembangan

1. Menjalankan ABC dan PSO pada beberapa seed, lalu membandingkan rata-rata dan variasi metrik.
2. Menguji model pada unit kendaraan lain sebagai external holdout.
3. Menyediakan baseline Random Forest tanpa optimasi.
4. Membandingkan random split dengan split berdasarkan kendaraan atau periode.
5. Menambahkan analisis residual berdasarkan rentang RUL.
6. Menambahkan pemeriksaan outlier serta distribusi fitur antarunit.
7. Menguji kestabilan feature importance menggunakan permutation importance.
8. Menambahkan interval ketidakpastian prediksi.
9. Membuat notebook inferensi terpisah setelah kontrak input produksi ditentukan.
10. Menambahkan skenario eksperimen hanya setelah instruksi dan tujuan skenario ditetapkan.

## 16. Kesimpulan

Newcode berhasil memisahkan proses optimasi ABC, optimasi PSO, dan build model ke dalam tiga notebook yang mempunyai tanggung jawab jelas. Kedua optimizer menggunakan pipeline data, random split, K-fold, ruang pencarian, dan seed yang sama sehingga dapat dibandingkan secara konsisten.

ABC menghasilkan test RMSE dan R² sedikit lebih baik, sedangkan PSO memberikan CV MSE lebih rendah, MAE sedikit lebih rendah, evaluasi lebih sedikit, dan waktu proses lebih cepat. Berdasarkan kriteria CV MSE, PSO dipilih sebagai model utama. Kedua model tetap disimpan agar keputusan dapat dievaluasi kembali ketika tersedia data eksternal.

Build model baru juga memperbaiki kesalahan serialisasi pada oldcode, menghilangkan perpindahan parameter secara manual, menyimpan metadata lengkap, dan memverifikasi model setelah dimuat kembali. Hasil akhir berupa bundle Random Forest yang lebih mudah ditelusuri dan digunakan kembali.

Walaupun hasil test menunjukkan R² sekitar 0,91, pengujian lebih lanjut pada kendaraan atau lokasi lain tetap diperlukan sebelum model digunakan sebagai dasar keputusan operasional.
