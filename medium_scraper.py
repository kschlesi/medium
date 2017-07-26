'''This is a module for scraping Medium.'''

# import libraries
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd
from selenium import webdriver

def start_sql_db(dbname):
    '''starts or connects to a postgreSQL db'''
    username = 'kimberly'
    engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))

    ## create a database (if it doesn't exist)
    if not database_exists(engine.url):
        create_database(engine.url)
    
    return engine

def url_list(filename,start_index=0):
    '''reads and returns list of urls (iterable)'''
    with open(filename) as f:
        myurls = f.read().splitlines()
    return myurls[start_index:]

def open_browser():
    '''open selenium-driven chrome browser; returns browser obj'''
    path_to_chromedriver = '/Users/kimberly/Documents/Insight/Medium/selenium/chromedriver'
    browser = webdriver.Chrome(executable_path = path_to_chromedriver)
    return browser

def process_medium_url(theurl,browser,engine):
    '''given url and browser, this opens, scrapes, and saves data 
    from one Medium url'''
    # get url and wait for page load
    browser.get(theurl)
    browser.implicitly_wait(10) # seconds

    # scrape desired data
    hilite = get_highlight(browser)
    atext = get_text(browser)
    likes = get_likes(browser)
    comments = get_comments(browser)
    userid = get_user_ID(browser)
    username = get_username(browser)
    title = get_title(browser)
    tags = get_tags(browser)
    aID = get_post_ID(browser)

    # format data for articles
    a_list = format_adata(aID,tags,title,username,userid,comments,
                          likes,atext,hilite)
    a_data = pd.DataFrame(a_list)
    a_data = a_data.T
    a_data.columns = ['postid', 'title', 'username', 'userid', 'npar', 'text', 
                      'highlight', 'nlikes', 'ncomments', 'ntags', 'tags']

    # format data for users
    #u_list = [user]
    #user_data = pd.DataFrame(u_list,columns=['uID'])

    # save data in DB
    a_data.to_sql('articles', engine, if_exists='append')
    #user_data.to_sql('users', engine, if_exists='append')
    
    # return data to append to dataframe
    return a_data

def get_highlight(browser):
    '''scrapes highlight from a medium article in browser, returns str'''
    try:
        return browser.find_element_by_css_selector('.is-other').text
    except:
        return None

def get_text(browser):
    '''scrapes article text from medium article in browser,
    returns list of str (one per <p> tag)'''
    try:
        return [p.text for p in browser.find_elements_by_tag_name('p')]
    except:
        return None

def get_likes(browser):
    '''gets number of likes from browser, returns str'''
    try:
        likes_elem = browser.find_elements_by_css_selector('.js-actionRecommend')
        return likes_elem[0].find_elements_by_css_selector('button')[1].text
    except:
        return None

def get_comments(browser):
    '''gets number of comments'''
    try:
        elem = browser.find_elements_by_css_selector('.buttonSet-inner .u-baseColor--buttonNormal')
        return elem[2].text
    except:
        return None

def get_user_ID(browser):
    '''gets user ID from medium'''
    try:
        elem = browser.find_elements_by_xpath('//a[@data-action="show-user-card"]')
        return elem[1].get_attribute("data-user-id")
    except:
        return None

def get_username(browser):
    '''gets user name'''
    try:
        elem = browser.find_elements_by_xpath('//a[@data-action="show-user-card"]')
        return elem[1].text
    except:
        return None

def get_title(browser): 
    '''gets article title'''
    try:
        return browser.find_element_by_css_selector('.graf--title').text
    except:
        return None

def get_tags(browser):
    try:
        tag_elem = browser.find_element_by_css_selector('.tags--borderless')
        return [tag.text for tag in tag_elem.find_elements_by_css_selector('li')]
    except:
        return None

def get_post_ID(browser):
    try:
        elem = browser.find_element_by_xpath('//div[@data-source="post_page"]')
        return elem.get_attribute("data-post-id")
    except:
        return None

def format_adata(aID,tags,title,username,userid,comments,
                              likes,atext,hilite):
    '''formats article data for db storage'''
    try:
        ltext = len(atext)
    except:
        ltext = None
    try:
        atext = '\n'.join(atext)
    except:
        atext = None
    try:
        ltags = len(tags)  
    except:
        ltags = None
    try:
        atags = ','.join(tags)
    except:
        atags = None    
    return [aID,title,username,userid,ltext,atext,
                  hilite,likes,comments,ltags,atags]              

# main routine to run scraper
if __name__ == '__main__':
    # initial values
    trial_name = 'medium_test_11'
    filename = 'medium_urls_unique.txt'
    start_index = 1257+420+2696
    
    # setup
    e = start_sql_db(trial_name)
    b = open_browser()

    # dataframe for storing article data
    dfA = pd.DataFrame(columns = ['postid', 'title', 'username', 'userid', 'npar', 'text', 
                                  'highlight', 'nlikes', 'ncomments', 'ntags', 'tags'])
    try:
        # analysis for each url
        for url in url_list(filename,start_index):
            dfA_new = process_medium_url(url,b,e)
            dfA = pd.concat([dfA,dfA_new])
        # dump all data to csv
        dfA.to_csv(trial_name + '.csv', index=False)
        print('SUCCESSFUL PROCESSING... CLOSE')
        b.quit()
    except:
        dfA.to_csv(trial_name + '.csv', index=False)
        print('ERROR IN PROCESSING... CLOSE')
        b.quit()
        raise

# 
