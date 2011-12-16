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
                 self.response.out.write(""" <form action="/editSurvey" method="post">""")
                 curTitle=""
                 curQuestion=""
                 titleNum=0             
                 for survey in surveys:
                     if curTitle!=survey.title:
                         curTitle=survey.title
                         titleNum=titleNum+1
                         questionNum=0
                         self.response.out.write("""<div>
                         <input type="radio" name = "title", value=%s/>
                         <font size = 6>%s. %s</font>
                         </div>"""%(curTitle, titleNum, curTitle))
                     if curQuestion!=survey.question:
                         curQuestion=survey.question
                         questionNum=questionNum+1
                         optionNum=0
                         tq= [str(curTitle), str(curQuestion)] 
                         self.response.out.write("""<div>                          
                          &nbsp &nbsp <font size = 5><input type="radio" name = "question", value=%s/>Q%s. %s</font>
                          </div>"""%(tq, questionNum, curQuestion))
                     optionNum=optionNum+1
                     tqc= [str(curTitle), str(curQuestion), str(survey.option)]
                     self.response.out.write("""<div>&nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp <input type="radio" name = "question", value=%s/> C%s. %s
                     </div>"""%(tqc, optionNum, survey.option)) 
                 self.response.out.write(""" <input type="submit" name="button" value= "delete" />
                         <input type="submit" name="button" value= "edit" />
                         <input type="submit" name="button" value= "add a new question" />
                         <input type="submit" name="button" value= "add an option" />""")    
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
    
class CreateSurvey(webapp.RequestHandler):
    def post(self):
        account=self.request.get('account')
        queOrChoi=self.request.get('button')
        title=self.request.get('title')
        question=self.request.get('question')
        option=self.request.get('option')
        if queOrChoi == "add a new question":
            if title == "":
                self.response.out.write("""
                  <html>
                     <body>
                       <p><big> You have to give a title of the new survey:</big></p> 
                       <form action="/newSurvey" method="post">
                         <div><textarea name="title" rows="3" cols="60"></textarea></div>
                         <div><input type="submit" name="button" value="add a new question"></div>
                         <input type="hidden" name="account" value="%s" />
                      </form>
                    </body>
                 </html>""" % account)
            else:
                self.response.out.write("""
                <html>
                  <body>
                     <p><big> Add a question for survey: "%s"</big></p>
                     <form action="/newSurvey" method="post">
                       <div><textarea name="question" rows="3" cols="60"></textarea></div>
                       <div><input type="submit" name="button" value="add an option"></div>
                        <input type="hidden" name="title" value="%s" />
                       <input type="hidden" name="account" value="%s" />
                     </form>
                 </body>
               </html>""" % (title,title,account))
          
        if queOrChoi == "add an option":
            if question =="":
                self.response.out.write("""
                  <html>
                     <body>
                       <p><big> You have to give the question first:</big></p> 
                       <form action="/newSurvey" method="post">
                         <div><textarea name="question" rows="3" cols="60"></textarea></div>
                         <div><input type="submit" name="button" value="add an option"></div>
                         <input type="hidden" name="title" value="%s" />
                         <input type="hidden" name="account" value="%s" />
                      </form>
                    </body>
                 </html>""" %(title, account))
            else:
                self.response.out.write("""
                 <html>
                  <body>
                   <p><big> Add an option for question "%s--%s":</big></p> 
                   <form action="/newSurvey" method="post">
                     <div><textarea name="option" rows="3" cols="60"></textarea></div>
                     <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
                          <input type="submit" name="button" value="new survey complete"></div>
                      <input type="hidden" name="question" value="%s" />
                      <input type="hidden" name="title" value="%s" />
                      <input type="hidden" name="account" value="%s" />
                   </form>
                  </body>
                 </html>""" %(title,question, question, title, account))

        if queOrChoi == "next question":
            if option =="":
                self.response.out.write("""
                  <html>
                     <body>
                       <p><big> You can not leave the option as blank. What's the option?</big></p> 
                       <form action="/newSurvey" method="post">
                         <div><textarea name="option" rows="3" cols="60"></textarea></div>
                         <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
                              <input type="submit" name="button" value="new survey complete"></div>
                              <input type="hidden" name="question" value="%s" />
                              <input type="hidden" name="title" value="%s" />
                              <input type="hidden" name="account" value="%s" />
                      </form>
                    </body>
                 </html>""" % (question, title, account))
            else:
                self.response.out.write("""
                 <html>
                  <body>
                   <p><big> Add a question for survey: "%s"</big></p> 
                   <form action="/newSurvey" method="post">
                     <div><textarea name="question" rows="3" cols="60"></textarea></div>
                     <div><input type="submit" name="button" value="add an option"></div>
                      <input type="hidden" name="title" value="%s" />
                      <input type="hidden" name="account" value="%s" />
                   </form>
                  </body>
                 </html>""" %(title,title,account))
                s = Survey(account=account,
                            title=title,
                            question=question,
                            option=option,
                            count=0)
                db.put(s)
                
        if queOrChoi == "next option":
            if option =="":
                self.response.out.write("""
                  <html>
                     <body>
                       <p><big> You can not leave the option as blank. What's the option?</big></p> 
                       <form action="/newSurvey" method="post">
                         <div><textarea name="option" rows="3" cols="60"></textarea></div>
                         <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
                              <input type="submit" name="button" value="new survey complete"></div>
                              <input type="hidden" name="question" value="%s" />
                              <input type="hidden" name="title" value="%s" />
                              <input type="hidden" name="account" value="%s" />
                      </form>
                    </body>
                 </html>""" %(question, title, account))
            else:
                self.response.out.write("""
                 <html>
                  <body>
                   <p><big> Add a option for question "%s--%s":</big></p> 
                   <form action="/newSurvey" method="post">
                     <div><textarea name="option" rows="3" cols="60"></textarea></div>
                     <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
                          <input type="submit" name="button" value="new survey complete"></div>
                     <input type="hidden" name="question" value="%s" />
                     <input type="hidden" name="title" value="%s" />
                     <input type="hidden" name="account" value="%s" />     
                   </form>
                  </body>
                 </html>""" %(title, question, question, title, account))
                
                s = Survey(account=account,
                            title=title,
                            question=question,
                            option=option,
                            count=0)
                db.put(s)
                                            
                
        if queOrChoi == "new survey complete":
             if option =="":
                self.response.out.write("""
                  <html>
                     <body>
                       <p><big> You can not leave the option as blank. What's the option?</big></p> 
                       <form action="/newSurvey" method="post">
                         <div><textarea name="option" rows="3" cols="60"></textarea></div>
                         <div><input type="submit" name="button" value="next question"><input type="submit" name="button" value="next option">
                              <input type="submit" name="button" value="new survey complete"></div>
                               <input type="hidden" name="question" value="%s" />
                               <input type="hidden" name="title" value="%s" />
                               <input type="hidden" name="account" value="%s" />
                      </form>
                    </body>
                 </html>""" %(question, title, account))
             else:
                 self.response.out.write("""
                 <html>
                   <body>
                     <p><big> A new survey is created</big></p>
                     <a href=\"/\">Back To Home Page</a>
                   </body>
                 </html>""" )
                 
                 s = Survey(account=account,
                            title=title,
                            question=question,
                            option=option,
                            count=0)
                 db.put(s)
                 
#class EditSurvey(webapp.RequestHandler):
        
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/sign', TaskChoice),
                                       ('/newSurvey', CreateSurvey)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
