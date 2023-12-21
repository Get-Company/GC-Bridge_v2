from flask_wtf import FlaskForm
from wtforms import validators
from wtforms.fields.numeric import FloatField
from wtforms.fields.simple import StringField, TextAreaField
from wtforms_alchemy import ModelForm

from .BridgeMarketplaceEntity import BridgeMarketplaceEntity


class BridgeMarketplaceForm(ModelForm, FlaskForm):

    # Beispiel: Überschreiben des 'name'-Feldes mit benutzerdefiniertem Label und Validatoren
    name = StringField('Marktplatzname', [
        validators.Length(min=4, message='Der Name muss mindestens 4 Zeichen lang sein.'),
        validators.DataRequired(message='Dieses Feld ist erforderlich.')
    ])
    description = TextAreaField('Beschreibung', [
        validators.Optional(),
        validators.Length(max=500, message='Die Beschreibung darf maximal 500 Zeichen lang sein.')
    ])

    url = StringField('URL', [
        validators.Optional(),
        validators.Length(max=255, message='Die URL darf maximal 255 Zeichen lang sein.'),
        validators.URL(message='Bitte geben Sie eine gültige URL ein.')
    ])

    api_key = StringField('API-Schlüssel', [
        validators.Optional(),
        validators.Length(max=255, message='Der API-Schlüssel darf maximal 255 Zeichen lang sein.')
    ])

    # Da das JSON-Feld sehr spezifisch ist, hängt die Validierung von Ihren Anforderungen ab.
    # Hier ist ein einfaches Beispiel ohne spezielle Validierung.
    config = TextAreaField('Konfiguration', validators=[validators.Optional()])

    factor = FloatField('Faktor', validators=[
        validators.Optional(),
        validators.NumberRange(min=0, message='Der Faktor muss eine positive Zahl sein.')
    ])