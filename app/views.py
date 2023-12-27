from django.shortcuts import render, redirect
from app.models import Case
from app.forms import BaseUserCreationForm

def index(request):
	return render(request, "index.html")

def report(request):
	"""Create a case"""
	if request.method == "POST":
		c = Case(id=Case.short_uuid())
		c.animal = request.POST.get("animal-type")
		c.add_log_entry(
			request.POST.get("reporter-name"),
			request.POST.get("reporter-phone-number"),
			request.POST.get("notes"),
			request.POST.get("coordinates"),
			"waiting"
		)
		c.save()
		print(f"New {c.animal} case saved")
		return redirect(index)
	return render(request, 'report.html')

def map(request):
	cases = Case.objects.all()
	return render(request, 'map.html', {"cases":cases})

def case(request,id):
	case = Case.objects.get(pk=id)
	return render(request, 'case.html', {"case":case})

def register(request):
	if request.method == "POST":
		form = BaseUserCreationForm(request.POST)
		if form.is_valid():
			user_save = form.save()
			return render(request, 'index.html')

	form = BaseUserCreationForm()

	return render(request, 'register.html', {'form':form})