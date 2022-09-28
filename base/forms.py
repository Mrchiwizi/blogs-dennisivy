from django.forms import ModelForm, Textarea
from . models import Message, Room, User
from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User



class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']




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


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'bio']