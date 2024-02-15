import matplotlib.pyplot as plt
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA


def arima(df, column_name):
    df["date"] = df.iloc[:, 0]
    df = df[[column_name, "date"]]
    df.set_index("date", inplace=True)

    # 可視化
    # df.plot()
    # plt.show()

    # ADF検定（原系列）定常過程かどうかを検定する
    dftest = adfuller(df)
    # print('ADF Statistic: %f' % dftest[0])
    print("p-value: %f" % dftest[1])
    # print('Critical values :')
    # for k, v in dftest[4].items():
    #    print('\t', k, v)

    # プログラムのURL:https://toukei-lab.com/python_stock
    if dftest[1] <= 0.05:
        print("p-value <= 0.05")
        print("データは定常過程です")
    else:
        print("データは定常過程ではありません")
        # ARIMAモデル データ準備
        train_data, test_data = df[0 : int(len(df) * 0.7)], df[int(len(df) * 0.7) :]
        train_data = train_data[column_name].values
        test_data = test_data[column_name].values

        # ARIMAモデル実装
        # train_data = df["close"].values
        model = ARIMA(train_data, order=(6, 1, 0))
        model_fit = model.fit()
        print(model_fit.summary())

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
        fig, axs = plt.subplots()

        # 実測値の描画
        axs.plot(test_data, color="Red", label="Measured")
        # 予測値の描画
        axs.plot(model_predictions, color="Blue", label="Prediction")
        axs.set_title(" ARIMA model", fontname="MS Gothic")
        axs.set_xlabel("Date", fontname="MS Gothic")
        axs.set_ylabel("Amazon stock price", fontname="MS Gothic")
        axs.legend(prop={"family": "MS Gothic"})

        axs.set_title("Prediction", fontname="MS Gothic")

        return fig
