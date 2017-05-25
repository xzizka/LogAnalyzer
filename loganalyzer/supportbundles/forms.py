from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms.fields import IntegerField, TextAreaField, FileField, StringField
from wtforms.validators import DataRequired, Optional, NumberRange, Regexp

class SBForm_base(FlaskForm):
    service_request=IntegerField('Service Request number', validators=[DataRequired(message='You must input a valid number'),NumberRange(min=0,message='Input is not a valid number.')])
    comment=TextAreaField('Add comments',validators=[Optional()])
    tags = StringField('Tags', validators=[Regexp(r'^[a-z,A-Z0-9, ]*$', message='Tags can only contains letters and numbers')])

    def validate(self):

        #if not self.input_file and request.endpoint == "edit":
        #    self.input_file.data = FileField()

        if not FlaskForm.validate(self):
            return False

        stripped = [t.strip() for t in self.tags.data.split(',')]
        not_empty = [tag for tag in stripped if tag]
        tagset = set(not_empty)
        self.tags.data = ",".join(tagset)

        return True


class SBForm_upload(SBForm_base):
    input_file=FileField('Select Support Bundle',validators=[FileRequired(message='The Support Bundle is mandatory')])

