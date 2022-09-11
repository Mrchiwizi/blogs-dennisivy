from django.forms import ModelForm, Textarea
from . models import Message, Room


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'




class MessageUpdateForm(ModelForm):
    class Meta:
        model = Message
        fields = ['body']

        # widgets = {
        #     'name': Textarea(
        #         attrs= {
        #             'cols': 5, 'rows': 2
        #         }
        #     ),
        # }