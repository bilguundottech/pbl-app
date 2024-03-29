# ARIMAモデル

import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA


def arima(original_df, column_name):
    df = original_df.copy()
    xlabel_name = df.columns[0]
    if xlabel_name == "年":  # 年ごとのデータの場合
        xlabel_name = "Year"
        df["index"] = pd.to_datetime(df.iloc[:, 0], format="%Y")  # 2000->2000-01-01

    elif xlabel_name == "date":  # 1日ごとの場合
        xlabel_name = "date"
        df["index"] = pd.to_datetime(df["date"])

    df.set_index("index", inplace=True)
    data = df[column_name].dropna()  # NaNの行を削除

    # ADF検定（原系列）定常過程かどうかを検定する
    dftest = adfuller(data)
    # print('ADF Statistic: %f' % dftest[0])
    print("p-value: %f" % dftest[1])

    if dftest[1] <= 0.05:
        msg = "The selected data set is a stationary process. Please select another analysis method. "
        fig = None
    else:
        # print("データは定常過程ではありません")
        # ARIMAモデル データ準備
        train_data, test_data = (
            data[0 : int(len(data) * 0.7)],
            data[int(len(data) * 0.7) :],
        )
        train_data = train_data.values
        test_data = test_data.values

        # ARIMAモデル実装
        # train_data = data["close"].values
        model = ARIMA(train_data, order=(6, 1, 0))
        model_fit = model.fit()
        # print(model_fit.summary())

        # ARIMAモデル 予測
        history = [x for x in train_data]
        model_predictions = []

        for time_point in range(len(test_data)):
            # ARIMAモデル 実装
            model = ARIMA(history, order=(6, 1, 0))
            model_fit = model.fit()
            # 予測データの出力
            output = model_fit.forecast()
            yhat = output[0]
            model_predictions.append(yhat)
            # トレーニングデータの取り込み
            true_test_value = test_data[time_point]
            history.append(true_test_value)

        # サブプロットの設定
        fig, axs = plt.subplots(figsize=(10, 6))

        pd.Series(test_data).plot(color="Red", label="Measured")
        # 予測値の描画
        pd.Series(model_predictions).plot(color="Blue", label="Prediction")
        axs.set_title("ARIMA model")
        axs.set_xlabel(xlabel_name, fontname="MS Gothic")
        # axs.set_ylabel("Stock Price")
        axs.legend(prop={"family": "MS Gothic"})
        msg = "Successfully predicted the future value using the ARIMA model."
    return fig, msg
