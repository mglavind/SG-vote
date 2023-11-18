from django.contrib import admin
from django import forms
from .models import Choice, Question, Member
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls.resolvers import URLPattern
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import admin, messages
from typing import List
from datetime import datetime
from django.shortcuts import render
from django.utils.html import strip_tags
import random
import csv

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text',
                                         'is_published',
                                         'pub_date',
                                         'closing_date_time',
                                         ],}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'is_published', 'closing_date_time', )
    list_filter = ['pub_date']
    search_fields = ['question_text']


class MemberAdminForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = "__all__"

class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()




class MemberAdmin(admin.ModelAdmin):
    form = MemberAdminForm
    list_display = [
        "username",
        "first_name",
        "last_name",
        "gang",
        "room_number",
        "email",
    ]
    readonly_fields = [
        "created",
        "last_updated",
    ]
    actions = ["export_to_csv", "send_email_action"]

    def export_to_csv(modeladmin, request, queryset):
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="members.csv"'
            response.write(u'\ufeff'.encode('utf8'))

            writer = csv.writer(response)
            writer.writerow(['First Name', 'Last Name', 'Username', 'Email'])

            for member in queryset:
                writer.writerow([member.first_name, member.last_name, member.username, member.email])
            return response
    export_to_csv.short_description = "Export selected members to CSV"
    
    def get_urls(self) -> List[URLPattern]:
        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]
        return new_urls + urls
    
    def upload_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]

            if not csv_file.name.endswith(".csv"):
                messages.warning(request, "Wrong file type was uploaded. Please upload a CSV file.")
                return HttpResponseRedirect(request.path_info)

            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")

            for line in csv_data:
                fields = line.split(",")
                form_data = {
                    "first_name": fields[0],
                    "last_name": fields[1],
                    "username": fields[2],
                    "email": fields[3],
                }
                
                # Generate a random password (you can customize the length and characters)
                random_password = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=12))
                form_data["password"] = random_password
                
                # Set date_joined to the current date and time
                form_data["date_joined"] = datetime.now()

                # Create a MemberAdminForm instance with the modified form_data
                form = MemberAdminForm(form_data)

                if form.is_valid():
                     # Save the member instance
                    member = form.save()

                     # Activate the user
                    User = get_user_model()  # Get the custom user model
                    user = User.objects.get(username=member.username)
                    user.is_active = True
                    user.save()
                else:
                    error_messages = []
                    for field, errors in form.errors.items():
                        error_messages.append(f"Field '{field}': {'; '.join(map(str, errors))}")
                    error_message = "; ".join(error_messages)
                    messages.warning(request, f"Invalid data in CSV: {error_message}")

        form = CsvImportForm()
        data = {"form": form}
        return render(request, "admin/csv_upload.html", data)
    
    
    def send_email_action(self, request, queryset):
        email_template = "Mpollsember/reset_password_guide_email.html"

        for member in queryset:
            subject = "Velkommen til Seniorkursus Slettens booking system"
            context = {'member': member}
            message = render_to_string(email_template, context)
            plain_message = strip_tags(message)

            send_mail(subject, plain_message, 'seniorkursussletten@gmail.com', [member.email], html_message=message)
        
        self.message_user(request, f"Emails sent to {queryset.count()} members.")
    send_email_action.short_description = "Send hjælp til at komme igang email til members"    

admin.site.register(Question, QuestionAdmin)
admin.site.register(Member, MemberAdmin)
