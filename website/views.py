from django.shortcuts import redirect

def index_view(request):
    if not request.user.is_authenticated():
        return redirect('login')
    else:
        return redirect('maraudes:index')
