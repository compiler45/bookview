from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField, StringField, RadioField
from wtforms.validators import DataRequired, Optional

from .fields import MultiCheckboxField
from ..models import Tag


class WriteArticleForm(FlaskForm):
    title = StringField('Book Title', validators=[DataRequired()])
    author = StringField('Author', validators=[DataRequired()])
    year_published = StringField('Year Published (optional)',
                                 validators=[Optional()])
    book_image = FileField('Upload an image of the book (optional)',
                           validators=[Optional(), FileAllowed(['jpg', 'png'],
                                                                'Images only!')])
    tags = MultiCheckboxField('Tags for this book',
                              validators=[DataRequired()])
    markdown_field = PageDownField('Enter your article text',
                                   validators=[DataRequired()])
    save = SubmitField('Save Article')
    publish = SubmitField('Publish Article')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tags.choices = [(t.name, t.name) for t in Tag.query.all()]
