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
               <input type="radio" name="taskChoice" value="view survey results " /> view survey results<br />
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
               <input type="radio" name="taskChoice" value="view survey results " /> view survey results<br />
               <input type="submit" name = "button" value="submit" />
              </form>"""%account)
        else: 
          self.response.out.write('<html><body>%s, you choose to '%account)
          self.response.out.write(cgi.escape(taskChoice))
          self.response.out.write('.<br /></body></html>')

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
             surveys = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1", account
                                  )
             if surveys.count()!=0:
                 self.response.out.write(""" <html><body>""")
                 self.response.out.write(""" <form action="/editTitle" method="post">""")
                 curTitle=""
                 titleNum=0             
                 for survey in surveys:
                     if curTitle!=survey.title:
                         curTitle=survey.title
                         titleNum=titleNum+1
                         self.response.out.write("""<div>
                         <input type="radio" name = "title", value="%s"/>
                         <font size = 4>No. %s. %s</font>
                         </div>"""%(curTitle, titleNum, curTitle))
                     ## if curQuestion!=survey.question:
                 ##         curQuestion=survey.question
                 ##         questionNum=questionNum+1
                 ##         optionNum=0
                 ##         tq= [str(curTitle), str(curQuestion)] 
                 ##         self.response.out.write("""<div>                          
                 ##          &nbsp &nbsp <font size = 5><input type="radio" name = "question", value="%s"/>Q%s. %s</font>
                 ##          </div>"""%(tq, questionNum, curQuestion))
                 ##     optionNum=optionNum+1
                 ##     tqc= [str(curTitle), str(curQuestion), str(survey.option)]
                 ##     self.response.out.write("""<div>&nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp <input type="radio" name = "question", value=%s/> C%s. %s
                 ##     </div>"""%(tqc, optionNum, survey.option)) 
                 self.response.out.write(""" <input type="submit" name="button" value= "delete" />
                         <input type="submit" name="button" value= "edit" />
                         <input type="submit" name="button" value= "add a new question" />
                         <input type="submit" name="button" value= "edit questions" />
                         <input type="hidden" name="account" value= "%s" />"""%account)    
                 self.response.out.write(""" </form>""")
                 self.response.out.write(""" </body></html>""")
             else:
                 self.response.out.write("""
                   <html>
                   <body>
                     <p><big> There is no survey created.</big></p>
                     <a href=\"/\">Back To Home Page</a>
                   </body>
                   </html>""" )
                 
            
       # else if taskChoice=="view survey results":
        #else:

class UpdateText(webapp.RequestHandler):
     def post(self):
        #print "asdsa"
        account=self.request.get('account')
        title=self.request.get('title')
        question=self.request.get('question')
        option=self.request.get('option')
        newTitle=self.request.get('newTitle')
        newQuestion=self.request.get('newQuestion')
        newOption=self.request.get('newOption')
        if newTitle!="":
             surveys = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title = :2", account, title
                                  )
             for survey in surveys:
                 survey.title=newTitle
                 survey.put()
        if newQuestion!="":
             surveys = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title = :2 and question =:3", account, title, question
                                  )
             for survey in surveys:
                 survey.question=newQuestion
                 survey.put()
        if newOption!="":
             surveys = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title = :2 and question =:3 and option = :4",
                                    account, title, question, option
                                  )
             for survey in surveys:
                 survey.option=newOption
                 survey.put()
        self.response.out.write("""
                   <html>
                   <body>
                     <p><big> The survey is updated.</big></p>
                     <a href=\"/\">Back To Home Page</a>
                   </body>
                   </html>""" )
             
class EditTitle(webapp.RequestHandler):
     def post(self):
        account=self.request.get('account')
        opSelected=self.request.get('button')
        title=self.request.get('title')
        if title == "":
            surveys = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1", account
                                  )
            self.response.out.write(""" <html><body>""")
            self.response.out.write(""" You have to select a survey before selecting the operations.""")
            self.response.out.write(""" <form action="/editTitle" method="post">""")
            curTitle=""
            titleNum=0             
            for survey in surveys:
               if curTitle!=survey.title:
                         curTitle=survey.title
                         titleNum=titleNum+1
                         self.response.out.write("""<div>
                         <input type="radio" name = "title", value="%s"/>
                         <font size = 4>No. %s. %s</font>
                         </div>"""%(curTitle, titleNum, curTitle))
            self.response.out.write(""" <input type="submit" name="button" value= "delete" />
                         <input type="submit" name="button" value= "edit" />
                         <input type="submit" name="button" value= "add a new question" />
                         <input type="submit" name="button" value= "edit questions" />
                         <input type="hidden" name="account" value= "%s" />"""%account)
            self.response.out.write(""" </form>""")
            self.response.out.write(""" </body></html>""")
                             
        else:
            if opSelected == "delete":
                 surveys = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title =:2", account,title
                                  )
                 db.delete(surveys)
                 self.response.out.write("""
                   <html>
                   <body>
                     <p><big> The survey is deleted.</big></p>
                     <a href=\"/\">Back To Home Page</a>
                   </body>
                   </html>""" )
            if opSelected == "edit":
                 self.response.out.write("""
                  <html>
                     <body>
                       <p><big> The title is about to be modified is:%s </big></p>
                       <p><big> Please give the new title: </big></p>
                       <form action="/updateText" method="post">
                         <div><textarea name="newTitle" rows="3" cols="60"></textarea></div>
                         <div><input type="submit" name="button" value="submit"></div>
                              <input type="hidden" name="title" value="%s" />
                              <input type="hidden" name="account" value="%s" />
                      </form>
                    </body>
                 </html>""" %(title, title, account))
            if opSelected == "add a new question":
                 print '%s'%title
            if opSelected == "edit questions":
                self.response.out.write(""" <html><body>""")
                self.response.out.write(""" <form action="/editQuestion" method="post">""")
                curQuestion=""
                questionNum=0   
                questions = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title =  :2", account, title
                                  )
                for question in questions:
                     if curQuestion!=question.question:
                         curQuestion=question.question
                         questionNum=questionNum+1
                         self.response.out.write("""<div>
                         <input type="radio" name = "question", value="%s"/>
                         <font size = 4>Q%s. %s</font>
                         </div>"""%(curQuestion, questionNum, curQuestion))
                self.response.out.write(""" <input type="submit" name="button" value= "delete" />
                         <input type="submit" name="button" value= "edit" />
                         <input type="submit" name="button" value= "add an option" />
                         <input type="submit" name="button" value= "edit options" />
                         <input type="hidden" name="account" value= "%s" />
                         <input type="hidden" name="title" value= "%s" />"""%(account,title))    
                self.response.out.write(""" </form>""")
                self.response.out.write(""" </body></html>""")
                
class EditQuestion(webapp.RequestHandler):
     def post(self):
        account=self.request.get('account')
        opSelected=self.request.get('button')
        title=self.request.get('title')
        question = self.request.get('question')
        if question == "":
            questions = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title = :2", account, title
                                  )
            self.response.out.write(""" <html><body>""")
            self.response.out.write(""" You have to select a question before selecting the operations.""")
            self.response.out.write(""" <form action="/editQuestion" method="post">""")
            curQuestion=""
            questionNum=0             
            for question in questions:
               if curQuestion!=question.question:
                         curQuestion=question.question
                         questionNum=questionNum+1
                         self.response.out.write("""<div>
                         <input type="radio" name = "question", value="%s"/>
                         <font size = 4>Q. %s. %s</font>
                         </div>"""%(curQuestion, questionNum, curQuestion))
            self.response.out.write(""" <input type="submit" name="button" value= "delete" />
                         <input type="submit" name="button" value= "edit" />
                         <input type="submit" name="button" value= "add an option" />
                         <input type="submit" name="button" value= "edit options" />
                         <input type="hidden" name="account" value= "%s" />
                         <input type="hidden" name="title" value= "%s" />"""%(account, title))
            self.response.out.write(""" </form>""")
            self.response.out.write(""" </body></html>""")
                             
        else:
            if opSelected == "delete":
                 questions = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title =:2 and question =:3",
                                          account,title, question
                                  )
                 db.delete(questions)
                 self.response.out.write("""
                   <html>
                   <body>
                     <p><big> The question is deleted.</big></p>
                     <a href=\"/\">Back To Home Page</a>
                   </body>
                   </html>""" )
            if opSelected == "edit":
                 self.response.out.write("""
                  <html>
                     <body>
                       <p><big> The question is about to be modified is:%s </big></p>
                       <p><big> Please give the new question: </big></p>
                       <form action="/updateText" method="post">
                         <div><textarea name="newQuestion" rows="3" cols="60"></textarea></div>
                         <div><input type="submit" name="button" value="submit"></div>
                              <input type="hidden" name="title" value="%s" />
                              <input type="hidden" name="question" value="%s" />
                              <input type="hidden" name="account" value="%s" />
                      </form>
                    </body>
                 </html>""" %(question, title, question, account))
            if opSelected == "add an option":
                 print '%s'%title
            if opSelected == "edit options":
                self.response.out.write(""" <html><body>""")
                self.response.out.write(""" <form action="/editOption" method="post">""")
                curOption=""
                optionNum=0   
                options = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title =  :2 and question = :3",
                                   account, title, question
                                  )
                for option in options:
                         optionNum=optionNum+1
                         self.response.out.write("""<div>
                         <input type="radio" name = "option", value="%s"/>
                         <font size = 4>C%s. %s</font>
                         </div>"""%(option.option, optionNum, option.option))
                self.response.out.write(""" <input type="submit" name="button" value= "delete" />
                         <input type="submit" name="button" value= "edit" />
                         <input type="hidden" name="account" value= "%s" />
                         <input type="hidden" name="title" value= "%s" />
                         <input type="hidden" name="question" value= "%s" />"""%(account,title, question))    
                self.response.out.write(""" </form>""")
                self.response.out.write(""" </body></html>""")
class EditOption(webapp.RequestHandler):
     def post(self):
        account=self.request.get('account')
        opSelected=self.request.get('button')
        title=self.request.get('title')
        question = self.request.get('question')
        option = self.request.get('option')
        if option == "":
            options = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title = :2 and question = :3",
                                   account, title, question
                                  )
            self.response.out.write(""" <html><body>""")
            self.response.out.write(""" You have to select an option before selecting the operations.""")
            self.response.out.write(""" <form action="/editOption" method="post">""")
            optionNum=0             
            for option in options:
                         optionNum=optionNum+1
                         self.response.out.write("""<div>
                         <input type="radio" name = "option", value="%s"/>
                         <font size = 4>C%s. %s</font>
                         </div>"""%(option.option, optionNum, option.option))
            self.response.out.write(""" <input type="submit" name="button" value= "delete" />
                         <input type="submit" name="button" value= "edit" />
                         <input type="hidden" name="account" value= "%s" />
                         <input type="hidden" name="title" value= "%s" />
                         <input type="hidden" name="question" value= "%s" />"""%(account, title, question))
            self.response.out.write(""" </form>""")
            self.response.out.write(""" </body></html>""")
                             
        else:
            if opSelected == "delete":
                 options = db.GqlQuery("SELECT * "
                                   "FROM Survey "
                                   "WHERE account = :1 and title =:2 and question =:3 and option =:4",
                                          account,title, question, option
                                  )
                 db.delete(options)
                 self.response.out.write("""
                   <html>
                   <body>
                     <p><big> The option is deleted.</big></p>
                     <a href=\"/\">Back To Home Page</a>
                   </body>
                   </html>""" )
            if opSelected == "edit":
                  self.response.out.write("""
                  <html>
                     <body>
                       <p><big> The option is about to be modified is:%s </big></p>
                       <p><big> Please give the new option: </big></p>
                       <form action="/updateText" method="post">
                         <div><textarea name="newOption" rows="3" cols="60"></textarea></div>
                         <div><input type="submit" name="button" value="submit"></div>
                              <input type="hidden" name="title" value="%s" />
                              <input type="hidden" name="question" value="%s" />
                              <input type="hidden" name="option" value="%s" />
                              <input type="hidden" name="account" value="%s" />
                      </form>
                    </body>
                 </html>""" %(option, title, question, option, account))

def defsurvey_title(account,title,self):
    errorMsg=""
    if title != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2", account, title)
        if existSurvey.count() == 0:
            self.response.out.write("""
            <html><body>
            <p><big> Add a question for survey: "%s"</big></p>
            <form action="/newSurvey" method="post">
            <div><textarea name="question" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="add an option"></div>
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />
            </form></body></html>""" % (title,title,account))
        else:
            errorMsg="The title you input exists! Please give another one:"
    else:
        errorMsg="You have to give a title of the new survey:"
    if errorMsg != "":
        self.response.out.write("""
        <html><body>
        <p><big> %s</big></p> 
        <form action="/newSurvey" method="post">
        <div><textarea name="title" rows="3" cols="60"></textarea></div>
        <div><input type="submit" name="button" value="add a new question"></div>
        <input type="hidden" name="account" value="%s" />
        </form></body></html>""" % (errorMsg, account))
    return

def defquestion(account,title,question,self):
    errorMsg=""
    if question != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2 and question = :3", account, title, question)
        if existSurvey.count() == 0:
            self.response.out.write("""
            <html><body>
            <p><big> Add an option for question "%s--%s":</big></p> 
            <form action="/newSurvey" method="post">
            <div><textarea name="option" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
            <input type="submit" name="button" value="new survey complete"></div>
            <input type="hidden" name="question" value="%s" />
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />
            </form></body></html>""" % (title,question, question, title, account))
        else:
            errorMsg="The question you input exists! Please input another one:"
    else:
        errorMsg="You have to give the question first:"
    if errorMsg != "":
        self.response.out.write("""
        <html><body>
        <p><big> %s</big></p> 
        <form action="/newSurvey" method="post">
        <div><textarea name="question" rows="3" cols="60"></textarea></div>
        <div><input type="submit" name="button" value="add an option"></div>
        <input type="hidden" name="title" value="%s" />
        <input type="hidden" name="account" value="%s" />
        </form></body></html>""" % (errorMsg,title, account))
    return

def defoption_question(account,title,question,option,self):
    errorMsg=""
    if option != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2 and question = :3 and option = :4", account, title, question, option)
        if existSurvey.count() == 0:
            self.response.out.write("""
            <html><body>
            <p><big> Add a question for survey: "%s"</big></p> 
            <form action="/newSurvey" method="post">
            <div><textarea name="question" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="add an option"></div>
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />
            </form></body></html>""" %(title,title,account))
            s = Survey(account=account,
                        title=title,
                        question=question,
                        option=option,
                        count=0)
            db.put(s)
        else:
            errorMsg="The option you input exists! Please input another one:"
    else:
        errorMsg="You can not leave the option as blank. What's the option?"
    if errorMsg!="":
        self.response.out.write("""
        <html><body>
        <p><big> %s</big></p> 
        <form action="/newSurvey" method="post">
        <div><textarea name="option" rows="3" cols="60"></textarea></div>
        <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
        <input type="submit" name="button" value="new survey complete"></div>
        <input type="hidden" name="question" value="%s" />
        <input type="hidden" name="title" value="%s" />
        <input type="hidden" name="account" value="%s" />
        </form></body></html>""" % (errorMsg,question, title, account))
    return

def defoption_option(account,title,question,option,self):
    errorMsg=""
    if option != "":
        existSurvey = db.GqlQuery("SELECT * "
                                  "FROM Survey "
                                  "WHERE account = :1 and title = :2 and question = :3 and option = :4", account, title, question, option)
        if existSurvey.count() == 0:
            self.response.out.write("""
            <html><body>
            <p><big> Add a option for question "%s--%s":</big></p> 
            <form action="/newSurvey" method="post">
            <div><textarea name="option" rows="3" cols="60"></textarea></div>
            <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
            <input type="submit" name="button" value="new survey complete"></div>
            <input type="hidden" name="question" value="%s" />
            <input type="hidden" name="title" value="%s" />
            <input type="hidden" name="account" value="%s" />     
            </form></body></html>""" %(title, question, question, title, account))
            s = Survey(account=account,
                      title=title,
                      question=question,
                      option=option,
                      count=0)
            db.put(s)
        else:
            errorMsg="The option you input exists! Please input another one:"
    else:
        errorMsg="You can not leave the option as blank. What's the option?"
    if errorMsg!="":
        self.response.out.write("""
        <html><body>
        <p><big> %s</big></p> 
        <form action="/newSurvey" method="post">
        <div><textarea name="option" rows="3" cols="60"></textarea></div>
        <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
        <input type="submit" name="button" value="new survey complete"></div>
        <input type="hidden" name="question" value="%s" />
        <input type="hidden" name="title" value="%s" />
        <input type="hidden" name="account" value="%s" />
        </form></body></html>""" %(errorMsg,question, title, account))
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
            <p><big> A new survey is created</big></p>
            <a href=\"/\">Back To Home Page</a>
            </body></html>""" )

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
        <p><big> %s</big></p> 
        <form action="/newSurvey" method="post">
        <div><textarea name="option" rows="3" cols="60"></textarea></div>
        <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
        <input type="submit" name="button" value="new survey complete"></div>
        <input type="hidden" name="question" value="%s" />
        <input type="hidden" name="title" value="%s" />
        <input type="hidden" name="account" value="%s" />
        </form></body></html>""" %(errorMsg,question, title, account))
    return
                                
class CreateSurvey(webapp.RequestHandler):
    def post(self):
        account=self.request.get('account')
        queOrChoi=self.request.get('button')
        title=self.request.get('title')
        question=self.request.get('question')
        option=self.request.get('option')
        if queOrChoi == "add a new question":
            defsurvey_title(account,title,self)
        if queOrChoi == "add an option":
            defquestion(account,title,question,self)
        if queOrChoi == "next question":
            defoption_question(account,title,question,option,self)
        if queOrChoi == "next option":
            defoption_option(account,title,question,option,self)
        if queOrChoi == "new survey complete":
            defoption_complete(account,title,question,option,self)
                
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', TaskChoice),
                                       ('/newSurvey', CreateSurvey),
                                       ('/editTitle', EditTitle)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
