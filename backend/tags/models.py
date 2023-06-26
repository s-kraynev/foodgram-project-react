from django.core.exceptions import ValidationError
from django.db import models
from django_extensions.validators import HexValidator


# NOTE: it could be moved to separte file, but for clear review define it here
class AsciiHexValidator(HexValidator):
    def __call__(self, value):
        # remove hash before validation
        if not value.startswith('#'):
            raise ValidationError(
                'Описание цвета должно начинаться с символа "#"'
            )
        value = value[1:]
        try:
            # HexValidator use binascii.unhexlify method, which does not
            # support non ascii symbols. So now it tries to convert data
            # to expected format
            value.encode('ascii')
        except UnicodeError:
            raise ValidationError('Поддерживаются только ASCII символы')
        try:
            super(AsciiHexValidator, self).__call__(value)
        except ValidationError:
            raise ValidationError('Некорректное значение цвета')


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(
        'Краткое название',
        max_length=200,
        unique=True,
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        validators=[AsciiHexValidator()],
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Бархатные Тяги'

    def __str__(self):
        return self.name
