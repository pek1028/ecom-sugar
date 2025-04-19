from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Customer
from datetime import date

class CustomerRegistrationForm(UserCreationForm):
    name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': '請輸入姓名。',
        },
        widget=forms.TextInput(attrs={'placeholder': '輸入姓名'})
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        error_messages={
            'required': '請輸入電話號碼。',
        },
        widget=forms.TextInput(attrs={'placeholder': '輸入電話號碼'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': '輸入電子郵件'}),
        error_messages={
            'required': '請輸入電子郵件。',
        }
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': '輸入地址'}),
        required=True,
        error_messages={
            'required': '請輸入地址。',
        }
    )
    line_id = forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': '請輸入Line ID。',
        },
        widget=forms.TextInput(attrs={'placeholder': '輸入Line ID'})
    )
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': '選擇出生日期'}),
        required=True,
        error_messages={
            'required': '請選擇出生日期。',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'name', 'phone', 'email', 'address', 'line_id', 'birthdate')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('此用戶名已被使用，請選擇其他用戶名。')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('此電子郵件已被註冊，請使用其他電子郵件。')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                phone=self.cleaned_data['phone'],
                email=self.cleaned_data['email'],
                address=self.cleaned_data['address'],
                line_id=self.cleaned_data['line_id'],
                birthdate=self.cleaned_data['birthdate']
            )
        return user

class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '輸入用戶名'}),
        error_messages={
            'required': '請輸入用戶名。',
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '輸入密碼'}),
        error_messages={
            'required': '請輸入密碼。',
        }
    )

class ShippingForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        error_messages={
            'required': '請輸入姓名。',
        },
        widget=forms.TextInput(attrs={'placeholder': '輸入姓名'})
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        error_messages={
            'required': '請輸入電話號碼。',
        },
        widget=forms.TextInput(attrs={'placeholder': '輸入電話號碼'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': '輸入地址'}),
        required=True,
        error_messages={
            'required': '請輸入地址。',
        }
    )
    delivery_method = forms.ChoiceField(
        choices=[
            ('family_mart', '全家'),
            ('seven_eleven', '7-11'),
            ('self_collect', '宅配')
        ],
        required=True,
        error_messages={
            'required': '請選擇送貨方式。',
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('line_pay', 'Line Pay'),
            ('bank', '銀行轉帳')
        ],
        required=True,
        error_messages={
            'required': '請選擇付款方式。',
        },
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('name', 'phone', 'email', 'address', 'line_id', 'birthdate')
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': '輸入姓名'}),
            'phone': forms.TextInput(attrs={'placeholder': '輸入電話號碼'}),
            'email': forms.EmailInput(attrs={'placeholder': '輸入電子郵件'}),
            'address': forms.Textarea(attrs={'placeholder': '輸入地址'}),
            'line_id': forms.TextInput(attrs={'placeholder': '輸入Line ID'}),
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
        }
        error_messages = {
            'name': {'required': '請輸入姓名。'},
            'phone': {'required': '請輸入電話號碼。'},
            'address': {'required': '請輸入地址。'},
            'line_id': {'required': '請輸入Line ID。'},
            'birthdate': {'required': '請選擇出生日期。'},
        }

class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': '輸入電子郵件'}),
        error_messages={
            'required': '請輸入電子郵件。',
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('此用戶名已被使用，請選擇其他用戶名。')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('此電子郵件已被註冊，請使用其他電子郵件。')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                name=user.username,  # Use username as default name
                phone='0000000000',  # Default phone number
                email=user.email
            )
        return user