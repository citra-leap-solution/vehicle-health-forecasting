# Build Model Random Forest

`newcode/Build_RF.ipynb` membangun model final dari hyperparameter terbaik hasil optimasi ABC dan PSO.

## Prasyarat

Jalankan notebook berikut terlebih dahulu:

1. `newcode/ABC_RF.ipynb`
2. `newcode/PSO_RF.ipynb`

Keduanya harus menghasilkan `metrics.json` pada direktori artefak masing-masing.

## Proses Build

Notebook melakukan proses berikut:

1. Memuat parameter dan metrik hasil ABC serta PSO.
2. Memastikan kontrak data kedua optimizer sama.
3. Memilih optimizer dengan CV MSE terkecil.
4. Menyiapkan seluruh data berstatus Critical.
5. Melatih ulang dua Random Forest pada seluruh data tersebut.
6. Menyimpan model ABC, model PSO, dan alias model terbaik.
7. Memuat ulang model untuk memverifikasi tipe optimizer dan konsistensi prediksi.

Metrik pada seluruh data training hanya digunakan sebagai diagnosis. Evaluasi generalisasi tetap memakai hasil holdout acak dari notebook optimizer.

## Menjalankan

Buka `newcode/Build_RF.ipynb`, pilih kernel virtual environment proyek, lalu gunakan **Run All**.

## Hasil

Konfigurasi awal menyimpan hasil ke:

```text
newcode/models/pt_amanah_critical/
```

File yang dihasilkan:

- `random_forest_abc.joblib`
- `random_forest_pso.joblib`
- `random_forest_best.joblib`
- `build_summary.json`
- `training_predictions.csv`
- `model_comparison.png`

Setiap file model berupa bundle yang mencakup objek model, optimizer asal, urutan fitur, hyperparameter, aturan target, seed, dan metadata data.
