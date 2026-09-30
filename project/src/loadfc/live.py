"""Live, prospective day-ahead forecasts.

Once a day, on day D-1 before 12:00 local time (day-ahead gate closure),
forecast every hour of day D and store the result. Stored forecasts are
never changed afterwards. The wrapper script tools/run-live.ps1 commits and
pushes them to GitHub, whose commit timestamps are an independent record
that each forecast existed before the official forecast was published.

Everything that could be tuned is frozen in live/settings.json, written by
`python -m loadfc live_setup` from the validation results, before the first
live forecast. The hypotheses are stated in live/PREREGISTRATION.md.

Variants stored every day
  lgbm, chronos, ensemble                 load up to D-2 (the headline setup)
  *_morning                               + load of D-1 until 08:00
  chronos_ft, ensemble_ft(_morning)       Chronos-2 fine-tuned monthly (GPU only)
  q05 ... q95                             probabilistic: avg(LightGBM + conformal, Chronos-2)
"""

import hashlib
import json
import platform
import subprocess

import lightgbm as lgb
import pandas as pd

from . import config, features, foundation, models, smard, weather
from .experiments import QUANTILES, _finetune, _prob_scores, conformal, correct, pinball
from .features import FEATURES, MORNING_FEATURES, TARGET

LIVE = config.ROOT / "live"
FORECASTS = LIVE / "forecasts"
SETTINGS = LIVE / "settings.json"
MODELS = config.DATA_PROCESSED / "live_models"   # large, not in git
DRYRUN = config.DATA_PROCESSED / "live_dryrun"
# Live data lives in its own copy, so the frozen backtest inputs in data/raw are never touched.
LIVE_RAW = config.DATA_RAW / "live"


def _raw(name: str):
    """Path of a live raw file; initialised from the backtest copy on first use."""
    import shutil

    LIVE_RAW.mkdir(parents=True, exist_ok=True)
    path = LIVE_RAW / name
    if not path.exists():
        shutil.copy(config.DATA_RAW / name, path)
    return path


def _now() -> pd.Timestamp:
    return pd.Timestamp.now(tz=config.TZ)


def _midnight(ts: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(ts.year, ts.month, ts.day, tz=config.TZ)


# ------------------------------------------------------------------- setup
def setup() -> dict:
    """Freeze every choice from the main window's validation period."""
    df = pd.read_parquet(config.DATA_PROCESSED / "features.parquet")
    meta = json.loads((config.DATA_PROCESSED / "meta_main.json").read_text())
    morning_rounds, _ = models.choose_rounds(
        features.add_morning_load(df), config.WINDOWS["main"], feature_list=FEATURES + MORNING_FEATURES)
    settings = {
        "frozen_on": str(_now().date()),
        "source": "validation period of the main window (2025-07-01 to 2025-09-30)",
        "lgbm_rounds": meta["lgbm_rounds"],
        "lgbm_morning_rounds": morning_rounds,
        "chronos_context_hours": meta["chronos_context_hours"],
        # reports/FINETUNE.md, main window
        "finetune_config": {"finetune_mode": "lora", "learning_rate": 1e-5, "num_steps": 500},
        "finetune_context_hours": 2048,
        # reports/PROBABILISTIC.md, main window
        "conformal_window_lgbm": 28,
        "conformal_window_official": 42,
        # reports/EXPERIMENTS.md, main window
        "official_bias_correction": {"window_days": 14, "alpha": 1.0, "by_hour": True},
        "deadline_hour_local": 12,
        "morning_until_hour_local": features.MORNING_UNTIL,
    }
    LIVE.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps(settings, indent=2))
    return settings


# -------------------------------------------------------------------- data
def _merge_into(path, new: pd.DataFrame) -> pd.DataFrame:
    old = features.to_ns(pd.read_parquet(path))
    merged = pd.concat([old, features.to_ns(new)])
    merged = merged[~merged.index.duplicated(keep="last")].sort_index()
    merged.to_parquet(path)
    return merged


def refresh_data(with_weather: bool = True) -> None:
    """Fetch the last weeks of SMARD data and the newest weather forecasts."""
    today = _midnight(_now())
    _merge_into(_raw("smard.parquet"), smard.download_all(today - pd.Timedelta(days=35)))
    if with_weather:
        wpath = _raw("weather.parquet")
        last = pd.read_parquet(wpath).index.max().tz_convert(config.TZ)
        _merge_into(wpath, weather.download(_midnight(last) - pd.Timedelta(days=3), today + pd.Timedelta(days=3)))


def _frame(target: pd.Timestamp) -> pd.DataFrame:
    """Feature table extended a few days past the target day, so future rows exist."""
    series = features.to_ns(pd.read_parquet(_raw("smard.parquet")))
    wx = weather.aggregate(pd.read_parquet(_raw("weather.parquet")))
    end = (target + pd.Timedelta(days=3)).tz_convert("UTC")
    idx = pd.date_range(series.index.min(), end, freq="h", tz="UTC").as_unit("ns")
    return features.build(series.reindex(idx), wx)


# ------------------------------------------------------------------ models
def _month_start(day: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(day.year, day.month, 1, tz=config.TZ)


def _lgbm(df: pd.DataFrame, feats: list[str], tag: str, rounds: int, today: pd.Timestamp) -> lgb.Booster:
    """Monthly retraining, exactly as in the backtest: data up to the day before the month starts."""
    MODELS.mkdir(parents=True, exist_ok=True)
    path = MODELS / f"lgbm_{tag}_{today:%Y-%m}.txt"
    if path.exists():
        return lgb.Booster(model_file=str(path))
    loc = df.index.tz_convert(config.TZ)
    cutoff = _month_start(today) - pd.Timedelta(days=1)
    train = models._trainable(df[(loc >= config.HISTORY_START) & (loc < cutoff)])
    model = lgb.train(models.PARAMS, lgb.Dataset(train[feats], train[TARGET]), num_boost_round=rounds)
    model.save_model(str(path))
    return model


def _chronos_ft(df: pd.DataFrame, today: pd.Timestamp, s: dict):
    """Fine-tuned Chronos-2, refreshed monthly. None without a GPU."""
    import torch

    if not torch.cuda.is_available():
        return None
    from chronos import Chronos2Pipeline

    path = MODELS / f"chronos_ft_{today:%Y-%m}"
    if path.exists():
        return Chronos2Pipeline.from_pretrained(str(path), device_map="cuda")
    ft = _finetune(df, _month_start(today) - pd.Timedelta(days=1), s["finetune_config"])
    ft.save_pretrained(str(path))
    return ft


def _git_commit() -> tuple[str, bool]:
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=config.ROOT, capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "src"], cwd=config.ROOT,
                                    capture_output=True, text=True).stdout.strip())
        return head, dirty
    except OSError:
        return "unknown", True


# ---------------------------------------------------------------- forecast
def forecast(dry_run: bool = False) -> dict:
    s = json.loads(SETTINGS.read_text())
    now = _now()
    today = _midnight(now)
    target = _midnight(today + pd.Timedelta(hours=36))  # tomorrow, DST-safe
    out_dir = DRYRUN if dry_run else FORECASTS
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{target:%Y-%m-%d}.csv"
    if out.exists():
        raise SystemExit(f"{out.name} already exists; stored forecasts are never overwritten")

    # Two schedulers could start at the same moment after the computer wakes up.
    # The lock makes sure only one of them issues the forecast.
    lock = out.with_suffix(".lock")
    _acquire(lock)
    try:
        return _issue(s, now, today, target, out, dry_run)
    finally:
        lock.unlink(missing_ok=True)


def _acquire(lock) -> None:
    """Create the lock file atomically; fail if another run holds it.

    A lock older than an hour can only come from a crashed run and is removed.
    """
    import os
    import time

    if lock.exists() and time.time() - lock.stat().st_mtime > 3600:
        lock.unlink()
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise SystemExit(f"another run for {lock.stem} is in progress")
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)


def _issue(s: dict, now: pd.Timestamp, today: pd.Timestamp, target: pd.Timestamp, out, dry_run: bool) -> dict:
    """Compute, write and describe one forecast. Called with the lock held."""
    if out.exists():  # another run may have finished while this one waited
        raise SystemExit(f"{out.name} already exists; stored forecasts are never overwritten")
    refresh_data()
    df = _frame(target)
    dfm = features.add_morning_load(df)
    rows = df.index[df["date"] == target.tz_localize(None)]
    local = df.index.tz_convert(config.TZ)

    # What was actually known?
    known = df[TARGET].notna()
    last_load = local[known].max()
    today_rows = df["date"] == today.tz_localize(None)
    morning_complete = bool((known & today_rows & (df["hour"] < s["morning_until_hour_local"])).sum() >= s["morning_until_hour_local"])
    yesterday_complete = bool((known & (df["date"] == (today - pd.Timedelta(days=1)).tz_localize(None))).sum() >= 23)
    weather_complete = bool(df.loc[rows, "temp"].notna().all())

    res = pd.DataFrame(index=rows)
    nan = pd.Series(float("nan"), index=rows)

    # LightGBM
    res["lgbm"] = _lgbm(df, FEATURES, "d2", s["lgbm_rounds"], today).predict(df.loc[rows, FEATURES])
    res["lgbm_morning"] = (_lgbm(dfm, FEATURES + MORNING_FEATURES, "morning", s["lgbm_morning_rounds"], today)
                           .predict(dfm.loc[rows, FEATURES + MORNING_FEATURES]) if morning_complete else nan)

    # Chronos-2, zero-shot
    ctx = s["chronos_context_hours"]
    cov = foundation.COVARIATES
    res["chronos"] = foundation.forecast(df, [target], cov, ctx).reindex(rows)
    res["chronos_morning"] = (foundation.forecast(df, [target], cov, ctx, cut_hour=s["morning_until_hour_local"])
                              .reindex(rows) if morning_complete else nan)
    chq = foundation.forecast_quantiles(df, [target], cov, ctx, QUANTILES).reindex(rows)

    # Chronos-2, fine-tuned (GPU only)
    ft = _chronos_ft(df, today, s)
    fctx = s["finetune_context_hours"]
    res["chronos_ft"] = foundation.forecast(df, [target], cov, fctx, pipe=ft).reindex(rows) if ft is not None else nan
    res["chronos_ft_morning"] = (foundation.forecast(df, [target], cov, fctx, pipe=ft, cut_hour=s["morning_until_hour_local"])
                                 .reindex(rows) if ft is not None and morning_complete else nan)

    res["ensemble"] = (res["lgbm"] + res["chronos"]) / 2
    res["ensemble_morning"] = (res["lgbm_morning"] + res["chronos_morning"]) / 2
    res["ensemble_ft"] = (res["lgbm"] + res["chronos_ft"]) / 2
    res["ensemble_ft_morning"] = (res["lgbm_morning"] + res["chronos_ft_morning"]) / 2

    # Probabilistic: LightGBM + conformal, averaged with Chronos-2 quantiles.
    # Residual history: the out-of-sample backtest plus all earlier live forecasts.
    hist = [pd.read_parquet(config.DATA_PROCESSED / "pred_main.parquet")["lgbm"]]
    hist += [_read(f)["lgbm"] for f in sorted(FORECASTS.glob("*.csv"))]
    point = pd.concat(hist + [res["lgbm"]]).sort_index()
    point = point[~point.index.duplicated(keep="last")]
    pdf = df.reindex(point.index)
    q = conformal(point, pdf[TARGET], pd.Series(pdf["date"].to_numpy(), index=point.index),
                  pd.Series(point.index.tz_convert(config.TZ).hour, index=point.index),
                  s["conformal_window_lgbm"]).reindex(rows)
    prob = (q + chq) / 2
    for tau in QUANTILES:
        res[f"q{int(round(tau * 100)):02d}"] = prob[tau]

    res.index.name = "time_utc"
    res.insert(0, "time_local", res.index.tz_convert(config.TZ).strftime("%Y-%m-%d %H:%M%z"))
    res.round(1).to_csv(out)
    # The issue time is when the file exists, not when the run started: a run that
    # starts at 11:58 and finishes at 12:01 is late.
    issued = _now()

    commit, dirty = _git_commit()
    import chronos
    import torch
    manifest = {
        "target_date": str(target.date()),
        "started_at_local": now.isoformat(),
        "issued_at_utc": issued.tz_convert("UTC").isoformat(),
        "issued_at_local": issued.isoformat(),
        "deadline_local": (today + pd.Timedelta(hours=s["deadline_hour_local"])).isoformat(),
        "on_time": bool(issued < today + pd.Timedelta(hours=s["deadline_hour_local"])),
        "dry_run": dry_run,
        "data": {
            "last_load_hour_local": str(last_load),
            "yesterday_complete (day D-2)": yesterday_complete,
            "morning_complete_until_08": morning_complete,
            "weather_for_target_complete": weather_complete,
        },
        "variants_missing": [c for c in res.columns if c != "time_local" and res[c].isna().all()],
        "models": {"lgbm_month": f"{today:%Y-%m}", "chronos_ft": ft is not None},
        "code_commit": commit,
        "code_uncommitted_changes": dirty,
        "versions": {"python": platform.python_version(), "lightgbm": lgb.__version__,
                     "pandas": pd.__version__, "torch": torch.__version__,
                     "chronos": getattr(chronos, "__version__", "?")},
        "sha256_csv": hashlib.sha256(out.read_bytes()).hexdigest(),
    }
    out.with_suffix(".json").write_text(json.dumps(manifest, indent=2))
    return manifest


def _read(path) -> pd.DataFrame:
    d = pd.read_csv(path, index_col="time_utc")
    d.index = pd.to_datetime(d.index, utc=True).as_unit("ns")
    return d


# ---------------------------------------------------------------- evaluate
def evaluate_live() -> tuple[pd.DataFrame, pd.DataFrame, int]:
    """Score all on-time live forecasts whose actuals are known."""
    s = json.loads(SETTINGS.read_text())
    refresh_data(with_weather=False)
    sm = features.to_ns(pd.read_parquet(_raw("smard.parquet")))
    local = sm.index.tz_convert(config.TZ)
    date = pd.Series(local.normalize().tz_localize(None), index=sm.index)
    hour = pd.Series(local.hour, index=sm.index)
    y_all = sm["load_actual"]
    official_bc = correct(sm["load_official"], y_all, date, hour, **s["official_bias_correction"])
    official_q = conformal(sm["load_official"], y_all, date, hour, s["conformal_window_official"])

    frames = []
    for f in sorted(FORECASTS.glob("*.csv")):
        m = json.loads(f.with_suffix(".json").read_text())
        if m["on_time"] and not m["dry_run"]:
            frames.append(_read(f))
    if not frames:
        return pd.DataFrame(), pd.DataFrame(), 0
    fc = pd.concat(frames)
    y = y_all.reindex(fc.index)
    ok = y.notna() & sm["load_official"].reindex(fc.index).notna()
    fc, y = fc[ok], y[ok]
    days = int(pd.Series(date.reindex(fc.index)).nunique())

    points = ["lgbm", "chronos", "ensemble", "lgbm_morning", "chronos_morning", "ensemble_morning",
              "chronos_ft", "ensemble_ft", "ensemble_ft_morning"]
    table = pd.DataFrame(index=fc.index)
    table["official"] = sm["load_official"].reindex(fc.index)
    table["official+bc"] = official_bc.reindex(fc.index)
    for p in points:
        table[p] = fc[p]
    rows = []
    for col in table:
        v = table[col].notna()
        rows.append({"model": col, "hours": int(v.sum()),
                     "MAPE %": float(((table.loc[v, col] - y[v]).abs() / y[v]).mean() * 100) if v.any() else None})
    point_table = pd.DataFrame(rows)

    qcols = [f"q{int(round(t * 100)):02d}" for t in QUANTILES]
    ours = fc[qcols].set_axis(QUANTILES, axis=1)
    bench = official_q.reindex(fc.index)
    prob_table = pd.DataFrame([
        {"method": "avg(LightGBM + conformal, Chronos-2)", **_prob_scores(y, ours)},
        {"method": "official + conformal (benchmark)", **_prob_scores(y, bench)},
    ])
    return point_table, prob_table, days
