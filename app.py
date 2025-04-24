from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    result_sorted = None
    error = None

    if request.method == "POST":
        print("🔥 フォームが送信されました！")
        print("📦 受け取ったフォーム内容:", request.form)

        try:
            start_year = int(request.form.get("start_year"))
            end_year = int(request.form.get("end_year"))
            start_month = int(request.form.get("start_month"))
            end_month = int(request.form.get("end_month"))
            target_days = request.form.getlist("target_days")

            print(f"▶ 開始年: {start_year}, 終了年: {end_year}")
            print(f"▶ 開始月: {start_month}, 終了月: {end_month}")
            print(f"▶ 対象日: {target_days}")

            all_data = []

            for year in range(start_year, end_year + 1):
                for month in range(start_month, end_month + 1):
                    for day in target_days:
                        filename = f"data/aim_{year}{month:02}{day}.csv"
                        if os.path.exists(filename):
                            df = pd.read_csv(filename)
                            all_data.append(df)
                        else:
                            print(f"⚠ ファイルが見つかりません: {filename}")

            if all_data:
                df_all = pd.concat(all_data, ignore_index=True)
                df_all["G数"] = pd.to_numeric(df_all["G数"], errors="coerce")
                df_all["BB"] = pd.to_numeric(df_all["BB"], errors="coerce")
                df_all["RB"] = pd.to_numeric(df_all["RB"], errors="coerce")

                agg = df_all.groupby("台番")[["G数", "BB", "RB"]].sum().reset_index()
                agg["BB率_avg"] = agg.apply(lambda row: f"1/{int(row['G数']/row['BB'])}" if row["BB"] > 0 else "-", axis=1)
                agg["RB率_avg"] = agg.apply(lambda row: f"1/{int(row['G数']/row['RB'])}" if row["RB"] > 0 else "-", axis=1)

                result = agg.sort_values("台番").reset_index(drop=True)

                # ソート用（RB率が高い順）
                rb_sort_df = agg[agg["RB"] > 0].copy()
                rb_sort_df["RB率数値"] = rb_sort_df["G数"] / rb_sort_df["RB"]
                result_sorted = rb_sort_df.sort_values("RB率数値").drop(columns=["RB率数値"]).reset_index(drop=True)
            else:
                error = "指定されたCSVファイルが見つかりませんでした。"

        except Exception as e:
            error = f"エラーが発生しました: {e}"
            print("❌ エラー詳細:", e)

    return render_template("index.html", result=result, result_sorted=result_sorted, error=error)

# Render用：ホストとポートを指定
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
