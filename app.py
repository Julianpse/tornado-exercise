import tornado.ioloop
import tornado.web
import tornado.log

import os
import boto3

client = boto3.client(
  'ses',
  region_name = 'us-east-1',
  aws_access_key_id = 'AKIAIVDPAKCKT3CTLUSQ',
  aws_secret_access_key='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'
)

from jinja2 import \
Environment, PackageLoader, select_autoescape

ENV = Environment(
  loader=PackageLoader('myapp', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    context['page'] = self.request.path
    self.write(template.render(**context))

class MainHandler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("home.html", {})

class Page2Handler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("products.html", {})

def send_email(email,first_name,last_name,message):
  response = client.send_email(
      Destination={
        'ToAddresses': ['julianpse@gmail.com'],
      },
      Message={
      'Body': {
        'Text': {
          'Charset': 'UTF-8',
          'Data': '{} {}wants to talk to you\n\n{} {}'.format(first_name,last_name,email,message),
        },
      },
      'Subject': {'Charset': 'UTF-8', 'Data': 'Test email'},
    },
      Source='julianpse@gmail.com',
    )
    
class ContactHandler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age=0')
    self.render_template("contact.html", {})
    
  def post(self):
    email = self.get_body_argument('email')
    first_name = self.get_body_argument('first_name')
    last_name = self.get_body_argument('last_name')
    message = self.get_body_argument('message')
    
    if email:
      print("IT WORKED")
      send_email(email,first_name,last_name,message)
      self.redirect("/success")
      
    else:
      error = "PUT YOUR EMAIL IN"
      
class SuccessHandler(TemplateHandler):
  def get(self):
    self.set_header(
      'Cache-Control',
      'no-store, no-cache, must-revalidate, max-age =0')
    self.render_template("success.html", {})
    
   
def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/page2", Page2Handler),
    (r"/contact", ContactHandler),
    (r"/success", SuccessHandler),
    (
      r"/static/(.*)",
      tornado.web.StaticFileHandler,
      {'path': 'static'}
    ),
  ], autoreload=True)
  
if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  
  app = make_app()
  PORT = int(os.environ.get('PORT', '8888'))
  app.listen(PORT)
  tornado.ioloop.IOLoop.current().start()
    