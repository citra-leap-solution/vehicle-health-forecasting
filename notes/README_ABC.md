# ABC Random Forest

`newcode/ABC_Random_Forest.ipynb` adalah notebook generik untuk mengoptimalkan hyperparameter `RandomForestRegressor` menggunakan Artificial Bee Colony (ABC). Notebook tidak terikat pada nama unit atau lokasi tertentu; dataset serta parameter eksperimen ditentukan melalui cell konfigurasi.

## Kemampuan

- Membaca Excel (`.xlsx`/`.xls`) dan CSV.
- Menoleransi perbedaan kapitalisasi status.
- Menoleransi variasi kolom temperatur dengan atau tanpa akhiran `(°C)`.
- Menggunakan target yang sudah tersedia pada dataset.
- Membentuk target RUL dari baris berstatus `Break` atau nilai `failure_hour` eksplisit.
- Memfilter status yang digunakan untuk training.
- Menggunakan holdout acak dan K-fold acak dengan seed tetap.
- Menggunakan seed tetap, cache evaluasi, dan early stopping.
- Menyimpan model, konfigurasi, metrik, prediksi, feature importance, dan grafik.

## Instalasi

Jalankan dari root proyek:

```bash
python -m pip install -r newcode/requirements.txt
```

## Menjalankan Notebook

Buka `newcode/ABC_Random_Forest.ipynb`, pilih kernel Python yang sudah memiliki dependensi, lalu jalankan cell secara berurutan dari atas ke bawah.

Konfigurasi awal menggunakan:

```text
datas/Data_PT.Amanah_Critical_Break.xlsx
```

Dataset PT Amanah tidak memiliki kolom `sisa jam`. Notebook mendeteksi lifetime pada baris `Break` dan membentuk target:

```text
RUL = min(max_rul, max(0, failure_hour - Unit Lifetime))
```

Pada konfigurasi awal, `failure_hour` terdeteksi sebagai 78.637 dan `max_rul` bernilai 2.550 agar konsisten dengan keluaran oldcode.

## Menggunakan Dataset Lain

Ubah nilai `cfg` pada bagian **Konfigurasi eksperimen** di dalam notebook:

- `cfg["data"]`: path Excel atau CSV.
- `cfg["run_name"]`: nama eksperimen dan folder hasil.
- `cfg["target"]["train_status"]`: status yang digunakan untuk training.
- `cfg["target"]["failure_hour"]`: wajib diisi jika target dan baris `Break` tidak tersedia.
- `cfg["target"]["max_rul"]`: batas maksimum RUL atau `None` jika tidak dibatasi.
- `cfg["split"]`: proporsi test dan jumlah fold.
- `cfg["abc"]`: ukuran populasi, limit, iterasi, dan patience.

## Artefak

Setiap eksekusi lengkap membuat folder `newcode/artifacts/<run_name>/` berisi:

- `model.joblib`
- `metrics.json`
- `convergence.json`
- `test_predictions.csv`
- `convergence.png`
- `actual_vs_predicted.png`

Direktori artefak diabaikan Git karena hasil eksperimen dapat dibuat ulang.

## Catatan Validasi

Notebook menggunakan evaluasi acak karena observasi pada dataset diperoleh secara acak. Seed tetap digunakan pada holdout dan K-fold agar hasil pembagian dapat direproduksi serta lebih sebanding dengan oldcode.
