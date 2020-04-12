import numpy as np
import colorcet as cc
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Button, CheckboxGroup, HoverTool, RadioButtonGroup
from bokeh.plotting import figure
from datetime import date
import csv

population = {}
plotted = set()
plottimeline = {}
plotcont = {}

default_countries = ['Estonia', 'US', 'Finland', 'China', 'Latvia', 'Lithuania', 'United Kingdom', 'Germany', 'Italy', 'Spain', 'Turkey', 'Norway', 'France', 'Korea, South']

# Read JHU data
def readJHU(datatype):
    COVdata={}
    with open('JHU\\csse_covid_19_data\\csse_covid_19_time_series\\time_series_covid19_'+datatype+'_global.csv',newline='') as csvfile:
        CSVReader = csv.reader(csvfile, delimiter=',')
        header=next(CSVReader)[4:]
        for urow in CSVReader:
            population[urow[1]]=0
            if urow[1] not in COVdata:
                COVdata[urow[1]]=[int(i) for i in urow[4:]]
            else:
                COVdata[urow[1]]=list(map(lambda x,y: int(x)+y,urow[4:], COVdata[urow[1]]))
    return header, COVdata

COV_conf_h, COV_conf = readJHU('confirmed')
COV_rec_h, COV_rec = readJHU('recovered')
COV_ded_h, COV_ded = readJHU('deaths')

#print(COV_conf_h, COV_rec_h, COV_ded_h)

# Filter out countries with lower number of confirmed cases
for name in COV_conf:
    if int(max(COV_conf[name]))<100:
        del population[name]


with open('Population.csv',newline='') as csvfile:
    CSVReader = csv.reader(csvfile, delimiter=';')
    # next(CSVReader)
    for urow in CSVReader:
        if urow[0] in population:
            population[urow[0]]=int(urow[1])

for country, pop in population.items():
    if pop == 0:
        print(country)

COV_active = {}
COV_delta = {}
COV_last14 = {}
COV_apop = {}


for name in population:
    COV_active[name]=list(map(lambda x,y,z: x-y-z,COV_conf[name],COV_ded[name],COV_rec[name]))
    COV_delta[name]=[]
    COV_last14[name]=[]
    if population[name]==0:
        print('population 0: ' + name + ' ' + population[name])
    COV_apop[name]=list(map(lambda x: x/population[name],COV_active[name]))

    a_old=0
    for i,a in enumerate(COV_conf[name]):
            COV_delta[name].append(a-a_old)
            a_old=a

    a_old=0
    for i,a in enumerate(COV_active[name]):
            if a < 100: # zero out cont stats for < hundred cases
                COV_last14[name].append(0)
            elif i<14:
                COV_last14[name].append(sum(COV_delta[name][:i])/a)
            else:
                COV_last14[name].append(sum(COV_delta[name][i-14:i])/a)
            a_old=a

plottimeline['Dates']=[]
a=[]
for i in COV_conf_h:
    b=i.split('/')
    a.append(date(int(b[2])+2000,int(b[0]),int(b[1])))
    plottimeline['Dates'].append('20'+b[2]+'-'+b[0]+'-'+b[1])

plottimeline['Date'] = np.array(a, dtype=np.datetime64)

palette = [cc.glasbey_dark[i] for i in range(255)]

# Set up widgets

# Enable default countries
a=[]
for i,name in enumerate(list(population)):
    if name in default_countries:
        a.append(i)
checkbox = CheckboxGroup(labels=list(population), active=a)
btn_clear = Button(label="Clear", button_type="success")
radio_main = RadioButtonGroup(labels=["Conf", "Recov", "Dead", "Active", "aPop"], active=0)

# test data
# name='Estonia'
# print(list(zip(COV_active[name],COV_last14[name])))
# print(COV_conf[name])

def plot_t():
    source = ColumnDataSource(data=plottimeline)
    # Set up plot
    plot = figure(x_axis_type='datetime', y_axis_type='log', plot_height=800, plot_width=800, title="My test",
                  tools="crosshair,pan,reset,save,box_zoom,wheel_zoom")
    active_plot = radio_main.labels[radio_main.active]

    for i,n in enumerate(checkbox.active):
        name=checkbox.labels[n]
        if active_plot == "Active":
            plottimeline[name] = COV_active[name]
        elif active_plot == "Recov":
            plottimeline[name] = COV_rec[name]
        elif active_plot == "Dead":
            plottimeline[name] = COV_ded[name]
        elif active_plot == "aPop":
            plottimeline[name] = COV_apop[name]            
        else:
            plottimeline[name] = COV_conf[name]
        source.data = plottimeline
        plot.line('Date', name, source=source, line_width=3, line_alpha=0.6, color=palette[n], name=name, legend_label=name)
    plot.add_tools(HoverTool(tooltips=[('', "$name"),('',"(@Dates, $y)")]))
    plot.legend.click_policy="hide"
    plot.legend.location='top_left'
    return plot

def plot_c():
    source = ColumnDataSource(data=plotcont)
    plot = figure(x_axis_type='log', y_axis_type='linear', plot_height=800, plot_width=800, title="plotcont",
                  tools="crosshair,pan,reset,save,box_zoom,wheel_zoom")
    for i,n in enumerate(checkbox.active):
        name=checkbox.labels[n]
        plotcont[name+'_a'] = COV_apop[name]
        plotcont[name+'_t'] = COV_last14[name]
        source.data = plotcont
        plot.line(name+'_a', name+'_t', source=source, line_width=3, line_alpha=0.6, color=palette[n], name=name, legend_label=name)

    plot.add_tools(HoverTool(tooltips=[('', "$name"),('',"($x, $y)")]))
    plot.legend.click_policy="hide"
    plot.legend.location='top_left'
    return plot

# def add_contmap(name):
#     plotcont[name+'_a'] = COV_apop[name]
#     plotcont[name+'_t'] = COV_last14[name]
#     source2.data = plotcont
#     plot_cont.line(name+'_a', name+'_t', source=source2, line_width=3, line_alpha=0.6, color=palette[len(checkbox.active)], name=name, legend_label=name)

# def add_dateline(name):
#     plottimeline[name] = COV_conf[name]
#     # plottimeline[name+' A'] = list(map(lambda x,y,z: int(x)-int(y)-int(z),COV_conf[name],COV_ded[name],COV_rec[name]))
#     source.data = plottimeline
#     plot_dateline.line('Date', name, source=source, line_width=3, line_alpha=0.6, color=palette[len(checkbox.active)], name=name, legend_label=name)
#     # plot_dateline.line('Date', name+' A', source=source, line_width=2, line_alpha=0.6, tags=[name])

# def del_dateline(name):
#     #line=plot_dateline.select_one({'name': name})
#     #print(line)
#     #plot_dateline.renderers.remove(line)
#     # line=plot_dateline.select_one(name)
#     # plot_dateline.renderers.remove(line)
#     return

# Set up callbacks
def update_country(new):
    for c in new:
        if c not in plotted:
            # add_dateline(checkbox.labels[c])
            # add_contmap(checkbox.labels[c])
            print('+', checkbox.labels[c])
            plotted.add(c)
            # print(COV_conf[checkbox.labels[c]], COV_rec[checkbox.labels[c]], COV_ded[checkbox.labels[c]])
    for c in plotted.copy():
        if c not in new:
            print('-', checkbox.labels[c])
            # del_dateline(checkbox.labels[c])
            plotted.remove(c)
    layout.children[1].children=[plot_t(), plot_c()]

def clearplot():
    checkbox.active=[]

def radiomain(new):
    layout.children[1].children[0]=plot_t()

checkbox.on_click(update_country)
btn_clear.on_click(clearplot)
radio_main.on_click(radiomain)

# Set up layouts and add to document
inputs = column(btn_clear, radio_main, checkbox)
outputs = column(plot_t(),plot_c())
layout = row(inputs,outputs)
curdoc().add_root(layout)
curdoc().title = "Plot"