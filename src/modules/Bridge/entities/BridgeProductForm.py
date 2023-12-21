from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class BridgeProductForm(FlaskForm):
    # Felder für BridgeProductEntity
    erp_nr = StringField(
        'ERP Nummer',
        validators=[
            DataRequired(message='Die ERP-Nummer ist erforderlich.'),
            Length(max=255, message='Die ERP-Nummer darf maximal 255 Zeichen lang sein.')
        ]
    )

    stock = IntegerField(
        'Lagerbestand',
        validators=[
            DataRequired(message='Der Lagerbestand ist erforderlich.'),
            NumberRange(min=0, message='Der Lagerbestand darf nicht negativ sein.')
        ]
    )

    storage_location = StringField(
        'Lagerort',
        validators=[Length(max=255, message='Der Lagerort darf maximal 255 Zeichen lang sein.')]
    )

    unit = StringField(
        'Einheit',
        validators=[Length(max=255, message='Die Einheit darf maximal 255 Zeichen lang sein.')]
    )

    min_purchase = IntegerField(
        'Mindestkaufmenge',
        validators=[NumberRange(min=0, message='Die Mindestkaufmenge darf nicht negativ sein.')]
    )

    purchase_unit = IntegerField(
        'Kaufeinheit',
        validators=[NumberRange(min=0, message='Die Kaufeinheit darf nicht negativ sein.')]
    )

    shipping_cost_per_bundle = FloatField(
        'Versandkosten pro Bündel',
        validators=[NumberRange(min=0, message='Die Versandkosten pro Bündel dürfen nicht negativ sein.')]
    )

    shipping_bundle_size = IntegerField(
        'Bündelgröße für Versand',
        validators=[NumberRange(min=0, message='Die Bündelgröße für Versand darf nicht negativ sein.')]
    )

    active = BooleanField('Aktiv')



