import cgi
import datetime

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext import search  

class Survey(search.SearchableModel):
    account = db.StringProperty()
    title = db.StringProperty()
    question = db.StringProperty()
    option = db.StringProperty()
    count = db.IntegerProperty()
    picture = db.BlobProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    
class MyVote(db.Model):
    account = db.StringProperty()
    title = db.StringProperty()
    question = db.StringProperty()
    option = db.StringProperty()
    author = db.StringProperty()
    
class VoteCount(db.Model):
    account = db.StringProperty()
    voter =db.StringProperty()
    title = db.StringProperty()
    count = db.IntegerProperty()
    
class Comment(db.Model):
    account = db.StringProperty()
    author = db.StringProperty()
    title = db.StringProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    
def getuniqlist(mylist,attribute):
    newlist = []
    for element in mylist:
        flag=0
        if attribute=="question":
            tmp=element.question
        if attribute=="title":
            tmp=element.title
        if attribute=="option":
            tmp=element.option
        if attribute=="account":
            tmp=element.account
        for item in newlist:
            if item==tmp:
                flag=1
        if flag==0:
            newlist.append(tmp)
    return newlist

def printVoteResult(voter, title, account, self):
        titles = db.GqlQuery("SELECT * "
                             "FROM VoteCount "
                             "WHERE account = :1 and title = :2 and voter =:3",
                             account, title, voter)
        if titles.count()==0:
            vc=VoteCount(account=account, title=title, voter=voter, count=1)
            db.put(vc)
        else:
            vcs=db.GqlQuery(" SELECT * "
                            " FROM VoteCount "
                            " WHERE account = :1 and title = :2 and voter = :3", account, title, voter)
            if vcs.count()==0:
                for tt in titles:
                    tt.count=tt.count+1
                    tt.put()
            
        results = db.GqlQuery("SELECT * "
                            "FROM MyVote "
                            "WHERE account = :1 and title = :2 and author = :3", voter, title,account)
        if results.count()!=0:
            self.response.out.write("""<font size=4>Survey: %s(%s)</font></br>"""%(cgi.escape(title), cgi.escape(account)))
            qNum=1
            for result in results:
                self.response.out.write("<div><p><big>Q%s. %s</big><br />"%(qNum,cgi.escape(result.question)))
                self.response.out.write("Your choice: %s<br />" %cgi.escape(result.option))
                surveys = db.GqlQuery("SELECT * "
                                      "FROM Survey "
                                      "WHERE account = :1 and title = :2 and question =:3 and option = :4", account, title, result.question, result.option)
                if surveys.count()!=0:
                    for entry in surveys:
                        if entry.picture:
                            self.response.out.write("<img src='img?img_id=%s'></img>" %entry.key())
                self.response.out.write("</p></div>")
                qNum=qNum+1

            self.response.out.write("""
            <html><body>
            <form action="/addComment" method="post">""")
            self.response.out.write("""Would you please give some comments for this survey: </br>""")
            self.response.out.write("""<div><textarea name="comment" rows="5" cols="60"></textarea></div>""")
            self.response.out.write("""<div><input type="submit" name="button" value="submit"></div>""")
            self.response.out.write("""
                      <input type="hidden" name="voter" value="%s">
                      <input type="hidden" name="title" value="%s">
                      <input type="hidden" name="account" value="%s">
                      </form></body></html>""" %(cgi.escape(voter),cgi.escape(title),cgi.escape(account)))
        
#list all the uniq author by survey:
def listOptions(self,voter,title,account,flag,index):
    
    queIndex=int(index)
    questions = db.GqlQuery("SELECT * "
                            "FROM Survey "
                            "WHERE account = :1 and title = :2", account, title)
    
    questionList = getuniqlist(questions,"question")
   
    if queIndex>len(questionList):
         self.response.out.write("""
            You finished all the question. Thank you for voting!  <a href=\"/\">Back To Home Page</a></br>""")
         printVoteResult(voter, title, account,self)      
    else:
         curQ=questionList.pop(queIndex-1)
         self.response.out.write("""
         <html><body>
         <form action="/voteOptions" method="post">""")
         self.response.out.write(""" <font size=5>Q%s. %s</font>"""%(queIndex,cgi.escape(curQ)))
         options =  db.GqlQuery("SELECT * "
                                "FROM Survey "
                                "WHERE account = :1 and title = :2 and question = :3", account, title, curQ)
             #optionlist= getuniqlist(options, "option")
         oNum=1;
         for entry in options:
             if flag=="change":
                 questions = db.GqlQuery("SELECT * "
                            "FROM MyVote "
                            "WHERE author = :1 and title = :2 and question = :3 and option = :4 and account =:5", account,title,curQ,entry.option,voter)
                 if questions.count()!=0:
                     self.response.out.write("<div>  Your answer: C%s.%s</div>" %(oNum,cgi.escape(entry.option)))
                     if entry.picture:
                         self.response.out.write("<div><img src='img?img_id=%s'></img>" %entry.key())
                     old_option=entry.option
                 else:
                     self.response.out.write("""
                     <div><input type="radio" name = "option", value="%s"/><font size = 4>C%s.%s</font></div>"""
                         %(cgi.escape(entry.option),oNum,cgi.escape(entry.option)))
                     if entry.picture:
                         self.response.out.write("<div><img src='img?img_id=%s'></img>" %entry.key())
             if flag=="vote":
                 self.response.out.write("""
                 <div><input type="radio" name = "option", value="%s"/><font size = 4>C%s.%s</font></div>"""
                     %(cgi.escape(entry.option),oNum,cgi.escape(entry.option)))
                 if entry.picture:
                     self.response.out.write("<div><img src='img?img_id=%s'></img>" %entry.key())
             oNum=oNum+1
         if flag=="vote":
             self.response.out.write("""<div><input type="submit" name="button" value="next question">
                                           <input type="submit" name="button" value="skip to the end"></div>""")
         if flag=="change":
             self.response.out.write("""<div><input type="submit" name="button" value="change">
                                           <input type="submit" name="button" value="change and next">
                                           <input type="submit" name="button" value="next"></div>
                                           <input type="hidden" name="old option" value="%s" >""" %cgi.escape(old_option))
          
         self.response.out.write("""
                      <input type="hidden" name="voter" value="%s">
                      <input type="hidden" name="title" value="%s">
                      <input type="hidden" name="account" value="%s">
                      <input type="hidden" name="question" value="%s">
                      <input type="hidden" name="index" value="%s">
                      <input type="hidden" name="flag" value="%s">
                      </form></body></html>"""%(cgi.escape(voter),cgi.escape(title),cgi.escape(account),cgi.escape(curQ),queIndex,flag))
 
def listAuthorbySurvey(self,voter,title,flag,ErrorMsg):
    surveys = db.GqlQuery("SELECT * "
                          "FROM Survey "
                          "WHERE title = :1", title)
    if surveys.count()!=0:
        self.response.out.write("""
        <html><body>
        <form action="/displayresult" method="post">""")

        if ErrorMsg!="":
            self.response.out.write("""
            %s  <a href=\"/\">Back To Home Page</a>""" %cgi.escape(ErrorMsg))

        newlist=getuniqlist(surveys,"account")
        if flag=="vote":
            votedSurveys = db.GqlQuery("SELECT * "
                          "FROM MyVote "
                          "WHERE account = :1 and title = :2", voter,title)
            if votedSurveys.count()!=0:
                isVoted=0
                notVotedSurvey=[]
                for survey in surveys:
                    for voted in votedSurveys:
                        if voted.author == survey.account and voted.title == survey.title:
                            isVoted=1
                            break
                    if isVoted==0:
                        notVotedSurvey.append(survey)
                newlist=getuniqlist(notVotedSurvey,"account")
        if flag=="change":
            votedSurveys = db.GqlQuery("SELECT * "
                          "FROM MyVote "
                          "WHERE account = :1 and title = :2", voter,title)
            if votedSurveys.count()!=0:
                votedSurvey=[]
                for survey in surveys:
                    for voted in votedSurveys:
                        if voted.author == survey.account and voted.title == survey.title:
                            votedSurvey.append(survey)
                            break
                newlist=getuniqlist(votedSurvey,"account") 
        account_num=1
        for entry in newlist:
            self.response.out.write("""
            <div><input type="radio" name = "account", value="%s"/><font size = 4>Author %s. %s</font></div>"""
            %(cgi.escape(entry), account_num, cgi.escape(entry)))
            account_num=account_num+1

        if flag=="vote":
            self.response.out.write("""
            <input type="submit" name="button" value= "vote" />""")
        if flag=="result":
            self.response.out.write("""
            <input type="submit" name="button" value= "result" />""")
        if flag=="change":
            self.response.out.write("""
            <input type="submit" name="button" value= "change" />""")

        self.response.out.write("""
        <input type="hidden" name="title" value= "%s" />
        <input type="hidden" name="flag" value=  "%s" />
        <input type="hidden" name="voter" value="%s" />
        </form></body></html>"""%(cgi.escape(title),flag,cgi.escape(voter)))
    else:
        self.response.out.write("""
        <html><body>
        <p><big> There is no survey created. </big></p>
        </body></html>""" )
    return

#list all the uniq survey title belong to the login account:
def listsurveyTitlebyAccount(account,self,ErrorMsg):
    surveys = db.GqlQuery("SELECT * "
                          "FROM Survey "
                          "WHERE account = :1", account)
    if surveys.count()!=0:
        self.response.out.write("""
        <html><body>
        <form action="/cleanSurvey" method="post">""")

        if ErrorMsg!="":
            self.response.out.write("""
            %s  <a href=\"/\">Back To Home Page</a>""" %cgi.escape(ErrorMsg))

        newlist=getuniqlist(surveys,"title")
        title_num=1
        for entry in newlist:
            self.response.out.write("""
            <div><input type="radio" name = "title", value="%s"/><font size = 4>No. %s. %s</font></div>"""%(cgi.escape(entry), title_num, cgi.escape(entry)))
            title_num=title_num+1

        self.response.out.write("""
        <input type="submit" name="button" value= "delete" />
        <input type="submit" name="button" value= "edit title" />
        <input type="submit" name="button" value= "add question" />
        <input type="submit" name="button" value= "edit question" />
        <input type="hidden" name="account" value= "%s" />"""%cgi.escape(account))

        self.response.out.write(""" </form>""")
        self.response.out.write(""" </body></html>""")
    else:
        self.response.out.write("""
        <html><body>
        <p><big> There is no survey created.<a href=\"/\">Back To Home Page</a></big></p>
        </body></html>""" )
    return

#list all uniq survey
def listsurveyTitle(voter,self,flag,ErrorMsg):
    if flag=="popularity":
        topSurveys=db.GqlQuery("SELECT * "
                          "FROM VoteCount "
                          "ORDER BY count DESC LIMIT 5 ")
        if topSurveys.count()==0:
             self.response.out.write("""<big><p>There is no survey created or voted.</p></big>""")
             return
        else:
             top=0
             for survey in topSurveys:
                 top=top+1 
                 self.response.out.write("""<big><p>No.%s %s(author:%s, voted times:%s)</p></big>"""
                                    %(top, cgi.escape(survey.title), cgi.escape(survey.account), survey.count))             
             return
    surveys = db.GqlQuery("SELECT * "
                          "FROM Survey ")
    
    if surveys.count()!=0:
        self.response.out.write("""
        <html><body>
        <form action="/getauthor" method="post">""")

        if ErrorMsg!="":
            self.response.out.write("""
            %s  <a href=\"/\">Back To Home Page</a>""" %cgi.escape(ErrorMsg))

        newlist=getuniqlist(surveys,"title")
        if flag=="change":
            votedSurveys = db.GqlQuery("SELECT * "
                          "FROM MyVote "
                          "WHERE account = :1", voter)
            if votedSurveys.count()!=0:
                votedSurvey=[]
                for survey in surveys:
                    isVoted=0
                    for voted in votedSurveys:
                        if voted.author == survey.account and voted.title == survey.title:
                            votedSurvey.append(survey)
                            break
                newlist=getuniqlist(votedSurvey,"title")
            else:
                newlist=[]
        if flag=="vote":
            votedSurveys = db.GqlQuery("SELECT * "
                          "FROM MyVote "
                          "WHERE account = :1", voter)
            if votedSurveys.count()!=0:
                notVotedSurvey=[]
                for survey in surveys:
                    isVoted=0
                    for voted in votedSurveys:
                        if voted.author == survey.account and voted.title == survey.title:
                            isVoted=1
                            break
                    if isVoted==0:
                        notVotedSurvey.append(survey)
                newlist=getuniqlist(notVotedSurvey,"title")
        title_num=1
        for entry in newlist:
            self.response.out.write("""
            <div><input type="radio" name = "title", value="%s"/><font size = 4>No.%s %s</font></div>"""%(cgi.escape(entry), title_num, cgi.escape(entry)))
            title_num=title_num+1

        if flag=="vote":
            if newlist==[]:
                self.response.out.write(""" <p><big> There is no surveys for you to vote.""")
            else:
                self.response.out.write("""
                <input type="submit" name="button" value= "vote" />""")    
        if flag=="result":
            self.response.out.write("""
            <input type="submit" name="button" value= "result" />""")
        if flag=="change":
            if newlist==[]:
                self.response.out.write(""" <p><big>You have not voted yet.""")
            else:
                self.response.out.write("""
                <input type="submit" name="button" value= "change" />""")

        self.response.out.write("""
        <input type="hidden" name="voter" value="%s">
        <input type="hidden" name="flag" value="%s">
        </form></body></html>""" %(cgi.escape(voter),flag))
    else:
        self.response.out.write("""
        <html><body>
        <p><big> There is no survey created.</big></p>
        </body></html>""" )
    return

#list all the uniq question name belong to the login account&&specified title:
def listQbyAT(account,title,self,ErrorMsg):
    questions = db.GqlQuery("SELECT * "
                          "FROM Survey "
                          "WHERE account = :1 and title = :2", account,title)
    if questions.count()!=0:
        self.response.out.write("""
        <html><body>
        <form action="/editQuestion" method="post">
        <p><big>The survey title is %s. </big><a href=\"/\">Back To Home Page</a></p>""" %cgi.escape(title))

        if ErrorMsg!="":
            self.response.out.write("""
            %s""" %cgi.escape(ErrorMsg))

        newlist=getuniqlist(questions,"question")
        question_num=1
        for entry in newlist:
            self.response.out.write("""
            <div><input type="radio" name = "question", value="%s"/><font size = 4>Q%s. %s</font></div>"""%(cgi.escape(entry), question_num, cgi.escape(entry)))
            question_num=question_num+1

        self.response.out.write("""
        <input type="submit" name="button" value= "delete" />
        <input type="submit" name="button" value= "edit question name" />
        <input type="submit" name="button" value= "add option" />
        <input type="submit" name="button" value= "edit option" />
        <input type="hidden" name="account" value= "%s" />
        <input type="hidden" name="title" value= "%s" /> """%(cgi.escape(account),cgi.escape(title)))

        self.response.out.write(""" </form>""")
        self.response.out.write(""" </body></html>""")
    else:
        self.response.out.write("""
        <html><body>
        <p><big> There is no questions in the survey %s.</big></p>
        </body></html>""" % cgi.escape(title) )
    return

#list all the uniq option name belong to the login account&&specified title$$specified question:
def listObyATQ(account,title,question,self,ErrorMsg):
    options = db.GqlQuery("SELECT * "
                          "FROM Survey "
                          "WHERE account = :1 and title = :2 and question = :3", account,title,question)
    if options.count()!=0:
        self.response.out.write("""
        <html><body>
        <form action="/editOption" enctype="multipart/form-data" method="post">
        <p><big>%s - %s </big><a href=\"/\">Back To Home Page</a></p>""" %(cgi.escape(title),cgi.escape(question)))

        if ErrorMsg!="":
            self.response.out.write("""
            %s""" %cgi.escape(ErrorMsg))

        #newlist=getuniqlist(options,"option")
        option_num=1
        for entry in options:
            self.response.out.write("""
            <div><input type="radio" name = "option", value="%s"/><font size = 4>C%s. %s</font></div>"""
            %(cgi.escape(entry.option), option_num, cgi.escape(entry.option)))
            if entry.picture:
                self.response.out.write("<div><img src='img?img_id=%s'></img></div>"%entry.key())
            option_num=option_num+1

        self.response.out.write("""
        <input type="submit" name="button" value= "delete" />
        <input type="submit" name="button" value= "edit option name" />
        <input type="hidden" name="account" value= "%s" />
        <input type="hidden" name="title" value= "%s" />
        <input type="hidden" name="question" value="%s" /> """%(cgi.escape(account),cgi.escape(title),cgi.escape(question)))

        self.response.out.write(""" </form>""")
        self.response.out.write(""" </body></html>""")
    else:
        self.response.out.write("""
        <html><body>
        <p><big> There is no option in the survey (%s) for this question (%s).</big></p>
        </body></html>""" % (cgi.escape(title),cgi.escape(question)) )
    return

# process the edit survey title page. 1. the title input is null, display error msg;
# 2. the title input exists for the login account, display error msg;
# 3. correct title, "create" -> add question; "edit" -> go back to survey title page
def defsurvey_title(account,title,flag,old_title,self):
    errorMsg=""
    if title != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2", account, title)
        if existSurvey.count() == 0:
            if flag=="create":
                self.response.out.write("""
                <html><body>
                <p><big> Add a question for survey: "%s"</big></p>
                <form action="/newSurvey" method="post">
                <div><textarea name="question" rows="3" cols="60"></textarea></div>
                <div><input type="submit" name="button" value="add an option"></div>
                <input type="hidden" name="title" value="%s" />
                <input type="hidden" name="account" value="%s" />
                </form></body></html>""" % (cgi.escape(title),cgi.escape(title),cgi.escape(account)))
            if flag=="edit":
                surveys = db.GqlQuery("SELECT * "
                                      "FROM Survey "
                                      "WHERE account = :1 and title = :2", account, old_title)
                for survey in surveys:
                    survey.title=title
                    survey.put()
                listsurveyTitlebyAccount(account,self,"The survey title is updated.")
        else:
            errorMsg="The title you input exists! Please give another one:"
    else:
        errorMsg="You have to give a title of the new survey:"
    if errorMsg != "":
        if flag=="create":
            self.response.out.write("""
            <html><body>
            <p><big> %s</big></p> 
            <form action="/newSurvey" method="post">
            <div><textarea name="title" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="add a new question"></div>
            <input type="hidden" name="account" value="%s" />
            </form></body></html>""" % (cgi.escape(errorMsg), cgi.escape(account)))
        if flag=="edit":
            self.response.out.write("""
            <html><body>
            <p><big> The title is about to be modified is:%s </big><a href=\"/\">Back To Home Page</a></p>
            <p><big> %s </big></p>
            <form action="/updateText" method="post">
            <div><textarea name="newTitle" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="submit"></div>
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />
            <input type="hidden" name="choice" value="update title" />
            </form></body></html>""" %(cgi.escape(old_title), cgi.escape(errorMsg),cgi.escape(old_title), cgi.escape(account)))
    return

# process the edit question name page. 1. the question name input is null, display error msg;
# 2. the question name input exists for the login account, display error msg;
# 3. correct question name, "create" -> add option; "edit" -> go back to question page
def defquestion(account,title,question,flag,old_question,self):
    errorMsg=""
    if question != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2 and question = :3", account, title, question)
        if existSurvey.count() == 0:
            if flag=="create":
                self.response.out.write("""
                <html><body>
                <p><big> Add an option for question "%s--%s":</big></p> 
                <form action="/newSurvey" enctype="multipart/form-data" method="post">
                <div><label>Message:</label></div>
                <div><textarea name="option" rows="3" cols="60"></textarea></div>
                <div><label>Image:</label></div>
                <div><input type="file" name="img" /></div>
                <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
                <input type="submit" name="button" value="complete"></div>
                <input type="hidden" name="question" value="%s" />
                <input type="hidden" name="title" value="%s" />
                <input type="hidden" name="account" value="%s" />
                </form></body></html>""" % (cgi.escape(title),cgi.escape(question), cgi.escape(question), cgi.escape(title), cgi.escape(account)))
            if flag=="edit":
                surveys = db.GqlQuery("SELECT * "
                                      "FROM Survey "
                                      "WHERE account = :1 and title = :2 and question =:3", account, title, old_question)
                for survey in surveys:
                    survey.question=question
                    survey.put()
                listQbyAT(account,title,self,"The question name is updated.")
        else:
            errorMsg="The question you input exists! Please input another one:"
    else:
        errorMsg="Please give the question:"
    if errorMsg != "":
        if flag=="create":
            self.response.out.write("""
            <html><body>
            <p><big> This survey is %s.<br />%s</big></p>
            <form action="/newSurvey" method="post">
            <div><textarea name="question" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="add an option"></div>
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />
            </form></body></html>""" % (cgi.escape(title),cgi.escape(errorMsg),cgi.escape(title), cgi.escape(account)))
        if flag=="edit":
            self.response.out.write("""
            <html><body>
            <p><big> The question is about to be modified is:%s </big><a href=\"/\">Back To Home Page</a></p>
            <p><big> %s </big></p>
            <form action="/updateText" method="post">
            <div><textarea name="newQuestion" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="submit"></div>
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="question" value="%s" />
            <input type="hidden" name="account" value="%s" />
            <input type="hidden" name="choice" value="update question" />
            </form></body></html>""" %(cgi.escape(old_question),cgi.escape(errorMsg), cgi.escape(title), cgi.escape(old_question), cgi.escape(account)))
    return

def defoption_question(account,title,question,option,self,picture):
    errorMsg=""
    if option != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2 and question = :3 and option = :4", account, title, question, option)
        if existSurvey.count() == 0:
            if picture:
                s = Survey(account=account,
                                   title=title,
                                   question=question,
                                   option=option,
                                   count=0,
                                   picture=db.Blob(picture))
            else:
                s = Survey(account=account,
                                   title=title,
                                   question=question,
                                   option=option,
                                   count=0)
            db.put(s)
            self.response.out.write("""
            <html><body>
            <p><big> Add a question for survey: "%s"</big></p> 
            <form action="/newSurvey" method="post">"""%cgi.escape(title))
            sets = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2", account, title)
            newlist=getuniqlist(sets,"question")
            num=1
            for entry in newlist:
                self.response.out.write("""
                <div><p>Q%s. %s </p></div>""" %(num,cgi.escape(entry)))
                num=num+1
            self.response.out.write("""
            <div><textarea name="question" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="add an option"></div>
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />
            </form></body></html>""" %(cgi.escape(title),cgi.escape(account)))
        else:
            errorMsg="The option you input exists! Please input another one:"
    else:
        errorMsg="Please give the option(text is required):"
    if errorMsg!="":
        self.response.out.write("""
        <html><body>
        <p><big> Add an option for question %s--%s.<br /> %s</big></p> 
        <form action="/newSurvey" enctype="multipart/form-data" method="post">""" %(cgi.escape(title),cgi.escape(question),cgi.escape(errorMsg)))
        sets = db.GqlQuery("SELECT * "
                            "FROM Survey "
                            "WHERE account = :1 and title = :2 and question = :3", account, title, question)
        num=1
        for entry in sets:
            self.response.out.write("""
            <div><p>C%s. %s</p> """ %(num,cgi.escape(entry.option)))
            if entry.picture:
                self.response.out.write("""
                <img src ='img?img_id=%s'></img>""" %entry.key())
            self.response.out.write("</div>")
            num=num+1
        self.response.out.write("""
        <div><label>Message:</label></div>
        <div><textarea name="option" rows="3" cols="60"></textarea></div>
        <div><label>Image:</label></div>
        <div><input type="file" name="img" /></div>
        <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
        <input type="submit" name="button" value="complete"></div>
        <input type="hidden" name="question" value="%s" />
        <input type="hidden" name="title" value="%s" />
        <input type="hidden" name="account" value="%s" />
        </form></body></html>""" % (cgi.escape(question), cgi.escape(title), cgi.escape(account)))
    return

def defoption_option(account,title,question,option,flag,old_option,self,picture):
    errorMsg=""
    if option != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2 and question = :3 and option = :4", account, title, question, option)
        if existSurvey.count() == 0:
            if flag=="create":
                if picture:
                    s = Survey(account=account,
                               title=title,
                               question=question,
                               option=option,
                               count=0,
                               picture=db.Blob(picture))
                else:
                    s = Survey(account=account,
                               title=title,
                               question=question,
                               option=option,
                               count=0)
                db.put(s)
                self.response.out.write("""
                <html><body>
                <p><big> Add a option for question "%s--%s":</big></p>
                <form action="/newSurvey" enctype="multipart/form-data" method="post">""" %(cgi.escape(title),cgi.escape(question)))
                sets = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title = :2 and question = :3", account, title, question)
                num=1
                for entry in sets:
                    self.response.out.write("""
                    <div><p>C%s. %s</p> """ %(num,cgi.escape(entry.option)))
                    if entry.picture:
                        self.response.out.write("""
                        <img src ='img?img_id=%s'></img>""" %entry.key())
                    self.response.out.write("</div>")
                    num=num+1
                self.response.out.write("""
                <div><label>Message:</label></div>
                <div><textarea name="option" rows="3" cols="60"></textarea></div>
                <div><label>Image:</label></div>
                <div><input type="file" name="img" /></div>
                <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
                <input type="submit" name="button" value="complete"></div>
                <input type="hidden" name="question" value="%s" />
                <input type="hidden" name="title" value="%s" />
                <input type="hidden" name="account" value="%s" />     
                </form></body></html>""" %(cgi.escape(question), cgi.escape(title), cgi.escape(account)))
            if flag=="edit":
                surveys = db.GqlQuery("SELECT * "
                                      "FROM Survey "
                                      "WHERE account = :1 and title = :2 and question =:3 and option = :4",
                                      account, title, question, old_option)
                db.delete(surveys)
                if picture:
                    s = Survey(account=account,
                               title=title,
                               question=question,
                               option=option,
                               count=0,
                               picture=db.Blob(picture))
                else:
                    s = Survey(account=account,
                               title=title,
                               question=question,
                               option=option,
                               count=0)
                db.put(s)
                #for survey in surveys:
                #   survey.option=option
                #    survey.put()
                    
                listObyATQ(account,title,question,self,"The option name is updated.")
        else:
            errorMsg="The option you input exists! Please input another one:"
    else:
        errorMsg="Please give the option(text is required):"
    if errorMsg!="":
        if flag=="create":
            self.response.out.write("""
            <html><body>
            <p><big> Add an option for question %s--%s.<br />%s</big></p> 
            <form action="/newSurvey" enctype="multipart/form-data" method="post">""" %(cgi.escape(title),cgi.escape(question),cgi.escape(errorMsg)))
            sets = db.GqlQuery("SELECT * "
                               "FROM Survey "
                               "WHERE account = :1 and title = :2 and question = :3", account, title, question)
            num=1
            for entry in sets:
                self.response.out.write("""
                <div><p>C%s. %s</p> """ %(num,cgi.escape(entry.option)))
                if entry.picture:
                    self.response.out.write("""
                    <img src ='img?img_id=%s'></img>""" %entry.key())
                self.response.out.write("</div>")
                num=num+1
            self.response.out.write("""
            <div><label>Message:</label></div>
            <div><textarea name="option" rows="3" cols="60"></textarea></div>
            <div><label>Image:</label></div>
            <div><input type="file" name="img" /></div>
            <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
            <input type="submit" name="button" value="complete"></div>
            <input type="hidden" name="question" value="%s" />
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />
            </form></body></html>""" %(cgi.escape(question), cgi.escape(title), cgi.escape(account)))
        if flag=="edit":
            self.response.out.write("""
            <html><body>
            <p><big> The option is about to be modified is:%s </big><a href=\"/\">Back To Home Page</a></p>
            <p><big> %s </big></p>
            <form action="/updateText" enctype="multipart/form-data" method="post">
            <div><label>Message:</label></div>
            <div><textarea name="newOption" rows="3" cols="60"></textarea></div>
            <div><label>Picture:</label></div>
            <div><input type="file" name="img"/></div>
            <div><input type="submit" name="button" value="submit"></div>
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="question" value="%s" />
            <input type="hidden" name="option" value="%s" />
            <input type="hidden" name="account" value="%s" />
            <input type="hidden" name="choice" value="update option" />
            </form></body></html>"""
            %(cgi.escape(option),cgi.escape(errorMsg), cgi.escape(title), cgi.escape(question), cgi.escape(old_option), cgi.escape(account)))
    return

def defoption_complete(account,title,question,option,self,picture):
    errorMsg=""
    if option != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2 and question = :3 and option = :4", account, title, question, option)
        if existSurvey.count() == 0:
            self.response.out.write("""
            <html><body>
            <p><big> Finished!</big></p>
            <a href=\"/\">Back To Home Page</a>
            </body></html>""" )
            if picture:
                s = Survey(account=account,
                           title=title,
                           question=question,
                           option=option,
                           count=0,
                           picture=db.Blob(picture))
            else:
                s = Survey(account=account,
                           title=title,
                           question=question,
                           option=option,
                           count=0)
            db.put(s)
        else:
            errorMsg="The option you input exists! Please input another one:"
    else:
        errorMsg="You can not leave the option as blank. What's the option"
    if errorMsg!="":
        self.response.out.write("""
        <html><body>
        <p><big> Add an option for question %s--%s.<br />%s</big></p> 
        <form action="/newSurvey" enctype="multipart/form-data" method="post">""" %(cgi.escape(title),cgi.escape(question),cgi.escape(errorMsg)))
        sets = db.GqlQuery("SELECT * "
                            "FROM Survey "
                            "WHERE account = :1 and title = :2 and question = :3", account, title, question)
        num=1
        for entry in sets:
            self.response.out.write("""
            <div><p>C%s. %s</p> """ %(num,cgi.escape(entry.option)))
            if entry.picture:
                self.response.out.write("""
                <img src ='img?img_id=%s'></img>""" %entry.key())
            self.response.out.write("</div>")
            num=num+1
        self.response.out.write("""
        <div><label>Message:</label></div>
        <div><textarea name="option" rows="3" cols="60"></textarea></div>
        <div><label>Image:</label></div>
        <div><input type="file" name="img" /></div>
        <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
        <input type="submit" name="button" value="complete"></div>
        <input type="hidden" name="question" value="%s" />
        <input type="hidden" name="title" value="%s" />
        <input type="hidden" name="account" value="%s" />
        </form></body></html>""" %(cgi.escape(question), cgi.escape(title), cgi.escape(account)))
    return

class MainPage(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        
        if user:
             account = user.nickname()
             greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" %
                        ( account,users.create_login_url("/")))
             self.response.out.write("<html><body>%s</body></html>" % greeting)
             self.response.out.write("""
              <form action="/sign" method="post">
               <input type="hidden" name="account" value=%s />
               <div><p><input type="radio" name="taskChoice" value="create a new survey" /> create a new survey<br />
               <input type="radio" name="taskChoice" value="edit your survey" /> edit your survey<br />
               <input type="radio" name="taskChoice" value="vote" /> vote<br />
               <input type="radio" name="taskChoice" value="view survey results" /> view survey results<br /></p></div>
               <div><p><input type="radio" name="taskChoice" value="change your votes" /> change your votes<br />
               <input type="radio" name="taskChoice" value="show Top 5 surveys" /> show Top 5 surveys<br />
               <input type="radio" name="taskChoice" value="search survey" /> search survey<br /></p><div>
               <input type="submit" name = "button" value="submit" />
              </form>"""%cgi.escape(account))
             
        else:
           greeting = ("<a href=\"%s\">Sign in or register</a>." %
                        users.create_login_url("/"))
           self.response.out.write("<html><body>%s</body></html>" % greeting)

class TaskChoice(webapp.RequestHandler):
    def post(self):
        taskChoice=self.request.get('taskChoice')
        account=self.request.get('account')

        if taskChoice=='':
             greeting = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" %
                        ( account,users.create_login_url("/")))
             self.response.out.write("<html><body>%s</body></html>" %greeting)
             self.response.out.write("<html><body><br /><br />You have to choose one option:</body></html>")
             self.response.out.write("""
              <form action="/sign" method="post">
               <input type="hidden" name="account" value=%s />
               <div><p><input type="radio" name="taskChoice" value="create a new survey" /> create a new survey<br />
               <input type="radio" name="taskChoice" value="edit your survey" /> edit your survey<br />
               <input type="radio" name="taskChoice" value="vote" /> vote<br />
               <input type="radio" name="taskChoice" value="view survey results" /> view survey results<br /></p></div>
               <div><p><input type="radio" name="taskChoice" value="change your votes" /> change your votes<br />
               <input type="radio" name="taskChoice" value="show Top 5 surveys" /> show Top 5 surveys<br />
               <input type="radio" name="taskChoice" value="search survey" /> search survey<br /></p><div>
               <input type="submit" name = "button" value="submit" />
              </form>"""%cgi.escape(account))
        else: 
          self.response.out.write('<html><body>%s, you choose to '%cgi.escape(account))
          self.response.out.write(cgi.escape(taskChoice))
          self.response.out.write('. <a href=\"/\">Back To Home Page</a><br /></body></html>')

        if taskChoice=="create a new survey":
          self.response.out.write("""
          <html>
            <body>
              <p><big> What's the title of the survey?</big></p> 
              <form action="/newSurvey" method="post">
                <div><textarea name="title" rows="3" cols="60"></textarea></div>
                <div> <input type="submit" name="button" value= "add a new question" /></div>
                 <input type="hidden" name="account" value=%s />
              </form>
            </body>
          </html>"""%cgi.escape(account))

        if taskChoice=="edit your survey":
            listsurveyTitlebyAccount(account,self,"")
        if taskChoice=="vote":
            listsurveyTitle(account,self,"vote","")
        if taskChoice=="view survey results":
            listsurveyTitle(account,self,"result","")
        if taskChoice=="change your votes":
            listsurveyTitle(account,self,"change","")
        if taskChoice=="show Top 5 surveys":
            listsurveyTitle(account,self,"popularity","")
        if taskChoice=="search survey":
            self.response.out.write("""
            <html><body>
            <form action="/searchSurvey" method="post">""")
            self.response.out.write("""Please give the input: </br>""")
            self.response.out.write("""<div><textarea name="searchInput" rows="1" cols="60"></textarea></div>""")
            self.response.out.write("""<div><input type="submit" name="button" value="search"></div>""")
            self.response.out.write("""
                      <input type="hidden" name="account" value="%s">
                      </form></body></html>""" %(cgi.escape(account)))
            
class UpdateText(webapp.RequestHandler):
     def post(self):
        account=self.request.get('account')
        title=self.request.get('title')
        question=self.request.get('question')
        option=self.request.get('option')
        newTitle=self.request.get('newTitle')
        newQuestion=self.request.get('newQuestion')
        newOption=self.request.get('newOption')
        choice=self.request.get('choice')
        picture=self.request.get('img')
        if choice=="update title":
            defsurvey_title(account,newTitle,"edit",title,self)
        if choice=="update question":
            defquestion(account,title,newQuestion,"edit",question,self)
        if choice=="update option":
            defoption_option(account,title,question,newOption,"edit",option,self,picture)

class CleanSurvey(webapp.RequestHandler):
     def post(self):
        account=self.request.get('account')
        title=self.request.get('title')
        opSelected=self.request.get('button')
        if title == "":
            listsurveyTitlebyAccount(account,self," You have to select a survey before selecting the operations.")
        else:
             self.response.out.write("""
                  <html>
                     <body>
                       <form action="/editTitle" method="post">
                       <p><big> You operation will cause the delete of all the statistical data for survey:%s </big></p>
                       <p><big> Continue?</big><input type="submit" name="clean" value="yes"> or <a href=\"/\">Back To Home Page</a></p>                     
                       <input type="hidden" name="title" value="%s" />
                       <input type="hidden" name="account" value="%s" />
                       <input type="hidden" name="button" value="%s" />
                      </form>
                    </body>
                 </html>""" %(cgi.escape(title), cgi.escape(title), cgi.escape(account),cgi.escape(opSelected)))
        
         
class EditTitle(webapp.RequestHandler):
     def post(self):
        account=self.request.get('account')
        opSelected=self.request.get('button')
        title=self.request.get('title')
        question=""
        votes = db.GqlQuery("SELECT * "
                            "FROM MyVote "
                            "WHERE author = :1 and title = :2",
                            account, title)
        db.delete(votes)
        vcs = db.GqlQuery("SELECT * "
                          "FROM VoteCount "
                          "WHERE account = :1 and title = :2", account, title)  
        db.delete(vcs)
        surveys = db.GqlQuery("SELECT * "
                            "FROM Survey "
                            "WHERE account = :1 and title = :2",
                            account, title)
        for survey in surveys:
            survey.count=0
            survey.put()
        
        if opSelected == "delete":
             surveys = db.GqlQuery("SELECT * "
                               "FROM Survey "
                               "WHERE account = :1 and title =:2", account,title
                              )
             db.delete(surveys)
             listsurveyTitlebyAccount(account,self," The survey is deleted.")
        if opSelected == "edit title":
             self.response.out.write("""
              <html>
                 <body>
                   <p><big> The title is about to be modified is:%s  </big><a href=\"/\">Back To Home Page</a></p>
                   <p><big> Please give the new title: </big></p>
                   <form action="/updateText" method="post">
                     <div><textarea name="newTitle" rows="3" cols="60"></textarea></div>
                     <div><input type="submit" name="button" value="submit"></div>
                          <input type="hidden" name="title" value="%s" />
                          <input type="hidden" name="account" value="%s" />
                          <input type="hidden" name="choice" value="update title" />
                  </form>
                </body>
             </html>""" %(cgi.escape(title), cgi.escape(title), cgi.escape(account)))
        if opSelected == "add question":
            defquestion(account,title,question,"create","",self)

        if opSelected == "edit question":
                listQbyAT(account,title,self,"")
                
class EditQuestion(webapp.RequestHandler):
     def post(self):
        account=self.request.get('account')
        opSelected=self.request.get('button')
        title=self.request.get('title')
        question = self.request.get('question')
        option = ""
        picture=""
        if question == "":
            listQbyAT(account,title,self," You have to select a question before selecting the operations")
        else:
            if opSelected == "delete":
                 questions = db.GqlQuery("SELECT * "
                                         "FROM Survey "
                                         "WHERE account = :1 and title =:2 and question =:3",account,title, question)
                 db.delete(questions)
                 listQbyAT(account,title,self," The question is deleted.")
            if opSelected == "edit question name":
                 self.response.out.write("""
                  <html>
                     <body>
                       <p><big> The question is about to be modified is:%s </big><a href=\"/\">Back To Home Page</a></p>
                       <p><big> Please give the new question: </big></p>
                       <form action="/updateText" method="post">
                         <div><textarea name="newQuestion" rows="3" cols="60"></textarea></div>
                         <div><input type="submit" name="button" value="submit"></div>
                              <input type="hidden" name="title" value="%s" />
                              <input type="hidden" name="question" value="%s" />
                              <input type="hidden" name="account" value="%s" />
                              <input type="hidden" name="choice" value="update question" />
                      </form>
                    </body>
                 </html>""" %(cgi.escape(question), cgi.escape(title), cgi.escape(question), cgi.escape(account)))
            if opSelected == "add option":
                defoption_question(account, title, question, option, self,picture)
                
            if opSelected == "edit option":
                listObyATQ(account,title,question,self,"")
                
class EditOption(webapp.RequestHandler):
     def post(self):
        account=self.request.get('account')
        opSelected=self.request.get('button')
        title=self.request.get('title')
        question = self.request.get('question')
        option = self.request.get('option')
        if option == "":
            listObyATQ(account,title,question,self,"You have to select an option before selecting the operations.")
        else:
            if opSelected == "delete":
                 options = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title =:2 and question =:3 and option =:4",
                                          account,title, question, option)
                 db.delete(options)
                 listObyATQ(account,title,question,self,"The option is deleted.")
                 
            if opSelected == "edit option name":
                  self.response.out.write("""
                  <html><body>
                  <p><big> The option is about to be modified is:%s </big><a href=\"/\">Back To Home Page</a></p>
                  <p><big> Please give the new option: </big></p>
                  <form action="/updateText" enctype="multipart/form-data" method="post">
                  <div><label>Message:</label></div>
                  <div><textarea name="newOption" rows="3" cols="60"></textarea></div>
                  <div><label>Picture:</label></div>
                  <div><input type="file" name="img"/></div>
                  <div><input type="submit" name="button" value="submit"></div>
                  <input type="hidden" name="title" value="%s" />
                  <input type="hidden" name="question" value="%s" />
                  <input type="hidden" name="option" value="%s" />
                  <input type="hidden" name="account" value="%s" />
                  <input type="hidden" name="choice" value="update option" />
                  </form></body></html>""" %(cgi.escape(option), cgi.escape(title), cgi.escape(question), cgi.escape(option), cgi.escape(account)))

class GetAuthor(webapp.RequestHandler):
    def post(self):
        title=self.request.get('title')
        flag=self.request.get('flag')
        voter=self.request.get('voter')
        if title=="":
           listsurveyTitle(voter,self,flag,"You have to choose one survey:")
        else:
           listAuthorbySurvey(self,voter,title,flag,"")

class DisplayResult(webapp.RequestHandler):
    def post(self):
        title=self.request.get('title')
        account=self.request.get('account')
        flag=self.request.get('flag')
        voter=self.request.get('voter')
        queIndex = 1
        if account=="":
           listAuthorbySurvey(self,voter,title,flag,"You have to choose one author:")
        else:
            if flag=="vote":
                listOptions(self,voter,title,account,flag,queIndex)
            if flag=="change":
                listOptions(self,voter,title,account,flag,queIndex)
            if flag=="result":
                surveys = db.GqlQuery("SELECT * "
                                      "FROM Survey "
                                      "WHERE title = :1 and account = :2", title, account)
                if surveys.count()!=0:
                    self.response.out.write("""
                    <html><body>
                    <p>View the results of a survey on the web:
                    The number indicates how many people vote the specified option in total.</p>""")
                    questions=getuniqlist(surveys,"question")
                    question_num=1
                    for element in questions:
                        self.response.out.write("""
                        <p><big>Q%s. %s</big><br \>""" %(question_num,cgi.escape(element)))
                        options = db.GqlQuery("SELECT * "
                                              "FROM Survey "
                                              "WHERE title = :1 and account = :2 and question = :3", title, account,element)
                        option_num=1
                        for item in options:
                            self.response.out.write("""
                              &nbsp &nbsp C%s. %s -- <big>%s people voted</big> """ %(option_num,cgi.escape(item.option),item.count))
                            if item.picture:
                                 self.response.out.write("<div><img src='img?img_id=%s'></img></div>" %item.key())
                            option_num=option_num+1
                            self.response.out.write("<br />")
                        self.response.out.write("</p>")
                        question_num=question_num+1
                    self.response.out.write("""<br />
                    <a href=\"/\">Back To Home Page</a>
                    </form></body></html>""")
                else:
                    self.response.out.write("""
                    <html><body>
                    <p><big> There is no question in the survey %s (%s).</big></p>
                    </body></html>""" %(cgi.escape(title),cgi.escape(account) ))

def changeOperation(voter,title,account,question,old_option,selectedOption):
    options = db.GqlQuery("SELECT * "
                          "FROM MyVote "
                         "WHERE account = :1 and title = :2 and author = :3 and question = :4 and option=:5",voter, title,account,question,old_option)
    db.delete(options)
    answer=MyVote(account=voter,
                  author=account,
                  title=title,
                  question=question,
                  option=selectedOption)
    db.put(answer)

    options = db.GqlQuery("SELECT * "
                          "FROM Survey "
                          "WHERE account = :1 and title = :2 and question = :3 and option=:4",account, title,question,old_option)
    for option in options:
        option.count=option.count-1
        option.put()
    options = db.GqlQuery("SELECT * "
                          "FROM Survey "
                          "WHERE account = :1 and title = :2 and question = :3 and option=:4",account, title,question,selectedOption)
    for option in options:
        option.count=option.count+1
        option.put()
    return

class AddComment(webapp.RequestHandler):
    def post(self):
        title=self.request.get('title')
        content=self.request.get('comment')
        account=self.request.get('account')
        voter=self.request.get('voter')
        operation=self.request.get('button')
        if content!="":
            comm=Comment(account=voter,
                         title=title,
                         author=account,
                         content=content)
            db.put(comm)
        if operation =="submit":
            self.response.out.write("""<html><body><form action="/addComment" method="post">""")
            self.response.out.write("""Would you like to read all the comments? Or <a href=\"/\">Back To Home Page</a></br>""")
            self.response.out.write("""<div><input type="submit" name="button" value="yes"></div>""")
            self.response.out.write("""
                      <input type="hidden" name="voter" value="%s">
                      <input type="hidden" name="title" value="%s">
                      <input type="hidden" name="account" value="%s">
                      </form></body></html>""" %(cgi.escape(voter),cgi.escape(title),cgi.escape(account)))
        if operation =="yes":
             comments=db.GqlQuery("SELECT * "
                                  "FROM  Comment "
                                  "WHERE title = :1 and author = :2",
                                  title, account)
             for comment in comments:
                 self.response.out.write("""%s(%s):%s</br>"""%(cgi.escape(comment.account), comment.date, cgi.escape(comment.content)))
             self.response.out.write("""<a href=\"/\">Back To Home Page</a></br>""")
                
class VoteOptions(webapp.RequestHandler):
    def post(self):
        title=self.request.get('title')
        account=self.request.get('account')
        question=self.request.get('question')
        flag=self.request.get('flag')
        voter=self.request.get('voter')
        queIndex = self.request.get('index')
        old_option = self.request.get('old option')
        voteOp = self.request.get('button')
        selectedOption = self.request.get('option')

        if voteOp =="skip to the end":
            self.response.out.write("""
            Thank you for voting!  <a href=\"/\">Back To Home Page</a></br>""")
            printVoteResult(voter, title, account,self)

        if voteOp == "next":
                index=int(queIndex)+1
                listOptions(self,voter,title,account,flag,index)

        if voteOp == "change":
            if selectedOption == "":
                listOptions(self,voter,title,account,flag,queIndex)  
            else:
                changeOperation(voter,title,account,question,old_option,selectedOption)
                self.response.out.write("""
                Your answer changed!  <a href=\"/\">Back To Home Page</a></br>""")
                printVoteResult(voter, title, account,self)   

        if voteOp == "change and next":
            if selectedOption == "":
                listOptions(self,voter,title,account,flag,queIndex)  
            else:
                changeOperation(voter,title,account,question,old_option,selectedOption)
                index=int(queIndex)+1
                listOptions(self,voter,title,account,flag,index)
                
        if voteOp == "next question":
            if selectedOption == "":
                listOptions(self,voter,title,account,flag,queIndex)  
            else:
                 questions = db.GqlQuery("SELECT * "
                                      "FROM MyVote "
                                      "WHERE account = :1 and title = :2 and question =:3 and author = :4",
                                       voter, title, question, account)
                 if questions.count()!=0:
                      self.response.out.write("""
                       <html><body>You have voted for question: %s</br>
                       <form action="/voteOptions" method="post">"""%cgi.escape(question))
                      index=int(queIndex)+1
                      self.response.out.write("""<div><input type="submit" name="button" value="next question">
                                           <input type="submit" name="button" value="skip to the end"></div>""")
                      self.response.out.write("""
                      <input type="hidden" name="voter" value="%s">
                      <input type="hidden" name="title" value="%s">
                      <input type="hidden" name="account" value="%s">
                      <input type="hidden" name="question" value="%s">
                      <input type="hidden" name="index" value="%s">
                      <input type="hidden" name="flag" value="%s">
                      </form></body></html>""" %(cgi.escape(voter),cgi.escape(title),cgi.escape(account),cgi.escape(question),index,flag))
                 else:
                      vs = MyVote(account=voter,
                            author=account,
                            title=title,
                            question=question,
                            option=selectedOption,
                            )
                      db.put(vs)
                      surveys = db.GqlQuery("SELECT * "
                                      "FROM Survey "
                                      "WHERE account = :1 and title = :2 and question =:3 and option =:4",
                                       account, title, question, selectedOption)
                      for survey in surveys:
                          survey.count=survey.count+1
                          survey.put()
                      index=int(queIndex)+1
                      listOptions(self,voter,title,account,flag,index)
                    
class SearchSurvey(webapp.RequestHandler):
    def post(self):
        account=self.request.get('account')
        input=self.request.get("seachInput")
        query = Survey.all().search(input)
        for q in query:
              self.response.out.write("""
              <html><body><p>survey:%s</p>
              <p>question:%s</p>
              <p>option:%s</p>
              <p>voted times for the option:%s</p>
              <p>author:%s</br>
              -------------------------------------------</p>
              </html></body>"""%(cgi.escape(q.title), cgi.escape(q.question),
              cgi.escape(q.option),q.count,cgi.escape(q.account)))
                                                    
class CreateSurvey(webapp.RequestHandler):
    def post(self):
        account=self.request.get('account')
        queOrChoi=self.request.get('button')
        title=self.request.get('title')
        question=self.request.get('question')
        option=self.request.get('option')
        picture=self.request.get("img")
        if queOrChoi == "add a new question":
            defsurvey_title(account,title,"create","",self)
        if queOrChoi == "add an option":
            defquestion(account,title,question,"create","",self)
        if queOrChoi == "next question":
            defoption_question(account,title,question,option,self,picture)
        if queOrChoi == "next option":
            defoption_option(account,title,question,option,"create","",self,picture)
        if queOrChoi == "complete":
            defoption_complete(account,title,question,option,self,picture)


class Image(webapp.RequestHandler):
    def get(self):
        surveys = db.get(self.request.get("img_id"))
        if surveys.picture:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(surveys.picture)
            #  else:
            #self.response.out.write("No image")
                        
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/img', Image),
                                      ('/sign', TaskChoice),
                                       ('/newSurvey', CreateSurvey),
                                       ('/editTitle', EditTitle),
                                       ('/editQuestion', EditQuestion),
                                       ('/editOption', EditOption),
                                       ('/updateText', UpdateText),
                                       ('/getauthor',GetAuthor),
                                       ('/cleanSurvey',CleanSurvey),
                                       ('/displayresult',DisplayResult),
                                       ('/voteOptions',VoteOptions),
                                       ('/addComment',AddComment),
                                       ('/searchSurvey',SearchSurvey)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
