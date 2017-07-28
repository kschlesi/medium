
from flask import render_template, request, redirect
from Flask_App import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
#import a_Model as mod
from Flask_App import a_Model as mod

user = 'kimberly' #add your username here (same as previous postgreSQL)                      
host = 'localhost'
dbname = 'medium'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

@app.route('/')
@app.route('/index')
@app.route('/input')
def url_input():
    return render_template("input.html")#,
       #title = 'Home', user = { 'nickname': 'Kim' },
       #)

@app.route('/output')
def cesareans_output():
    #pull 'in_url' from input field and store it
    in_url = request.args.get('in_url')
    print(in_url)
    #just select the matching url from the articles table
    query = "SELECT title, username, highlight, popdate, nlikes FROM articles WHERE url='%s'" % in_url
    print(query)
    query_results=pd.read_sql_query(query,con)
    print(query_results)
    q_results_dict = []
    for i in range(0,query_results.shape[0]):
        q_results_dict.append(dict(title=query_results.iloc[i]['title'], 
                                  username=query_results.iloc[i]['username'], 
                                  highlight=query_results.iloc[i]['highlight'],
                                  popdate=query_results.iloc[i]['popdate'],
                                  nlikes=query_results.iloc[i]['nlikes']
                                  ))
        #the_result = mod.ModelIt(in_url,q_result_dict)
    return render_template("output.html", q_results_dict = q_results_dict, in_url=in_url)#, the_result = the_result)

@app.route('/fbpost')
def facebook_post():
    to_url = request.args.get('to_url')
    return redirect(to_url, code=302)


