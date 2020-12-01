from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from datetime import timedelta
# from gensim.summarization.summarizer import summarize
# from newspaper import Article
import json, pymysql, re, datetime
from flask_jsglue import JSGlue

import requests  
from bs4 import BeautifulSoup as bs

from generator import main

app = Flask(__name__)
jsglue = JSGlue(app)
app.secret_key = "dayday"

#home 화면
@app.route("/")
def test4():
    company_info = {('samsung.jpg','삼성전자'),
    ('lg.jpg','LG전자'),
    ('hyundai.jpg','현대자동차'),
    ('sk.jpg','SK하이닉스')}

    db = pymysql.connect(host="주소",
                    user="root", 
                    passwd="password", 
                    db="news", 
                    charset="utf8")

    cur = db.cursor()
    sql = 'SELECT * FROM news.company limit 20;'
    cur.execute(sql)
    data_list = cur.fetchall()

    return render_template("newbase6_1.html", data = company_info, data2 = data_list)

#통합 문장 생성
@app.route("/search")
def search():
    return render_template("newbase6_search.html")

#회사 개별 화면
@app.route("/com/<company_id>/<quarter>")
def test5(company_id,quarter):
    db = pymysql.connect(host="주소",
                    user="root", 
                    passwd="password", 
                    db="news", 
                    charset="utf8")

    #회사 정보
    cur = db.cursor()
    sql = 'SELECT * FROM news.company where company_id = '+ company_id
    cur.execute(sql)
    data_list = cur.fetchall()

    #여기에 카테고리 신제품으로 정해서 이슈에서 키워드들 가져오기
    sql2 = 'SELECT * FROM news.issue where cluster_id like "'+str(quarter)+'_'+company_id+'_1%"'
    cur.execute(sql2)
    issuelist = cur.fetchall()

    #워드클라우드 이미지 url
    sql3 = 'SELECT * FROM news.summary where quarter = '+str(quarter)+' and company_id = "'+company_id+'"'
    cur.execute(sql3)
    wordcloud = cur.fetchall()

    #회사별 총 기사 수
    sql4 = 'SELECT sum(num_of_articles) FROM news.summary where company_id = "'+company_id+'"'
    cur.execute(sql4)
    num_article = cur.fetchall()
    num_article = format(num_article[0][0],',')
    return render_template("newbase6_company.html", thiscom = data_list[0], quarter = quarter, issues = issuelist,wordcloud = wordcloud[0], num_article = num_article)

#gpt 진행
@app.route("/gptprocess", methods=["POST"])
def gpt():
    if request.method == "POST":
        gensent = request.get_json()["gensent"]
        quarter = request.get_json()['quarter']
        
        print(gensent)
        print(quarter)

        #main함수의 parameter는 generator.py 파일에서 조작할 수 있다.
        if request.get_json()['com_id'] == 'All':
            print('./checkpoint/KoGPT2_checkpoint_qt'+str(quarter)+'_total_60_138348.tar')
            sent = main(gensent, load_path = './checkpoint/KoGPT2_checkpoint_qt'+str(quarter)+'_total_60_138348.tar')
        else:
            print('./checkpoint/KoGPT2_checkpoint_qt'+str(quarter)+'_'+request.get_json()['com_id']+'.tar')
            sent = main(gensent, load_path = './checkpoint/KoGPT2_checkpoint_qt'+str(quarter)+'_'+request.get_json()['com_id']+'.tar')
            
        sents = {}
        
        print(sent)
        sent = '.'.join(sent.split('.')[:-1])+'.'
        sents['gen'] = sent
        return sents
    else:
        print('cc')
        return('asda')

#이슈 바꾸기
@app.route("/issueprocess", methods=["POST"])
def issue():
    if request.method == "POST":
        company = request.get_json()['com_id']
        quarter = request.get_json()['quarter']
        category = request.get_json()['category_id']

        db = pymysql.connect(host="주소",
                    user="root", 
                    passwd="password", 
                    db="news", 
                    charset="utf8")

        cur = db.cursor()
        print('company: ',company, 'quarter:',quarter, 'category:',category)
        #company,quarter,category
        sql = 'SELECT * FROM news.issue where cluster_id like "'+str(quarter)+'_'+company+'_'+str(category)+'%"'
        cur.execute(sql)
        data_list = cur.fetchall()
            
        return json.dumps(data_list)
    else:
        print('cc')
        return('asda')

#아티클 바꾸기
@app.route("/articleprocess", methods=["POST"])
def article():
    if request.method == "POST":
        company = request.get_json()['com_id']
        quarter = request.get_json()['quarter']
        category = request.get_json()['category_id']
        issue = request.get_json()['issue_id']

        db = pymysql.connect(host="주소",
                    user="root", 
                    passwd="password", 
                    db="news", 
                    charset="utf8")

        cur = db.cursor()
        print('compnay: ',company, 'quarter:',quarter, 'category:',category, 'issue',issue)
        #company,quarter,category,issue
        sql = 'SELECT * FROM news.article where company_id = "'+company+'" and quarter = '+str(quarter)+' and category_num = '+str(category) +' and cluster_label = '+str(issue[-1])+' limit 8'
        cur.execute(sql)
        data_list = cur.fetchall()
            
        return json.dumps(data_list)
    else:
        print('cc')
        return('asda')

#우리 정보
@app.route("/about")
def about():
    return render_template("newbase6_about.html")


#실행
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)     