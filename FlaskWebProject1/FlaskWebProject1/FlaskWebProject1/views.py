"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from flask import request
from FlaskWebProject1 import app
from flask import Markup, url_for

import pandas as pd
import random
import plotly
import plotly.graph_objs as go
from plotly import tools
import names

from chart_studio import plotly as py
from plotly.offline import iplot,init_notebook_mode

#pd.set_option('display.max_rows',None)
#pd.set_option('display.max_columns',None)

#数据导入与显示
df_output = pd.read_excel('D:\data\data\data\output1.xlsx')
df_story = pd.read_excel('D:\data\data\data\story1.xlsx')
df_sprint = pd.read_excel('D:\data\data\data\sprint数据1.xlsx')
df_reject = pd.read_excel('D:\data\data\data\w5-w6提测驳回1.xlsx')
df_commit = pd.read_json('D:\data\data\data\djiops_repo_commits.json')
df_merge = pd.read_json('D:\data\data\data\djiops_repo_merge_request.json')

#Variables 1 提交的stories数量

#提交过stories的人(去重)
name = []
for i in df_story["author_name"]:
    if not i in name:
        name.append(i)
total_stories = sum(df_story["author_name"].value_counts())
        
#First Variable dataframe
df_variable1 = df_story["author_name"].value_counts()

#Variables 2 驳回率

#每人被驳回次数

rejection_index1=[] #被驳回1次
rejection_index2=[] #被驳回2次
personnel=[]
dict1= {}

#获得被驳回stories条目索引
df = df_sprint["被驳回次数"]
for i in df[df.values == 1].index:
    rejection_index1.append(i)

for i in df[df.values == 2].index:
    rejection_index2.append(i)

#根据索引获得该stories经办人以及该经办人被驳回次数
for index in rejection_index1:
     personnel.append(df_sprint.iloc[index]["经办人"])

for index in rejection_index2:
     personnel.append(df_sprint.iloc[index]["经办人"])
     personnel.append(df_sprint.iloc[index]["经办人"])
    

for key in personnel:
    dict1[key] = dict1.get(key, 0) + 1
    
#计算驳回率 驳回次数/提交sotries数
per = []
person_name = []
reject_num = len(personnel)
personnel = list(set(personnel))
for person in personnel:
    if person in name:
        percentage = dict1[person]/df_story["author_name"].value_counts()[person]
        person_name.append(person)
        per.append(percentage)
        
output= {"经办人":person_name,"驳回率(%)":per}   
data = pd.DataFrame(output)

#删去驳回率>=1
d = data["驳回率(%)"]
    
data_clear = data.drop(d[d.values>=1].index)
final = data_clear.reset_index(drop=True)
final = final.round(3)
final.set_index(["经办人"], inplace=True)
final = final['驳回率(%)']*100

#Second Variable dataframe
df_variable2 = final

#Variable3 集成失败率
#total merge request
request_l = []
request_dict = {}

for i in range(len(df_merge)):
    request_l.append(df_merge.iloc[i]['author']['username'])
    
for key in request_l:
    request_dict[key] = request_dict.get(key, 0) + 1

#建立dataframe
merge_df = pd.DataFrame.from_dict(request_dict, orient='index')
merge_df = merge_df.sort_values(by=[0],ascending=False)
merge_df = merge_df.rename(columns={0:'Total_merge_request'})

#获得status异常的index（146个）
index = []

for status in df_merge['merge_status']:
    if status != 'can_be_merged':
        for i in df_merge['merge_status'][df_merge['merge_status'] == status].index:
            index.append(i)

index = list(set(index))
index.sort()

#获取经办人
name = []
name_dict={}

for i in index:
    name.append(df_merge.iloc[i]['author']['username'])
    
for key in name:
    name_dict[key] = name_dict.get(key, 0) + 1

#建立dataframe
new_df = pd.DataFrame.from_dict(name_dict, orient='index')
new_df = new_df.sort_values(by=[0],ascending=False)
new_df = new_df.rename(columns={0:'Invalid_merge_request'})
new_df.head()

#合并
final_df = pd.concat([merge_df,new_df],axis=1,sort=True)
final_df = final_df.sort_values(by=['Invalid_merge_request'],ascending=False)
final_df = final_df.fillna(0)

#计算merged request 异常率
percentage = []

for i in range(len(final_df)):
    if final_df['Invalid_merge_request'][i] != 0:
        per = final_df['Invalid_merge_request'][i]/final_df['Total_merge_request'][i]
        
        percentage.append(per)

percentage.extend((len(final_df)-len(percentage))* [0]) #补0
percentage = [i * 100 for i in percentage]

#合并DataFrame 按异常率降序排序
final_df['Invalid_percentage(%)'] = pd.Series(percentage).values
final_df = final_df.sort_values(by=['Invalid_percentage(%)'],ascending=False)

#Third Variable dataframe
df_variable3 = final_df

#Variables4 bug率：bug数/stories数
#提交过stories的人(去重)
name = []
for i in df_story["author_name"]:
    if not i in name:
        name.append(i)


#数据处理
df_output = df_output.fillna(0)
df_output = df_output.set_index(["Ad"])
df_output = df_output.drop(columns = ['business','Unnamed: 0'])
df_output = df_output.drop_duplicates()

#计算bug率，建立dataframe
per = []
person_name = []
for person in name:
    if person in list(df_output.index):
        percentage = df_output.loc[person]['bug数']/df_story["author_name"].value_counts()[person]
        person_name.append(person)
        per.append(percentage*100)
        
output= {"AD":person_name,"bug率(%)":per}   
data = pd.DataFrame(output)
data = data.set_index('AD')

#Forth Variable dataframe
df_variable4 = data

#第一次合并
fdf = pd.concat([df_variable1,df_variable2],axis=1,sort=True)
fdf = pd.concat([fdf,df_variable3],axis=1,sort=True)
fdf = pd.concat([fdf,df_variable4],axis=1,sort=True)
fdf = fdf.rename(columns={'author_name':'Stories'})
fdf = fdf.sort_values(by=['Stories'],ascending=False)
fdf = fdf.drop(columns = ['Total_merge_request','Invalid_merge_request'])
fdf = fdf.rename(columns={'Invalid_percentage(%)':'集成失败率(%)'})
fdf = fdf.fillna(0)
fdf = fdf.round(3)

#Variable5 代码量 随机生成

#随机数组

def random_int_list(start, stop, length):
    start, stop = (int(start), int(stop)) if start <= stop else (int(stop), int(start))
    length = int(abs(length)) if length else 0
    random_list = []
    for i in range(length):
        random_list.append(random.randint(start, stop))
    return random_list

coding = random_int_list(30,300,len(fdf))

#加入dataframe
fdf['代码量']=coding

#Variable6 测试覆盖率 随机生成
coverage = random_int_list(0,100,283)
#加入dataframe
fdf['测试覆盖率']=coverage

#开始计算各项得分

#1. 测试覆盖率得分
threshold = 20
scores = []
for cover in coverage:
    if cover<=threshold:
        score = cover-threshold
        scores.append(score)
    else:
        scores.append(cover)
        
fdf['测试覆盖率得分(100)']=scores

#2. story数量及评分
threshold = 3
scores = []

for person in fdf.index:
    if fdf['Stories'][person] > threshold:
        scores.append((fdf['Stories'][person]-threshold)*2)
    else:
        scores.append(0)

fdf['Stories得分']=scores

#3. 代码量评分
#区间值
T1 = 50
T2 = 150
T3 = 250
scores = []

#区间
for code in coding:
    if code <= T1:
        score = 70
        scores.append(score)
    elif T1 < code <= T2:
        score = 70 + (50/(T2-T1))*(code-T1)
        scores.append(score)
    elif T2 < code <= T3:
        score = 120 + (30/(T3-T2))*(code-T2)
        scores.append(score)
    else:
        score = 150
        scores.append(score)

fdf['代码量得分(70-150)']=scores

#4. 驳回率评分
#区间值
T1 = 50
T2 = 25
T3 = 15
scores = []

#区间
for percentage in fdf['驳回率(%)']:
    if percentage > T1:
        score = -50
        scores.append(score)
    elif T2 < percentage <= T1:
        score = (25/(T1-T2))*(T1-percentage)-50
        scores.append(score)
    elif T3 <= percentage <= T2:
        score = (25/(T2-T3))*(T2-percentage)-25
        scores.append(score)
    else:
        score = 0
        scores.append(score)

fdf['驳回率扣分(-50)']=scores

#5. Bug率评分
#区间值
T1 = 50
T2 = 25
T3 = 15

scores = []

#区间
for percentage in fdf['bug率(%)']:
    if percentage > T1:
        score = -50
        scores.append(score)
    elif T2 < percentage <= T1:
        score = (25/(T1-T2))*(T1-percentage)-50
        scores.append(score)
    elif T3 <= percentage <= T2:
        score = (25/(T2-T3))*(T2-percentage)-25
        scores.append(score)
    else:
        score = 0
        scores.append(score)

fdf['bug率扣分(-50)']=scores
fdf['bug与驳回总扣分(-100)']=fdf['驳回率扣分(-50)']+fdf['bug率扣分(-50)']

#6. 集成失败率评分

threshold = 5
scores = []

for percentage in fdf['集成失败率(%)']:
    if percentage > threshold:
        score = -percentage/2
        scores.append(score)
        
    else:
        score = 0
        scores.append(score)

fdf['集成率扣分(-50)']=scores

#总分计算标准1
#有效代码量(基础分) + 效率得分 + 测试覆盖率得分 - bug与驳回 （- 准时率）
fdf['总得分1(%)'] = ((fdf['代码量得分(70-150)']+fdf['测试覆盖率得分(100)']+fdf['Stories得分']+
                  fdf['bug与驳回总扣分(-100)']+fdf['集成率扣分(-50)'])/(100+150+30))*100

#总分计算标准2 (0-100)
fdf['总得分2'] = (fdf['代码量得分(70-150)']+fdf['测试覆盖率得分(100)']+fdf['Stories得分']+
                  fdf['bug与驳回总扣分(-100)']+fdf['集成率扣分(-50)'])

k=100/(fdf['总得分2'].max()-fdf['总得分2'].min())


percentage_scores =[]
for score in fdf['总得分2']:
    percentage_scores.append(k*(score-fdf['总得分2'].min()))
    

fdf['总得分2(%)'] = percentage_scores
fdf=fdf.sort_values(by=['总得分2(%)'],ascending=False)
fdf = fdf.rename(columns={'总得分2(%)':'总得分(%)'})
fdf = fdf.rename(columns={'总得分2':'总得分'})
fdf = fdf.round(3)


#可视化总得分2

#饼图labels
labels=[]

for i in fdf['总得分(%)']:
    if i > 90:
        labels.append('90 < 总得分')
    elif 80<i<90:
        labels.append('80 < 总得分 < 90')
    elif 70<i<80:
        labels.append('70 < 总得分 < 80')
    elif 50<i<70:
        labels.append('50 < 总得分 < 70')
    else:
        labels.append('总得分 < 50')

fdf['labels']=labels

#整理显示数据
fdf = fdf.drop(columns=['总得分1(%)'])
fdf = fdf.round(3)

#将总得分提前
cols = list(fdf)
cols.insert(0,cols.pop(cols.index('总得分(%)')))
fdf = fdf.loc[:,cols]

name_list = []
for i in range(len(fdf)):
    name_list.append(names.get_full_name())
name_list=sorted(name_list)



def plot1():
    trace1 = go.Bar(
                    x = fdf.index,
                    y = fdf['总得分(%)'], 
                    opacity = 0.6, 
                    name = "总得分")
    fig1 = go.Figure(data = [trace1])

    trace2 = go.Scatter(
                        x = fdf.index,  
                        y = fdf['总得分(%)'], 
                        mode = "lines",  
                        name = "总得分")

    fig2 = go.Figure(data = [trace2])
    fig5 = plotly.subplots.make_subplots(rows=1, cols=2,shared_xaxes=False, 
                                shared_yaxes=True, vertical_spacing=0.1,subplot_titles=("柱状图", "折线图")) 

    fig5.update_xaxes(title_text="AD", row=1, col=1) 
    fig5.update_xaxes(title_text="AD",  row=1, col=2) 

    fig5.append_trace(trace1, 1, 1) 
    fig5.append_trace(trace2, 1, 2) 

    layout5={"title": "总得分(%)","xaxis_title": "AD","yaxis_title": "总得分(%)",'width':750 ,'height':400}
    fig5['layout'].update(layout5)
    s1 = plotly.offline.plot(fig5, include_plotlyjs=False, output_type='div')
    return s1

def plot2():
    trace3 = go.Histogram(
        x=fdf['总得分(%)'],
        opacity=0.6,
        name = "总得分(%)",)

    
    layout3 = go.Layout(barmode='overlay',
                       title='总得分区间',
                       xaxis=dict(title='总得分(%)'),
                       yaxis=dict(title='人数'),
        )

    fig3 = go.Figure(data=trace3, layout=layout3)
    s2 = plotly.offline.plot(fig3, include_plotlyjs=False, output_type='div')
    return s2   

def plot3():
    fig4= {
      "data": [
        {
          "values": list(fdf['labels'].value_counts()),
          "labels": list(fdf['labels'].value_counts().index),
          "hoverinfo":"label+percent",
          "hole": 0.3, 
          "type": "pie"
        },],
      "layout": {
            "title":"总得分区间人数", 
        }
    }
    s3 = plotly.offline.plot(fig4, include_plotlyjs=False, output_type='div')
    return s3

#Bug数显示
bug_num=[]
for person in fdf.index:
    if person in list(df_output.index):
        bug_num.append(df_output.loc[person]['bug数'])

fdf.index = name_list 
average_bug = sum(bug_num)/len(name_list)
average_bug = round(average_bug,2)
average_stories = round(total_stories/len(fdf),2)
average_rejection_rate  = reject_num/total_stories
average_merge_fail = final_df['Invalid_merge_request'].sum()/final_df['Total_merge_request'].sum()
average_scores = round(fdf['总得分(%)'].sum()/len(fdf),2)
average_loc = round(fdf['代码量'].sum()/len(fdf),2)

fdf1 = fdf.drop(columns = ['labels','驳回率扣分(-50)','bug率扣分(-50)','集成率扣分(-50)','bug与驳回总扣分(-100)','测试覆盖率得分(100)','Stories得分','代码量得分(70-150)'])
fdf2 = fdf1.reset_index()
#获取个人单项排名
def fetch_ranking(text):
    ranking = []
    for title in fdf2: #三项0%
        if title == '驳回率(%)':
            rdf = fdf2.sort_values(by=[title],ascending=True)
            rdf['counter'] = range(len(rdf))
            if list(rdf[rdf['index']==text][title])[0] == 0:
                ranking.append(1)
            else:
                ranking.append(list(rdf[rdf['index']==text]['counter'])[0] + 1)
    
        elif title == 'bug率(%)':
            rdf = fdf2.sort_values(by=[title],ascending=True)
            rdf['counter'] = range(len(rdf))
            if list(rdf[rdf['index']==text][title])[0] == 0:
                ranking.append(1)
            else:
                ranking.append(list(rdf[rdf['index']==text]['counter'])[0] + 1)
            
        elif title == '集成失败率(%)':
            rdf = fdf2.sort_values(by=[title],ascending=True)
            rdf['counter'] = range(len(rdf))
            if list(rdf[rdf['index']==text][title])[0] == 0:
                ranking.append(1)
            else:
                ranking.append(list(rdf[rdf['index']==text]['counter'])[0] + 1)
    
        else:
            rdf = fdf2.sort_values(by=[title],ascending=False)
            rdf['counter'] = range(len(rdf))
            ranking.append(list(rdf[rdf['index']==text]['counter'])[0] + 1)

    return ranking

#建立个人df
def create_person_df(text):
    person_df = pd.DataFrame(fdf1.loc[text])
    ranking = fetch_ranking(text)
    person_df['排名'] = ranking[1:]
    return person_df

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    #获得表扬名单
    index_name_list=[]
    index_value_list=[]
    for column in ['总得分','Stories','代码量']:
        fdf[column]
        scores_argmax = fdf[fdf[column] == fdf[column].max()].index
        index_name_list.append(scores_argmax[0])
        index_value_list.append(fdf[column][scores_argmax[0]])

    return render_template(
        'index.html',
        average_bug = average_bug,
        average_stories= average_stories,
        average_rejection_rate = round(average_rejection_rate*100,2),
        average_merge_fail=round(average_merge_fail*100,2),
        average_scores=average_scores,
        average_loc=average_loc,
        fdf=fdf,
        lc1 = list(fdf['总得分(%)']),
        ad1= list(fdf.index),
        index_name_list=index_name_list,
        index_value_list=index_value_list,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your dataframes page.'
    )

@app.route('/dataframe')
def dataframe():
    """Renders the about page."""
    return render_template(
        'dataframe.html',
        title='Dataframe',
        data=fdf,
        year=datetime.now().year,
        message='Your application description page.'
    )


@app.route('/search', methods=['POST','GET'])
def search():
    #fetch search name
    name_ad = request.form.get('ad')

    if name_ad == None:
        return render_template(
        'search.html',
        margin_one = '50px',
        name_list=name_list,
        hide_or_not="visibility:hidden;"
    )
    else :
        if name_ad in name_list:
            #get rank
            fdf3 = fdf.reset_index()
            fdf3[fdf3['index']==name_ad].index
            identity = list(fdf3[fdf3['index']==name_ad].index)

            #color variables
            bgc = ['rgba(204,204,204,1)']*len(fdf)
            borderc = ['rgba(204,204,204,1)']*len(fdf)
            hbgc = ['rgba(204,204,204,1)']*len(fdf)

            bgc[identity[0]] = 'rgba(222,45,38,0.8)'
            borderc[identity[0]] = 'rgba(222,45,38,0.8)'
            hbgc[identity[0]] = 'rgba(222,45,38,0.8)'

            person_dfd = create_person_df(name_ad)
            person_dfd = person_dfd.to_html(border=0,justify="center")
            person_dfd = person_dfd.replace( '<table border="0" ','<table border="0" style="margin:auto";text-align:center ')
            if identity[0]>10 and identity[0]<(len(fdf)-10):

                return render_template('search.html', 
                                       AD = "", 
                                       name_ad=name_ad,
                                       name_list=name_list,
                                       margin_one='20px',
                                       hide_or_not="visibility:visible;",
                                       bgc= bgc[identity[0]-10:identity[0]+10],
                                       borderc=borderc[identity[0]-10:identity[0]+10],
                                       lc2 = list(fdf['总得分(%)'])[identity[0]-10:identity[0]+10],
                                       ad2= list(fdf.index)[identity[0]-10:identity[0]+10],
                                       hbgc=hbgc[identity[0]-10:identity[0]+10],
                                       personal_df=person_dfd,
                                       data_pie_search = list(fdf['labels'].value_counts()),
                                       label_pie_search = list(fdf['labels'].value_counts().index),

                                       min_value = list(fdf['总得分(%)'])[identity[0]+10],
                                       max_value = list(fdf['总得分(%)'])[identity[0]-10],
                                       )
            elif identity[0]<=10 :
                return render_template('search.html', 
                                       AD = "", 
                                       name_ad=name_ad,
                                       name_list=name_list,
                                       margin_one='20px',
                                       hide_or_not="visibility:visible;",
                                       bgc= bgc[0:identity[0]+10],
                                       borderc=borderc[0:identity[0]+10],
                                       lc2 = list(fdf['总得分(%)'])[0:identity[0]+10],
                                       ad2= list(fdf.index)[0:identity[0]+10],
                                       hbgc=hbgc[0:identity[0]+10],
                                       personal_df=person_dfd,
                                       data_pie_search = list(fdf['labels'].value_counts()),
                                       label_pie_search = list(fdf['labels'].value_counts().index),

                                       min_value = list(fdf['总得分(%)'])[identity[0]+10],
                                       max_value = list(fdf['总得分(%)'])[0],
                                       )
            elif identity[0]>=(len(fdf)-10):
                  return render_template('search.html', 
                                       AD = "", 
                                       name_ad=name_ad,
                                       name_list=name_list,
                                       margin_one='20px',
                                       hide_or_not="visibility:visible;",
                                       bgc= bgc[identity[0]-10:],
                                       borderc=borderc[identity[0]-10:],
                                       lc2 = list(fdf['总得分(%)'])[identity[0]-10:],
                                       ad2= list(fdf.index)[identity[0]-10:],
                                       hbgc=hbgc[identity[0]-10:],
                                       personal_df=person_dfd,
                                       data_pie_search = list(fdf['labels'].value_counts()),
                                       label_pie_search = list(fdf['labels'].value_counts().index),

                                       min_value = 0,
                                       max_value = list(fdf['总得分(%)'])[identity[0]-10],
                                       )
        else:
            return render_template(
            'search.html',
            margin_one = '50px',
            name_list=name_list,
            hide_or_not="visibility:hidden;",
            AD = "AD Not Found"
        )




@app.route('/charts')
def charts():
        return render_template(
        'charts.html',
        lc1 = list(fdf['总得分(%)']),
        ad1= list(fdf.index),
        data_pie = list(fdf['labels'].value_counts()),
        label_pie = list(fdf['labels'].value_counts().index),
        max_value=100,
        min_value=0,
        
    )

@app.route('/tables')
def tables():
        final_table = fdf.to_html(classes='data')
        final_table = final_table.replace('<table border="1" class="dataframe data"','<table data-toggle="table" data-pagination="true" data-search="true" data-show-columns="true" data-show-pagination-switch="true" data-show-refresh="true" data-key-events="true" data-show-toggle="true" data-resizable="true" data-cookie="true" data-cookie-id-table="saveId" data-show-export="true" data-click-to-select="true" data-toolbar="#toolbar" class="dataframe data"')
        final_table = final_table.replace('<tr style="text-align: right;">','<tr style="text-align: center;">')
        return render_template(
        'tables.html',
        tables=final_table, titles=fdf.columns.values,

    )

