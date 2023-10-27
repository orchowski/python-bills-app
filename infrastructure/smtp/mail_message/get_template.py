from jinja2 import Environment, PackageLoader, select_autoescape

from infrastructure.smtp.mail_message.mail_message import MailTemplate

env = Environment(
    loader=PackageLoader('templates', 'mail_templates'),
    autoescape=select_autoescape(['html', 'xml']))

def render_template(mail_template: MailTemplate):
    template = env.get_template(f"{mail_template.template_name}_{mail_template.language.value}.html")
    return template.render(**mail_template.content)
