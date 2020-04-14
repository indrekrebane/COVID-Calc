import numpy as np
import math
import colorcet as cc
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Button, CheckboxButtonGroup
from bokeh.models import CheckboxGroup, HoverTool, RadioButtonGroup, Slider
from bokeh.plotting import figure
from datetime import date
import csv

population = {}
plotted = set()
plottimeline = {}
plotcont = {}
c_period = 7
window=[3,5,10,5]
window=[float(i)/sum(window) for i in window]
#sick_time_avg = 21

# default_countries = ['Estonia', 'US', 'Finland', 'China', 'Latvia', 'Lithuania', 'United Kingdom', 'Germany', 'Italy', 'Spain', 'Turkey', 'Norway', 'France', 'Korea, South']
#default_countries = ['World', 'Estonia', 'Finland', 'US', 'China']
default_countries = ['Estonia', 'Belgium']

# Read JHU data
def readJHU(datatype):
    COVdata={}
    with open('JHU\\csse_covid_19_data\\csse_covid_19_time_series\\time_series_covid19_'+datatype+'_global.csv',newline='') as csvfile:
        CSVReader = csv.reader(csvfile, delimiter=',')
        header=next(CSVReader)[4:]
        COVdata['World']=[0 for i in header]
        population['World']=0
        for urow in CSVReader:
            population[urow[1]]=0
            if urow[1] not in COVdata:
                COVdata[urow[1]]=[int(i) for i in urow[4:]]
            else:
                COVdata[urow[1]]=list(map(lambda x,y: int(x)+y,urow[4:], COVdata[urow[1]]))
            COVdata['World']=list(map(lambda x,y: int(x)+y,urow[4:], COVdata['World']))
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
# COV_activeP = {}
COV_delta = {}
COV_lastP = {}
COV_apop = {}
# COV_apopP = {}
# COV_recP = {}


for name in population:
    COV_active[name]=list(map(lambda x,y,z: x-y-z,COV_conf[name],COV_ded[name],COV_rec[name]))
    COV_delta[name]=[]
    # COV_recP[name]=[]
    # Any new countries added that do not have population match?
    if population[name]==0:
        print('population 0: ' + name + ' ' + population[name])
    COV_apop[name]=list(map(lambda x: x/population[name],COV_active[name]))

    a_old=0
    for i,a in enumerate(COV_conf[name]):
            COV_delta[name].append(int(a)-int(a_old))
            # Predict active cases
            # if i<sick_time_avg:
            #     COV_recP[name].append(0)
            # else:
            #     COV_recP[name].append(COV_recP[name][i-1]+COV_delta[name][i-sick_time_avg]-(COV_ded[name][i]-COV_ded[name][i-1]))
            a_old=a
    # COV_activeP[name]=list(map(lambda x,y,z: x-y-z,COV_conf[name],COV_ded[name],COV_recP[name]))
    # COV_apopP[name]=list(map(lambda x: x/population[name],COV_activeP[name]))

def calc_lastP(period):
    for name in population:
        COV_lastP[name]=[]
        a_old=0
        for i,a in enumerate(COV_active[name]):
            if a < 100: # zero out cont stats for < 100 cases
                COV_lastP[name].append(0)
            elif i<(len(COV_active[name])-period):
                COV_lastP[name].append(sum(map(lambda x, y: x*y,COV_delta[name][i+period-len(window):i+period],window))/a)
            else: # last cases are misrepresenting
                COV_lastP[name].append(0)
            a_old=a

calc_lastP(c_period)

# print('c',COV_conf['Belgium'])
# print('d',COV_delta['Belgium'])
# print('a',COV_active['Belgium'])
# print('ap',COV_apop['Belgium'])
# print('l',COV_lastP['Belgium'])

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
btn_clear = Button(label="Clear countries", button_type="success")
btng_main = CheckboxButtonGroup(labels=[ "Active", "Conf", "Recov", "Dead", "aPop"], active=[0])
slide_c_period = Slider(start=len(window), end=14, value=(c_period), step=1, title="Cont. period")

# test data
# name='Estonia'
# print(list(zip(COV_active[name],COV_lastP[name])))
# print(COV_conf[name])

def plot_t():
    source = ColumnDataSource(data=plottimeline)
    # Set up plot
    plot = figure(x_axis_type='datetime', y_axis_type='log', plot_height=800, plot_width=1600, title="My test",
                  tools="crosshair,pan,reset,save,box_zoom,wheel_zoom")

    active_plot=[btng_main.labels[i] for i in btng_main.active]

    for i,n in enumerate(checkbox.active):
        name=checkbox.labels[n]
        if "Active" in active_plot:
            if name+'_act' not in plottimeline:
                plottimeline[name+'_act'] = COV_active[name]
            plot.line('Date', name+'_act', source=plottimeline, line_width=3, line_alpha=0.6, line_dash='solid', color=palette[n], name=name+'_act', legend_label=name)
        if "Recov" in active_plot:
            if name+'_rec' not in plottimeline:
                plottimeline[name+'_rec'] = COV_rec[name]
            plot.line('Date', name+'_rec', source=plottimeline, line_width=2, line_alpha=0.6, line_dash='dashed', color=palette[n], name=name+'_rec', legend_label=name)
        if "Dead" in active_plot:
            if name+'_ded' not in plottimeline:
                plottimeline[name+'_ded'] = COV_ded[name]
            plot.line('Date', name+'_ded', source=plottimeline, line_width=2, line_alpha=0.6, line_dash='dotted', color=palette[n], name=name+'_ded', legend_label=name)
        if "aPop" in active_plot:
            if name+'_aPop' not in plottimeline:
                plottimeline[name+'_aPop'] = COV_apop[name]
            plot.line('Date', name+'_aPop', source=plottimeline, line_width=1, line_alpha=0.6, line_dash='solid', color=palette[n], name=name+'_aPop', legend_label=name)
        if "Conf" in active_plot:
            if name not in plottimeline:
                plottimeline[name] = COV_conf[name]
            plot.line('Date', name, source=plottimeline, line_width=2, line_alpha=0.6, line_dash='dotdash', color=palette[n], name=name, legend_label=name)
    plot.add_tools(HoverTool(tooltips=[('', "$name"),('',"(@Dates, @$name)")]))
    plot.legend.click_policy="hide"
    plot.legend.location='top_left'
    return plot

def plot_c():
    source = ColumnDataSource(data=plotcont)
    plot = figure(x_axis_type='log', y_axis_type='linear', 
                  x_range=(10**-6, 10**-2), #y_range=(0,5), 
                  plot_height=800, plot_width=1600, title="plotcont",
                  tools="crosshair,pan,reset,save,box_zoom,wheel_zoom")
    for i,n in enumerate(checkbox.active):
        name=checkbox.labels[n]
        if name+'_aPop' not in plottimeline:
            plottimeline[name+'_aPop'] = COV_apop[name]
        # if name+'_aPopP' not in plottimeline:
        #     plottimeline[name+'_aPopP'] = COV_apopP[name]
        if name+'_lastP' not in plottimeline:
            plottimeline[name+'_lastP'] = [float('NaN') if x==0 else x for x in COV_lastP[name]]
        # if name+'_actP' not in plottimeline:
            # plottimeline[name+'_actP'] = COV_activeP[name]
        plot.line(name+'_aPop', name+'_lastP', source=plottimeline, line_width=2, line_alpha=0.6, color=palette[n], name=name+'_lastP', legend_label=name)
        # plot.line(name+'_aPop', name+'_aPopP', source=plottimeline, line_width=2, line_alpha=0.6, color=palette[n], name=name+'_actP', legend_label=name)

    plot.add_tools(HoverTool(tooltips=[('', "$name,@Dates"),('',"($x, @$name)")]))
    plot.legend.click_policy="hide"
    plot.legend.location='top_left'
    return plot

# def add_contmap(name):
#     plotcont[name+'_a'] = COV_apop[name]
#     plotcont[name+'_t'] = COV_lastP[name]
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

def clearcountries():
    checkbox.active=[]

def plottype_handler(new):
    layout.children[1].children[0]=plot_t()

def c_period_handler(attr, old, new):
    calc_lastP(int(new))
    for country, pop in population.items():
        if country+'_lastP' in plottimeline:
            del plottimeline[country+'_lastP']
    layout.children[1].children[1]=plot_c()

checkbox.on_click(update_country)
btn_clear.on_click(clearcountries)
btng_main.on_click(plottype_handler)
slide_c_period.on_change('value', c_period_handler)

# Set up layouts and add to document
inputs = column(btng_main, slide_c_period, btn_clear, checkbox)
outputs = column(plot_t(),plot_c())
layout = row(inputs,outputs)
curdoc().add_root(layout)
curdoc().title = "Plot"