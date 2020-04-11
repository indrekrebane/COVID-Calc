import numpy as np
import colorcet as cc
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, CheckboxGroup
from bokeh.plotting import figure
from datetime import date
import csv

population = {}
plotted = set()
plottimeline = {}
plotcont = {}

# Read JHU data
def readJHU(datatype):
    COVdata={}
    with open('JHU\\csse_covid_19_data\\csse_covid_19_time_series\\time_series_covid19_'+datatype+'_global.csv',newline='') as csvfile:
        CSVReader = csv.reader(csvfile, delimiter=',')
        header=next(CSVReader)[4:]
        for urow in CSVReader:
            population[urow[1]]=0
            if urow[1] not in COVdata:
                COVdata[urow[1]]=urow[4:]
            else:
                COVdata[urow[1]]=list(map(lambda x,y: int(x)+int(y),urow[4:], COVdata[urow[1]]))
    return header, COVdata

COV_conf_h, COV_conf = readJHU('confirmed')
COV_rec_h, COV_rec = readJHU('recovered')
COV_ded_h, COV_ded = readJHU('deaths')

#print(COV_conf_h, COV_rec_h, COV_ded_h)

with open('Population.csv',newline='') as csvfile:
    CSVReader = csv.reader(csvfile, delimiter=';')

    for urow in CSVReader:
        if urow[0] in population:
            population[urow[0]]=urow[1]

for country, pop in population.items():
    if pop == 0:
        print(country)

COV_active = {}
COV_delta = {}
COV_last14 = {}
COV_apop = {}


for name in population:
    COV_active[name]=list(map(lambda x,y,z: int(x)-int(y)-int(z),COV_conf[name],COV_ded[name],COV_rec[name]))
    COV_delta[name]=[]
    COV_last14[name]=[]
    if population[name]==0:
        print(population[name],name)
    COV_apop[name]=list(map(lambda x: int(x)/int(population[name]),COV_active[name]))

    for i in range(len(COV_active[name])):
        if i==0:
            COV_delta[name].append(COV_active[name][i])
        else:
            COV_delta[name].append(COV_active[name][i]-COV_active[name][i-1])
    for i in range(len(COV_active[name])):
        if COV_active[name][i] == 0:
            COV_last14[name].append(0)
            continue
        if i<14:
            COV_last14[name].append(sum(COV_delta[name][:i])/COV_active[name][i])
        else:
            COV_last14[name].append(sum(COV_delta[name][i-14:i])/COV_active[name][i])


a=[]
for i in COV_conf_h:
    b=i.split('/')
    a.append(date(int(b[2])+2000,int(b[0]),int(b[1])))

plottimeline['Date'] = np.array(a, dtype=np.datetime64)

source = ColumnDataSource(data=plottimeline)


#hover = HoverTool(tooltips=[("name", "@$name"), ("q", "$y"), ("Date", "@Date")])
#plot_dateline.hover.tooltips=[("name", "@$name")]
#plot_dateline.hover.mode='vline'


# Set up plot
plot_dateline = figure(x_axis_type='datetime', y_axis_type='log', y_range=[100,10**9], plot_height=800, plot_width=800, title="My test",
              tools="crosshair,pan,reset,save,box_zoom,wheel_zoom")

source2 = ColumnDataSource(data=plotcont)
plot_cont = figure(x_axis_type='log', y_axis_type='log', plot_height=800, plot_width=800, title="My test",
              tools="crosshair,pan,reset,save,box_zoom,wheel_zoom")



palette = [cc.glasbey_dark[i] for i in range(255)]

# Set up widgets
checkbox = CheckboxGroup(labels=list(population))

def add_contmap(name):
    plotcont[name+'_a'] = COV_apop[name]
    plotcont[name+'_t'] = COV_last14[name]
    source2.data = plotcont
    plot_cont.line(name+'_a', name+'_t', source=source2, line_width=3, line_alpha=0.6, color=palette[len(checkbox.active)], name=name, legend_label=name)

def add_dateline(name):
    plottimeline[name] = COV_conf[name]
    # plottimeline[name+' A'] = list(map(lambda x,y,z: int(x)-int(y)-int(z),COV_conf[name],COV_ded[name],COV_rec[name]))
    source.data = plottimeline
    plot_dateline.line('Date', name, source=source, line_width=3, line_alpha=0.6, color=palette[len(checkbox.active)], name=name, legend_label=name)
    # plot_dateline.line('Date', name+' A', source=source, line_width=2, line_alpha=0.6, tags=[name])

def del_dateline(name):
    #line=plot_dateline.select_one({'name': name})
    #print(line)
    #plot_dateline.renderers.remove(line)
    # line=plot_dateline.select_one(name)
    # plot_dateline.renderers.remove(line)
    return

# Set up callbacks
def update_country(new):
    for c in new:
        if c not in plotted:
            add_dateline(checkbox.labels[c])
            add_contmap(checkbox.labels[c])
            print('+', checkbox.labels[c])
            plotted.add(c)
            # print(COV_conf[checkbox.labels[c]], COV_rec[checkbox.labels[c]], COV_ded[checkbox.labels[c]])
    for c in plotted.copy():
        if c not in new:
            print('-', checkbox.labels[c])
            del_dateline(checkbox.labels[c])
            plotted.remove(c)

checkbox.on_click(update_country)

# Set up layouts and add to document
inputs = column(checkbox)

curdoc().add_root(row(inputs,column(plot_dateline,plot_cont)))
curdoc().title = "Plot"