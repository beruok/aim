from flask import Flask, render_template, request
import pandas as pd
import os
import glob

app = Flask(__name__)

# --- 補助関数 ---
def str_rate_to_float(rate):
    try:
        return float(rate.split("/")[1])
    except:
        return None

def rb_rate_str_to_float(rate):
    try:
        return float(rate.split("/")[1])
    except:
        return float("inf")

# --- メインルート ---
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    result_sorted = None
    error = None

    if request.method == "POST":
        # フォームから値を取得
        start_year = request.form.get("start_year", "")
        end_year = request.form.get("end_year", "")
        start_month = request.form.get("start_month", "")
        end_month = request.form.get("end_month", "")
        selected_days = request.form.getlist("days")

        # 未入力チェック
        if not (start_year and end_year and start_month and end_month and selected_days):
            error = "すべての項目を選択してください。"
            return render_template("index.html", result=None, result_sorted=None, error=error)

        # 数値に変換
        start_year = int(start_year)
        end_year = int(end_year)
        start_month = int(start_month)
        end_month = int(end_month)

        # 対象ファイルを抽出
        data_dir = "../data"
        file_list = glob.glob(os.path.join(data_dir, "aim_*.csv"))
        target_files = []

        for file in file_list:
            basename = os.path.basename(file)  # e.g. aim_20250417.csv
            y = int(basename[4:8])
            m = int(basename[8:10])
            d = basename[10:12]
            if start_year <= y <= end_year and start_month <= m <= end_month and d in selected_days:
                target_files.append(file)

        # CSVの読み込みと集計
        df_list = []
        for file in target_files:
            df = pd.read_csv(file)
            df = df[["台番", "G数", "BB", "RB", "BB率", "RB率"]].copy()
            df_list.append(df)

        if df_list:
            df_all = pd.concat(df_list, ignore_index=True)
            df_all["BB率数値"] = df_all["BB率"].apply(str_rate_to_float)
            df_all["RB率数値"] = df_all["RB率"].apply(str_rate_to_float)

            # 合計と平均を集計
            agg_numeric = df_all.groupby("台番")[["G数", "BB", "RB"]].sum()
            agg_rate = df_all.groupby("台番")[["BB率数値", "RB率数値"]].mean().round()

            # BB率・RB率を "1/xxx" に戻す
            agg_rate["BB率_avg"] = agg_rate["BB率数値"].apply(
                lambda x: f"1/{int(x)}" if pd.notnull(x) and x != 0 else "-"
            )
            agg_rate["RB率_avg"] = agg_rate["RB率数値"].apply(
                lambda x: f"1/{int(x)}" if pd.notnull(x) and x != 0 else "-"
            )

            # 結合
            result = pd.concat([agg_numeric, agg_rate[["BB率_avg", "RB率_avg"]]], axis=1).reset_index()

            # 欠損を "-" に置換（←これが肝心！）
            result.fillna("-", inplace=True)

            # RB率でソートしたバージョン
            result_sorted = result.copy()
            result_sorted["RB_rate_sort"] = result_sorted["RB率_avg"].apply(rb_rate_str_to_float)
            result_sorted = result_sorted.sort_values("RB_rate_sort")
            result_sorted.fillna("-", inplace=True)

    return render_template("index.html", result=result, result_sorted=result_sorted, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
