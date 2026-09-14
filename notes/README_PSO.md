# PSO Random Forest

`newcode/PSO_RF.ipynb` adalah notebook generik untuk mengoptimalkan hyperparameter `RandomForestRegressor` menggunakan Particle Swarm Optimization (PSO). Pipeline data dan evaluasinya dibuat konsisten dengan notebook ABC agar hasil kedua optimizer dapat dibandingkan.

## Mekanisme PSO

Notebook menggunakan komponen PSO berikut:

- Position untuk merepresentasikan hyperparameter setiap partikel.
- Velocity untuk menentukan perpindahan partikel.
- Personal best (`pbest`) untuk menyimpan pengalaman terbaik setiap partikel.
- Global best (`gbest`) untuk menyimpan solusi terbaik seluruh swarm.
- Inertia weight (`w`).
- Cognitive coefficient (`c1`).
- Social coefficient (`c2`).
- Nilai acak `r1` dan `r2` yang independen untuk setiap partikel dan dimensi.
- Boundary clipping agar posisi tetap berada dalam ruang pencarian.
- Cache evaluasi dan early stopping.

PSO langsung meminimalkan MSE dan tidak menggunakan employed bee, onlooker bee, scout bee, fitness probability, trial, atau limit milik ABC.

## Konfigurasi Awal

Konfigurasi awal menggunakan:

```text
datas/Data_PT.Amanah_Critical_Break.xlsx
```

Pengaturan default PSO:

```text
n_particles = 20
max_iter = 30
w = 0.7
c1 = 1.5
c2 = 1.5
patience = 8
seed = 42
```

Target RUL dibentuk dari lifetime pada baris `Break` dan dibatasi maksimum 2.550 jam. Hanya data berstatus `Critical` yang digunakan untuk training.

## Menjalankan Notebook

1. Pasang dependensi dari `newcode/requirements.txt`.
2. Buka `newcode/PSO_RF.ipynb`.
3. Pilih kernel virtual environment proyek.
4. Jalankan seluruh cell secara berurutan menggunakan **Run All**.

## Evaluasi

Notebook menggunakan random holdout 80:20 dan K-fold acak dengan seed 42. Konfigurasi split, fitur, target, dan ruang pencarian sama dengan notebook ABC.

## Artefak

Hasil disimpan di:

```text
newcode/artifacts/pso_pt_amanah_random/
```

Artefak yang dihasilkan:

- `model.joblib`
- `metrics.json`
- `convergence.json`
- `test_predictions.csv`
- `convergence.png`
- `actual_vs_predicted.png`
