import random
from django import forms
from django.contrib import messages
from django.shortcuts import render
from markdown2 import Markdown

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Title", "class": "form-control col-sm-2"}))
    content = forms.CharField(widget=forms.Textarea(attrs={"placeholder": "Markdown content", "class": "form-control col-sm-8"}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def md_to_html(title):
    entry = util.get_entry(title)
    markdowner = Markdown()
    if entry == None:
        return None
    else:
        return markdowner.convert(entry)
    
def entry(request, title):
    entry_content = md_to_html(title)
    if entry_content == None:
        return render(request, "encyclopedia/error.html", {
            "apology": "Page was not found"
        })
    else:
        return render(request, "encyclopedia/wiki.html", {
            "entry": entry_content,
            "title": title
        })
    
def search(request):
    if request.method == "POST":
        search_title = request.POST["q"]
        entry_content = md_to_html(search_title)
        if entry_content != None:
            return render(request, "encyclopedia/wiki.html", {
                "entry": entry_content,
                "title": search_title
            })
        else:
            search = []
            for entry in util.list_entries():
                if search_title.lower() in entry.lower():
                    search.append(entry)
            return render(request, "encyclopedia/search.html", {
                "search": search
            })
        
def create(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            newEntry = util.get_entry(title)
            if newEntry != None:
                messages.error(request, "Page already exists")
                return render(request, "encyclopedia/create.html", {
                    "form": form,
                })
            else:
                util.save_entry(title, content)
                entry_content = md_to_html(title)
                return render(request, "encyclopedia/wiki.html", {
                    "entry": entry_content,
                    "title": title
                })
    else:
        return render(request, "encyclopedia/create.html", {
            "form": NewEntryForm()
        })
    
def edit(request):
    if request.method == "POST":
        title = request.POST["title"]
        edit_content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "entry": edit_content,
            "title": title
        })
    
def update(request):
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["entry"]
        util.save_entry(title, content)
        entry_content = md_to_html(title)
        return render(request, "encyclopedia/wiki.html", {
            "entry": entry_content,
            "title": title
        })
    
def random_page(request):
    entries = util.list_entries()
    random_page = random.choice(entries)
    entry_content = md_to_html(random_page)
    return render(request, "encyclopedia/wiki.html", {
        "entry": entry_content,
        "title": random_page
    })