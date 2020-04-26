import matplotlib.pyplot as plt


def plot_all(result):
    B, msid_list, date_list = result.sum_hours()
    plt.bar(len(date_list), B[1,:])
    plt.show()

