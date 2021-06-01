import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX


def read_data():
    """
    Read January data and put in dictionary indexed by date


    Returns
    -------
        data : dict
            dictionary with cases indexed by date
    """
    data = {}
    with open("../data/data_all_cleaned.csv") as f:
        f.readline()
        for line in f.readlines():
            line = line.split(",")
            date = line[0]
            if date in data:
                data[date].append([float(line[1]), float(line[2])])
            else:
                data[date] = [[float(line[1]), float(line[2])]]
    return data


def reformat_data():
    """
    Returns array with number of cases per day

    Returns
    -------
        cases : list
            number of cases per day
    """
    data = read_data()
    cases = []
    for date in data:
        cases_date = len(data[date])
        cases.append(cases_date)

    cases = np.asarray(cases)

    return cases


def get_real(days):
    """
    Read real data of February

    Parameters
    ----------
        days : int
            number of days for which to get data

    Returns
    -------
        values : numpy array
            Real number of cases per day for given days
    """
    data = pd.read_csv("../data/february.csv", sep=";")

    by_date = {}

    for date, case in zip(data["DATE"], data["CASES"]):
        if date not in by_date:
            by_date[date] = 0

        if case == "<5":
            by_date[date] += 3
        else:
            by_date[date] += int(case)

    print(by_date)
    values = []
    for i in range(1, days+1):
        if i <= 9:
            date = f"2021-02-0{i}"
        else:
            date = f"2021-02-{i}"
        values.append(by_date[date])
    return np.asarray(values)


def predict():
    """
    Predict February data based on January using SARIMA
    """
    cases = reformat_data()
    # 7 is the seasonality in data (here in days)
    # Other parameters found by experimentation
    model = SARIMAX(endog=cases, order=(2, 0, 1), seasonal_order=(0,1,0,7), trend='n')
    fit = model.fit()

    # Forecast for 2 weeks
    prediction = fit.forecast(14)

    # Get real data
    real = get_real(14)
    print(prediction)

    # Plot history, predictions, and real data
    t1 = np.arange(1, 32)
    t2 = np.arange(32, 32+14)
    plt.figure()
    plt.plot(t1, cases, 'tab:blue', label="January")
    plt.xlabel("Days elapsed since 01/01/2021")
    plt.ylabel("Number of new cases in Brussels")
    plt.plot(t2, prediction, 'tab:red', label="February prediction")
    plt.plot(t2, real, 'tab:green', label="February real")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    predict()
