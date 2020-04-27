import matplotlib.pyplot as plt
import csv

def plot_all(result):
    B, msid_list, date_list = result.sum_hours()

    with open('test.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for x in range(len(B[:,1])):
            writer.writerow([msid_list[x],str(B[x,:])])

