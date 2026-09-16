"""Dashboard prediksi sisa jam untuk proyek Vehicle Health."""

from io import BytesIO
from pathlib import Path
import re
import json

import joblib
import numpy as np
import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
SENSOR_COLS = [
    "Exhaust Gas Temperature LF (Left Front)",
    "Exhaust Gas Temperature LR (Left Rear)",
    "Exhaust Gas Temperature RF (Right Front)",
    "Exhaust Gas Temperature RR (Right Rear)",
    "Blowby Pressure (Kpa)",
    "Boost Pressure (Kpa)",
    "Engine Oil Temp (°C)",
    "Coolant Temp (°C)",
]
MODEL_PATHS = {
    "Unggah model sendiri": None,
    "Skenario 01 — PSO SVR": ROOT / "newcode/scenarios/01_RF_SVR_data_single/models/best_model.joblib",
    "Skenario 02 — PSO Random Forest": ROOT / "newcode/scenarios/02_RF_SVR_data_gabungan/models/best_model.joblib",
}


@st.cache_resource(show_spinner=False)
def load_path(path: str):
    """Memuat model bawaan yang sudah berada di proyek."""
    return joblib.load(path)


def load_upload(data: bytes):
    """Memuat model unggahan; gunakan hanya berkas dari sumber tepercaya."""
    return joblib.load(BytesIO(data))


def load_data(file) -> pd.DataFrame:
    """Membaca data CSV atau Excel dari unggahan pengguna."""
    suffix = Path(file.name).suffix.lower()
    raw = BytesIO(file.getvalue())
    if suffix == ".csv":
        return pd.read_csv(raw)
    return pd.read_excel(raw)


def clean_name(value: object) -> str:
    """Membersihkan spasi dan karakter tak terlihat pada header data."""
    text = str(value).replace("\xa0", " ").strip()
    return re.sub(r"\s+", " ", text)


def align_cols(data: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, list[dict[str, str]]]:
    """Menyamakan variasi header data dengan nama fitur yang direkam model."""
    old_cols = list(data.columns)
    data = data.copy()
    data.columns = [clean_name(col) for col in old_cols]
    changed = [
        {"kolom_data": str(old), "kolom_dibersihkan": new}
        for old, new in zip(old_cols, data.columns)
        if str(old) != new
    ]

    aliases = {f"{col} (°C)": col for col in cols[:4]}
    rename = {}
    existing = set(data.columns)
    for old, new in aliases.items():
        if old in existing and new not in existing:
            rename[old] = new
            changed.append({"kolom_data": old, "kolom_dibersihkan": new})
    return data.rename(columns=rename), changed


def clean_data(data: pd.DataFrame, cols: list[str]) -> tuple[pd.DataFrame, dict[str, int]]:
    """Menghapus header ganda dan baris sensor yang tidak dapat diprediksi."""
    info = {"total": len(data), "header": 0, "invalid": 0, "ready": 0}
    header = pd.Series(True, index=data.index)
    for col in cols:
        header &= data[col].astype("string").map(clean_name).eq(col)
    info["header"] = int(header.sum())
    data = data.loc[~header].copy()

    for col in cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    invalid = data[cols].isna().any(axis=1)
    info["invalid"] = int(invalid.sum())
    data = data.loc[~invalid].copy()
    info["ready"] = len(data)
    return data, info


def model_name(model) -> str:
    """Mengambil nama estimator akhir, termasuk apabila model berupa Pipeline."""
    if hasattr(model, "steps") and model.steps:
        return type(model.steps[-1][1]).__name__
    return type(model).__name__


def model_cols(model) -> list[str]:
    """Mengambil fitur yang direkam model, atau memakai standar proyek."""
    cols = getattr(model, "feature_names_in_", None)
    if cols is None and hasattr(model, "steps") and model.steps:
        cols = getattr(model.steps[-1][1], "feature_names_in_", None)
    return list(cols) if cols is not None else SENSOR_COLS


def make_hist(values: pd.Series) -> pd.DataFrame:
    """Membentuk histogram sederhana yang dapat ditampilkan Streamlit."""
    count, edge = np.histogram(values.dropna(), bins=min(20, max(5, len(values) // 10)))
    labels = [f"{edge[i]:.0f}–{edge[i + 1]:.0f}" for i in range(len(count))]
    return pd.DataFrame({"jumlah": count}, index=labels)


@st.cache_data(show_spinner=False)
def load_metrics(path: str) -> tuple[dict, dict] | tuple[None, None]:
    """Membaca metrik kandidat terpilih dari artefak model bawaan."""
    model_dir = Path(path).parent
    summary_path = model_dir / "build_summary.json"
    compare_path = model_dir / "model_comparison.csv"
    threshold_path = model_dir / "threshold_comparison.csv"
    if not all(item.exists() for item in [summary_path, compare_path, threshold_path]):
        return None, None
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    selected = summary["selected_model"]
    compare = pd.read_csv(compare_path).set_index("candidate")
    threshold = pd.read_csv(threshold_path)
    row = compare.loc[selected].to_dict()
    limit = int(summary["primary_threshold_hours"])
    score = threshold[(threshold["candidate"] == selected) & (threshold["scope"] == "test") & (threshold["threshold"] == limit)]
    return row, score.iloc[0].to_dict() if not score.empty else None


st.set_page_config(page_title="Vehicle Health Forecast", page_icon="⚙️", layout="wide")
st.title("Vehicle Health — Forecasting Sisa Jam")
st.caption("Unggah model dan data sensor untuk memperoleh prediksi Remaining Useful Life (RUL).")

with st.sidebar:
    st.header("Input model")
    choice = st.selectbox("Sumber model", list(MODEL_PATHS))
    upload_model = None
    if choice == "Unggah model sendiri":
        upload_model = st.file_uploader("Model .joblib", type=["joblib"])
        st.warning("Unggah `.joblib` hanya dari sumber tepercaya. Berkas joblib dapat menjalankan kode saat dimuat.")
    st.divider()
    st.header("Input data")
    upload_data = st.file_uploader("Data sensor (.xlsx atau .csv)", type=["xlsx", "xls", "csv"])
    clip = st.checkbox("Batasi prediksi ke 0–2.550 jam", value=True)

model = None
load_error = None
try:
    if choice != "Unggah model sendiri":
        path = MODEL_PATHS[choice]
        if path and path.exists():
            model = load_path(str(path))
        else:
            load_error = "Model bawaan belum ditemukan pada lokasi proyek."
    elif upload_model is not None:
        model = load_upload(upload_model.getvalue())
except Exception as error:
    load_error = f"Model tidak dapat dimuat: {error}"

if load_error:
    st.error(load_error)

if model is not None:
    cols = model_cols(model)
    left, right = st.columns(2)
    left.metric("Tipe model", model_name(model))
    right.metric("Jumlah fitur", len(cols))
    with st.expander("Fitur yang dibutuhkan model", expanded=False):
        st.dataframe(pd.DataFrame({"nama_kolom": cols}), hide_index=True, use_container_width=True)

    if choice != "Unggah model sendiri":
        metric, threshold = load_metrics(str(MODEL_PATHS[choice]))
        if metric:
            st.subheader("Metrik model terpilih")
            st.caption("Metrik ini berasal dari artefak eksperimen model, bukan dari data yang baru diunggah.")
            row_a = st.columns(3)
            row_a[0].metric("CV MSE", f"{metric['cv_mse']:.2f}")
            row_a[1].metric("CV RMSE", f"{metric['cv_rmse']:.2f} jam")
            row_a[2].metric("Test MSE", f"{metric['test_mse']:.2f}")
            row_b = st.columns(3)
            row_b[0].metric("Test RMSE", f"{metric['test_rmse']:.2f} jam")
            row_b[1].metric("Test MAE", f"{metric['test_mae']:.2f} jam")
            row_b[2].metric("Test R²", f"{metric['test_r2']:.4f}")
            if threshold:
                st.caption("Evaluasi test pada ambang 250 jam")
                row_c = st.columns(4)
                row_c[0].metric("TN", f"{int(threshold['tn'])}")
                row_c[1].metric("FP", f"{int(threshold['fp'])}")
                row_c[2].metric("FN", f"{int(threshold['fn'])}")
                row_c[3].metric("TP", f"{int(threshold['tp'])}")
                row_d = st.columns(4)
                row_d[0].metric("Accuracy", f"{threshold['accuracy'] * 100:.2f}%")
                row_d[1].metric("Precision", f"{threshold['precision'] * 100:.2f}%")
                row_d[2].metric("Recall", f"{threshold['recall'] * 100:.2f}%")
                row_d[3].metric("F1 Score", f"{threshold['f1'] * 100:.2f}%")
    else:
        st.info("Metrik training model unggahan tidak tersedia tanpa artefak eksperimen pendukung.")

st.divider()
st.subheader("Prediksi batch")

if upload_data is None:
    st.info("Pilih model dan unggah data sensor untuk memulai prediksi.")
elif model is None:
    st.info("Model perlu tersedia terlebih dahulu sebelum data dapat diprediksi.")
else:
    try:
        data = load_data(upload_data)
    except Exception as error:
        st.error(f"Data tidak dapat dibaca: {error}")
        st.stop()

    data, changed = align_cols(data, cols)
    if changed:
        with st.expander("Penyesuaian nama kolom", expanded=False):
            st.info("Dashboard menyesuaikan header data agar cocok dengan fitur model.")
            st.dataframe(pd.DataFrame(changed), hide_index=True, use_container_width=True)

    missing = [col for col in cols if col not in data.columns]
    if missing:
        st.error("Kolom wajib tidak ditemukan. Gunakan nama kolom yang sama dengan model.")
        st.dataframe(pd.DataFrame({"kolom_yang_kurang": missing}), hide_index=True, use_container_width=True)
        st.stop()

    data, clean = clean_data(data, cols)
    if clean["header"] or clean["invalid"]:
        with st.expander("Ringkasan pembersihan data", expanded=True):
            st.dataframe(
                pd.DataFrame([
                    {"keterangan": "Baris data awal", "jumlah": clean["total"]},
                    {"keterangan": "Header ganda yang dihapus", "jumlah": clean["header"]},
                    {"keterangan": "Baris sensor tidak valid yang dihapus", "jumlah": clean["invalid"]},
                    {"keterangan": "Baris siap diprediksi", "jumlah": clean["ready"]},
                ]),
                hide_index=True,
                use_container_width=True,
            )
            st.warning("Baris yang dihapus tidak diprediksi karena tidak memiliki delapan nilai sensor numerik lengkap.")

    if data.empty:
        st.error("Tidak ada baris yang siap diprediksi setelah pembersihan data.")
        st.stop()

    feature = data[cols].copy()

    run_key = f"{choice}:{upload_data.name}:{upload_data.size}:{clip}"
    run = st.button("Proses Prediksi", type="primary", use_container_width=False)
    if run:
        st.session_state["run_key"] = run_key

    if st.session_state.get("run_key") != run_key:
        st.info("Data siap diproses. Tekan tombol **Proses Prediksi** untuk menjalankan model.")
        st.stop()

    try:
        pred = np.asarray(model.predict(feature), dtype=float)
    except Exception as error:
        st.error(f"Prediksi gagal dijalankan: {error}")
        st.stop()

    if clip:
        pred = np.clip(pred, 0, 2550)

    result = data.copy()
    result["prediksi_sisa_jam"] = pred
    result["status_peringatan_250_jam"] = np.where(pred <= 250, "Perlu perhatian", "Normal")

    total = len(result)
    warning = int((pred <= 250).sum())
    a, b, c, d = st.columns(4)
    a.metric("Jumlah baris", f"{total:,}")
    b.metric("Rata-rata prediksi", f"{pred.mean():.2f} jam")
    c.metric("Prediksi minimum", f"{pred.min():.2f} jam")
    d.metric("Perlu perhatian ≤250 jam", f"{warning:,}")

    tab_data, tab_chart, tab_eval = st.tabs(["Hasil prediksi", "Visualisasi", "Evaluasi jika target tersedia"])
    with tab_data:
        st.dataframe(result, use_container_width=True, height=420)
        csv = result.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Unduh hasil CSV", csv, "hasil_prediksi_sisa_jam.csv", "text/csv")

    with tab_chart:
        chart_left, chart_right = st.columns(2)
        with chart_left:
            st.caption("Distribusi prediksi sisa jam")
            st.bar_chart(make_hist(result["prediksi_sisa_jam"]), use_container_width=True)
        with chart_right:
            st.caption("Jumlah hasil berdasarkan status peringatan")
            count = result["status_peringatan_250_jam"].value_counts().reindex(["Normal", "Perlu perhatian"], fill_value=0)
            st.bar_chart(count, use_container_width=True)

    with tab_eval:
        target = "sisa_jam"
        if target not in result.columns:
            st.info("Tambahkan kolom `sisa_jam` pada data untuk membandingkan aktual dengan prediksi.")
        else:
            actual = pd.to_numeric(result[target], errors="coerce")
            valid = actual.notna()
            if not valid.any():
                st.warning("Kolom `sisa_jam` tidak berisi nilai numerik yang dapat dievaluasi.")
            else:
                err = actual[valid] - pred[valid]
                mse = float(np.mean(err ** 2))
                mae = float(np.mean(np.abs(err)))
                rmse = float(np.sqrt(mse))
                ss_res = float(np.sum(err ** 2))
                ss_tot = float(np.sum((actual[valid] - actual[valid].mean()) ** 2))
                r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")
                e1, e2, e3, e4 = st.columns(4)
                e1.metric("MSE", f"{mse:.2f}")
                e2.metric("RMSE", f"{rmse:.2f} jam")
                e3.metric("MAE", f"{mae:.2f} jam")
                e4.metric("R²", f"{r2:.4f}")
                plot = pd.DataFrame({"aktual_sisa_jam": actual[valid], "prediksi_sisa_jam": pred[valid]})
                st.scatter_chart(plot, x="aktual_sisa_jam", y="prediksi_sisa_jam", color="#2563eb", use_container_width=True)
