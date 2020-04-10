import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, CheckboxGroup
from bokeh.plotting import figure

import csv

population = {}
plotted = set()

# Read JHU data
def readJHU(datatype):
    COVdata=[]
    sumindex = {}
    with open('JHU\\csse_covid_19_data\\csse_covid_19_time_series\\time_series_covid19_'+datatype+'_global.csv',newline='') as csvfile:
        CSVReader = csv.reader(csvfile, delimiter=',')
        next(CSVReader)
        for urow in CSVReader:
            population[urow[1]]=0
            if urow[1] not in sumindex:
                COVdata.append([urow[1]]+urow[4:])
                sumindex[urow[1]] = len(COVdata)-1
            else:
                COVdata[sumindex[urow[1]]][1:]=list(map(lambda x,y: int(x)+int(y),urow[4:], COVdata[sumindex[urow[1]]][1:]))
#            print(COV_conf[sumindex[urow[1]]])
    return COVdata

COV_conf = readJHU('confirmed')
COV_rec = readJHU('recovered')
COV_ded = readJHU('deaths')

#with open('JHU\\csse_covid_19_data\\csse_covid_19_time_series\\time_series_covid19_recovered_global.csv',newline='') as csvfile:
#     CSVReader = csv.reader(csvfile, delimiter=',')
#     next(CSVReader)

# with open('JHU\\csse_covid_19_data\\csse_covid_19_time_series\\time_series_covid19_deaths_global.csv',newline='') as csvfile:
#     CSVReader = csv.reader(csvfile, delimiter=',')
#     next(CSVReader)   

with open('Population.csv',newline='') as csvfile:
    CSVReader = csv.reader(csvfile, delimiter=';')

    for urow in CSVReader:
        if urow[0] in population:
            population[urow[0]]=urow[1]

for country, pop in population.items():
    if pop == 0:
        print(country)

# Set up data
N = 200
x = np.linspace(0, 4*np.pi, N)
y = np.sin(x)
source = ColumnDataSource(data=dict(x=x, y=y))

# Set up plot
plot = figure(plot_height=800, plot_width=800, title="my sine wave",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[0, 4*np.pi], y_range=[-2.5, 2.5])

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

# Set up widgets
checkbox = CheckboxGroup(labels=list(population))



# Set up callbacks
def update_country(new):
    for c in new:
        if c not in plotted:
            print('+', checkbox.labels[c])
            plotted.add(c)
            for data in COV_conf, COV_rec, COV_ded:
                for i in data:
                    if i[0] == checkbox.labels[c]:
                        print(i)
                        break
    for c in plotted.copy():
        if c not in new:
            print('-', checkbox.labels[c])
            plotted.remove(c)

checkbox.on_click(update_country)

# Set up layouts and add to document
inputs = column(checkbox)

curdoc().add_root(row(inputs,plot))
curdoc().title = "Plot"