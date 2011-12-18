import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Survey(db.Model):
    account = db.StringProperty()
    title = db.StringProperty()
    question = db.StringProperty()
    option = db.StringProperty()
    count = db.IntegerProperty()
    
class MyVote(db.Model):
    account = db.StringProperty()
    title = db.StringProperty()
    question = db.StringProperty()
    option = db.StringProperty()
    author = db.StringProperty()
    
class VoteCount(db.Model):
    account = db.StringProperty()
    title = db.StringProperty()
    count = db.IntegerProperty()
    
    
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
        results = db.GqlQuery("SELECT * "
                            "FROM MyVote "
                            "WHERE account = :1 and title = :2 and author =:3", voter, title, account)
        self.response.out.write("""<font size=5>%s(%s)</font></br>"""%(title, account))
        qNum=1
        for result in results:
             self.response.out.write("""Q%s. %s</br>"""%(qNum,result.question))
             self.response.out.write("""&nbsp &nbsp  %s</br>"""%result.option)
             qNum=qNum+1
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
         self.response.out.write(""" <font size=5>Q%s. %s</font>"""%(queIndex,curQ))
         options =  db.GqlQuery("SELECT * "
                                "FROM Survey "
                                "WHERE account = :1 and title = :2 and question = :3", account, title, curQ)
         optionlist= getuniqlist(options, "option")
         oNum=1;
         for option in optionlist:
              self.response.out.write("""
              <div><input type="radio" name = "option", value="%s"/><font size = 4>C%s.%s</font></div>"""%(option,oNum,option))
              oNum=oNum+1
         self.response.out.write("""<div><input type="submit" name="button" value="next question">
                                           <input type="submit" name="button" value="skip to the end"></div>""")
         self.response.out.write("""
                      <input type="hidden" name="voter" value="%s">
                      <input type="hidden" name="title" value="%s">
                      <input type="hidden" name="account" value="%s">
                      <input type="hidden" name="question" value="%s">
                      <input type="hidden" name="index" value="%s">
                      <input type="hidden" name="flag" value="%s">
                      </form></body></html>""" %(voter,title,account,curQ,queIndex,flag))
 
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
            %s  <a href=\"/\">Back To Home Page</a>""" %ErrorMsg)

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
        account_num=1
        for entry in newlist:
            self.response.out.write("""
            <div><input type="radio" name = "account", value="%s"/><font size = 4>Author %s. %s</font></div>"""%(entry, account_num, entry))
            account_num=account_num+1

        self.response.out.write("""
        <input type="hidden" name="title" value= "%s" />"""%title)
        if flag=="vote":
            self.response.out.write("""
            <input type="submit" name="button" value= "vote" />""")
        if flag=="result":
            self.response.out.write("""
            <input type="submit" name="button" value= "result" />""")

        self.response.out.write("""
        <input type="hidden" name="title" value= "%s" />
        <input type="hidden" name="flag" value=  "%s" />
        <input type="hidden" name="voter" value="%s" />
        </form></body></html>"""%(title,flag,voter))
    else:
        self.response.out.write("""
        <html><body>
        <p><big> There is no survey created.</big></p>
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
        <form action="/editTitle" method="post">""")

        if ErrorMsg!="":
            self.response.out.write("""
            %s  <a href=\"/\">Back To Home Page</a>""" %ErrorMsg)

        newlist=getuniqlist(surveys,"title")
        title_num=1
        for entry in newlist:
            self.response.out.write("""
            <div><input type="radio" name = "title", value="%s"/><font size = 4>No. %s. %s</font></div>"""%(entry, title_num, entry))
            title_num=title_num+1

        self.response.out.write("""
        <input type="submit" name="button" value= "delete" />
        <input type="submit" name="button" value= "edit title" />
        <input type="submit" name="button" value= "add question" />
        <input type="submit" name="button" value= "edit question" />
        <input type="hidden" name="account" value= "%s" />"""%account)

        self.response.out.write(""" </form>""")
        self.response.out.write(""" </body></html>""")
    else:
        self.response.out.write("""
        <html><body>
        <p><big> There is no survey created.</big></p>
        </body></html>""" )
    return

#list all uniq survey
def listsurveyTitle(voter,self,flag,ErrorMsg):
    surveys = db.GqlQuery("SELECT * "
                          "FROM Survey ")
    
    if surveys.count()!=0:
        self.response.out.write("""
        <html><body>
        <form action="/getauthor" method="post">""")

        if ErrorMsg!="":
            self.response.out.write("""
            %s  <a href=\"/\">Back To Home Page</a>""" %ErrorMsg)         

        newlist=getuniqlist(surveys,"title")
        if flag=="vote":
            votedSurveys = db.GqlQuery("SELECT * "
                          "FROM MyVote "
                          "WHERE account = :1", voter)
            if votedSurveys.count()!=0:
                #print "%s"%votedSurveys.count() 
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
            <div><input type="radio" name = "title", value="%s"/><font size = 4>No.%s %s</font></div>"""%(entry, title_num, entry))
            title_num=title_num+1

        if flag=="vote":
            if newlist==[]:
                self.response.out.write(""" <p><big> You have finished all the surveys.""")
            else:
                self.response.out.write("""
                <input type="submit" name="button" value= "vote" />""")    
        if flag=="result":
            self.response.out.write("""
            <input type="submit" name="button" value= "result" />""")

        self.response.out.write("""
        <input type="hidden" name="voter" value="%s">
        <input type="hidden" name="flag" value="%s">
        </form></body></html>""" %(voter,flag))
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
        <p><big>The survey title is %s. </big><a href=\"/\">Back To Home Page</a></p>""" %title)

        if ErrorMsg!="":
            self.response.out.write("""
            %s""" %ErrorMsg)

        newlist=getuniqlist(questions,"question")
        question_num=1
        for entry in newlist:
            self.response.out.write("""
            <div><input type="radio" name = "question", value="%s"/><font size = 4>Q%s. %s</font></div>"""%(entry, question_num, entry))
            question_num=question_num+1

        self.response.out.write("""
        <input type="submit" name="button" value= "delete" />
        <input type="submit" name="button" value= "edit question name" />
        <input type="submit" name="button" value= "add option" />
        <input type="submit" name="button" value= "edit option" />
        <input type="hidden" name="account" value= "%s" />
        <input type="hidden" name="title" value= "%s" /> """%(account,title))

        self.response.out.write(""" </form>""")
        self.response.out.write(""" </body></html>""")
    else:
        self.response.out.write("""
        <html><body>
        <p><big> There is no questions in the survey %s.</big></p>
        </body></html>""" % title )
    return

#list all the uniq option name belong to the login account&&specified title$$specified question:
def listObyATQ(account,title,question,self,ErrorMsg):
    options = db.GqlQuery("SELECT * "
                          "FROM Survey "
                          "WHERE account = :1 and title = :2 and question = :3", account,title,question)
    if options.count()!=0:
        self.response.out.write("""
        <html><body>
        <form action="/editOption" method="post">
        <p><big>%s - %s </big><a href=\"/\">Back To Home Page</a></p>""" %(title,question))

        if ErrorMsg!="":
            self.response.out.write("""
            %s""" %ErrorMsg)

        newlist=getuniqlist(options,"option")
        option_num=1
        for entry in newlist:
            self.response.out.write("""
            <div><input type="radio" name = "option", value="%s"/><font size = 4>Q%s. %s</font></div>"""%(entry, option_num, entry))
            option_num=option_num+1

        self.response.out.write("""
        <input type="submit" name="button" value= "delete" />
        <input type="submit" name="button" value= "edit option name" />
        <input type="hidden" name="account" value= "%s" />
        <input type="hidden" name="title" value= "%s" />
        <input type="hidden" name="question" value="%s" /> """%(account,title,question))

        self.response.out.write(""" </form>""")
        self.response.out.write(""" </body></html>""")
    else:
        self.response.out.write("""
        <html><body>
        <p><big> There is no option in the survey (%s) for this question (%s).</big></p>
        </body></html>""" % (title,question) )
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
                </form></body></html>""" % (title,title,account))
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
            </form></body></html>""" % (errorMsg, account))
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
            </form></body></html>""" %(old_title, errorMsg,old_title, account))
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
                <form action="/newSurvey" method="post">
                <div><textarea name="option" rows="3" cols="60"></textarea></div>
                <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
                <input type="submit" name="button" value="complete"></div>
                <input type="hidden" name="question" value="%s" />
                <input type="hidden" name="title" value="%s" />
                <input type="hidden" name="account" value="%s" />
                </form></body></html>""" % (title,question, question, title, account))
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
            <p><big> %s</big></p>
            <form action="/newSurvey" method="post">
            <div><textarea name="question" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="add an option"></div>
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />
            </form></body></html>""" % (errorMsg,title, account))
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
            </form></body></html>""" %(old_question,errorMsg, title, old_question, account))
    return

def defoption_question(account,title,question,option,self):
    errorMsg=""
    if option != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2 and question = :3 and option = :4", account, title, question, option)
        if existSurvey.count() == 0:
            s = Survey(account=account,
                        title=title,
                        question=question,
                        option=option,
                        count=0)
            db.put(s)
            vc = VoteCount(account=account,
                           title=title,
                           count=0)
            db.put(vc)
            self.response.out.write("""
            <html><body>
            <p><big> Add a question for survey: "%s"</big></p> 
            <form action="/newSurvey" method="post">"""%title)
            sets = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2", account, title)
            newlist=getuniqlist(sets,"question")
            num=1
            for entry in newlist:
                self.response.out.write("""
                <p>Q%s. %s</p>""" %(num,entry))
                num=num+1
            self.response.out.write("""
            <div><textarea name="question" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="add an option"></div>
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />
            </form></body></html>""" %(title,account))
        else:
            errorMsg="The option you input exists! Please input another one:"
    else:
        errorMsg="Please give the option:"
    if errorMsg!="":
        self.response.out.write("""
        <html><body>
        <p><big> %s</big></p> 
        <form action="/newSurvey" method="post">""" %errorMsg)
        sets = db.GqlQuery("SELECT * "
                            "FROM Survey "
                            "WHERE account = :1 and title = :2 and question = :3", account, title, question)
        num=1
        for entry in sets:
            self.response.out.write("""
            <p>C%s. %s</p>""" %(num,entry.option))
            num=num+1
        self.response.out.write("""
        <div><textarea name="option" rows="3" cols="60"></textarea></div>
        <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
        <input type="submit" name="button" value="complete"></div>
        <input type="hidden" name="question" value="%s" />
        <input type="hidden" name="title" value="%s" />
        <input type="hidden" name="account" value="%s" />
        </form></body></html>""" % (question, title, account))
    return

def defoption_option(account,title,question,option,flag,old_option,self):
    errorMsg=""
    if option != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2 and question = :3 and option = :4", account, title, question, option)
        if existSurvey.count() == 0:
            if flag=="create":
                s = Survey(account=account,
                           title=title,
                           question=question,
                           option=option,
                           count=0)
                db.put(s)
                vc = VoteCount(account=account,
                           title=title,
                           count=0)
                db.put(vc)

                self.response.out.write("""
                <html><body>
                <p><big> Add a option for question "%s--%s":</big></p>
                <form action="/newSurvey" method="post">""" %(title,question))
                sets = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title = :2 and question = :3", account, title, question)
                num=1
                for entry in sets:
                    self.response.out.write("""
                    <p>C%s. %s</p>""" %(num,entry.option))
                    num=num+1
                self.response.out.write("""
                <div><textarea name="option" rows="3" cols="60"></textarea></div>
                <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
                <input type="submit" name="button" value="complete"></div>
                <input type="hidden" name="question" value="%s" />
                <input type="hidden" name="title" value="%s" />
                <input type="hidden" name="account" value="%s" />     
                </form></body></html>""" %(question, title, account))
            if flag=="edit":
                surveys = db.GqlQuery("SELECT * "
                                      "FROM Survey "
                                      "WHERE account = :1 and title = :2 and question =:3 and option = :4",
                                      account, title, question, old_option)
                for survey in surveys:
                    survey.option=option
                    survey.put()
                listObyATQ(account,title,question,self,"The option name is updated.")
        else:
            errorMsg="The option you input exists! Please input another one:"
    else:
        errorMsg="Please give the option:"
    if errorMsg!="":
        if flag=="create":
            self.response.out.write("""
            <html><body>
            <p><big> %s</big></p> 
            <form action="/newSurvey" method="post">""" %errorMsg)
            sets = db.GqlQuery("SELECT * "
                               "FROM Survey "
                               "WHERE account = :1 and title = :2 and question = :3", account, title, question)
            num=1
            for entry in sets:
                self.response.out.write("""
                <p>C%s. %s</p>""" %(num,entry.option))
                num=num+1
            self.response.out.write("""
            <div><textarea name="option" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
            <input type="submit" name="button" value="complete"></div>
            <input type="hidden" name="question" value="%s" />
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />
            </form></body></html>""" %(question, title, account))
        if flag=="edit":
            self.response.out.write("""
            <html><body>
            <p><big> The option is about to be modified is:%s </big><a href=\"/\">Back To Home Page</a></p>
            <p><big> %s </big></p>
            <form action="/updateText" method="post">
            <div><textarea name="newOption" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="submit"></div>
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="question" value="%s" />
            <input type="hidden" name="option" value="%s" />
            <input type="hidden" name="account" value="%s" />
            <input type="hidden" name="choice" value="update option" />
            </form></body></html>""" %(option,errorMsg, title, question, old_option, account))
    return

def defoption_complete(account,title,question,option,self):
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

            s = Survey(account=account,
                      title=title,
                      question=question,
                      option=option,
                      count=0)
            db.put(s)
            vc = VoteCount(account=account,
                           title=title,
                           count=0)
            db.put(vc)
        else:
            errorMsg="The option you input exists! Please input another one:"
    else:
        errorMsg="You can not leave the option as blank. What's the option"
    if errorMsg!="":
        self.response.out.write("""
        <html><body>
        <p><big> %s</big></p> 
        <form action="/newSurvey" method="post">""" %errorMsg)
        sets = db.GqlQuery("SELECT * "
                            "FROM Survey "
                            "WHERE account = :1 and title = :2 and question = :3", account, title, question)
        num=1
        for entry in sets:
            self.response.out.write("""
            <p>C%s. %s</p>""" %(num,entry.option))
            num=num+1
        self.response.out.write("""
        <div><textarea name="option" rows="3" cols="60"></textarea></div>
        <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
        <input type="submit" name="button" value="complete"></div>
        <input type="hidden" name="question" value="%s" />
        <input type="hidden" name="title" value="%s" />
        <input type="hidden" name="account" value="%s" />
        </form></body></html>""" %(question, title, account))
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
               <input type="radio" name="taskChoice" value="create a new survey" /> create a new survey<br />
               <input type="radio" name="taskChoice" value="edit your survey" /> edit your survey<br />
               <input type="radio" name="taskChoice" value="vote" /> vote<br />
               <input type="radio" name="taskChoice" value="view survey results" /> view survey results<br />
                <input type="radio" name="taskChoice" value="change your votes" /> change your votes<br />
               <input type="submit" name = "button" value="submit" />
              </form>"""%account)
             
        else:
           greeting = ("<a href=\"%s\">Sign in or register</a>." %
                        users.create_login_url("/"))
           self.response.out.write("<html><body>%s</body></html>" % greeting)

class TaskChoice(webapp.RequestHandler):
    def post(self):
        taskChoice=self.request.get('taskChoice')
        account=self.request.get('account')

        if taskChoice=='':
             self.response.out.write("<html><body>You have to choose one option:</body></html>")
             self.response.out.write("""
              <form action="/sign" method="post">
               <input type="hidden" name="account" value=%s />
               <input type="radio" name="taskChoice" value="create a new survey" /> create a new survey<br />
               <input type="radio" name="taskChoice" value="edit your survey" /> edit your survey<br />
               <input type="radio" name="taskChoice" value="vote" /> vote<br />
               <input type="radio" name="taskChoice" value="view survey results" /> view survey results<br />
               <input type="radio" name="taskChoice" value="change your votes" /> change your votes<br />
               <input type="submit" name = "button" value="submit" />
              </form>"""%account)
        else: 
          self.response.out.write('<html><body>%s, you choose to '%account)
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
          </html>"""%account)

        if taskChoice=="edit your survey":
            listsurveyTitlebyAccount(account,self,"")
        if taskChoice=="vote":
            listsurveyTitle(account,self,"vote","")
        if taskChoice=="view survey results":
            listsurveyTitle(account,self,"result","")
            
        ## if taskChoice=="change your votes":
            
            
       # else if taskChoice=="view survey results":
        #else:
            
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
        if choice=="update title":
            defsurvey_title(account,newTitle,"edit",title,self)
        if choice=="update question":
            defquestion(account,title,newQuestion,"edit",question,self)
        if choice=="update option":
            defoption_option(account,title,question,newOption,"edit",option,self)
            
class EditTitle(webapp.RequestHandler):
     def post(self):
        account=self.request.get('account')
        opSelected=self.request.get('button')
        title=self.request.get('title')
        question=""
        if title == "":
            listsurveyTitlebyAccount(account,self," You have to select a survey before selecting the operations.")                             
        else:
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
                 </html>""" %(title, title, account))
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
                 </html>""" %(question, title, question, account))
            if opSelected == "add option":
                defoption_question(account, title, question, option, self)
                
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
                  <html>
                     <body>
                       <p><big> The option is about to be modified is:%s </big><a href=\"/\">Back To Home Page</a></p>
                       <p><big> Please give the new option: </big></p>
                       <form action="/updateText" method="post">
                         <div><textarea name="newOption" rows="3" cols="60"></textarea></div>
                         <div><input type="submit" name="button" value="submit"></div>
                              <input type="hidden" name="title" value="%s" />
                              <input type="hidden" name="question" value="%s" />
                              <input type="hidden" name="option" value="%s" />
                              <input type="hidden" name="account" value="%s" />
                              <input type="hidden" name="choice" value="update option" />
                      </form>
                    </body>
                 </html>""" %(option, title, question, option, account))

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
                        <p><big>Q%s. %s</big><br \>""" %(question_num,element))
                        options = db.GqlQuery("SELECT * "
                                              "FROM Survey "
                                              "WHERE title = :1 and account = :2 and question = :3", title, account,element)
                        option_num=1
                        for item in options:
                            self.response.out.write("""
                              C%s. %s   --   %s<br \>""" %(option_num,item.option,item.count))
                            option_num=option_num+1
                        self.response.out.write("</p>")
                    self.response.out.write("""<br />
                    <a href=\"/\">Back To Home Page</a>
                    </form></body></html>""")
                else:
                    self.response.out.write("""
                    <html><body>
                    <p><big> There is no question in the survey %s (%s).</big></p>
                    </body></html>""" %(title,account) )

                
class VoteOptions(webapp.RequestHandler):
    def post(self):
        title=self.request.get('title')
        account=self.request.get('account')
        question=self.request.get('question')
        flag=self.request.get('flag')
        voter=self.request.get('voter')
        queIndex = self.request.get('index')
        voteOp = self.request.get('button')
        selectedOption = self.request.get('option')
        if voteOp =="skip to the end":
            self.response.out.write("""
            Thank you for voting!  <a href=\"/\">Back To Home Page</a></br>""")
            printVoteResult(voter, title, account,self)   
        if voteOp == "next question":
            if selectedOption == "":
                listOptions(self,voter,title,account,flag,queIndex)  
            else:
                 vs = MyVote(account=voter,
                            author=account,
                            title=title,
                            question=question,
                            option=selectedOption,
                            )
                 db.put(vs)
                 titles = db.GqlQuery("SELECT * "
                                      "FROM VoteCount "
                                      "WHERE account = :1 and title = :2",
                                       account, title)
                 for tt in titles:
                     tt.count=tt.count+1
                     tt.put()
                 
                 surveys = db.GqlQuery("SELECT * "
                                      "FROM Survey "
                                      "WHERE account = :1 and title = :2 and question =:3 and option =:4",
                                       account, title, question, selectedOption)
                 for survey in surveys:
                    survey.count=survey.count+1
                    survey.put()
                 index=int(queIndex)+1
                 listOptions(self,voter,title,account,flag,index)
                                           
class CreateSurvey(webapp.RequestHandler):
    def post(self):
        account=self.request.get('account')
        queOrChoi=self.request.get('button')
        title=self.request.get('title')
        question=self.request.get('question')
        option=self.request.get('option')
        if queOrChoi == "add a new question":
            defsurvey_title(account,title,"create","",self)
        if queOrChoi == "add an option":
            defquestion(account,title,question,"create","",self)
        if queOrChoi == "next question":
            defoption_question(account,title,question,option,self)
        if queOrChoi == "next option":
            defoption_option(account,title,question,option,"create","",self)
        if queOrChoi == "complete":
            defoption_complete(account,title,question,option,self)
                        
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', TaskChoice),
                                       ('/newSurvey', CreateSurvey),
                                       ('/editTitle', EditTitle),
                                       ('/editQuestion', EditQuestion),
                                       ('/editOption', EditOption),
                                       ('/updateText', UpdateText),
                                       ('/getauthor',GetAuthor),
                                       ('/displayresult',DisplayResult),
                                       ('/voteOptions',VoteOptions)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
