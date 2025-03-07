from django.shortcuts import render
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_not_required, login_required
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model

from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic.edit import FormView
from django.shortcuts import resolve_url
from Simulator.core import settings

from django.http import HttpResponseRedirect, QueryDict

from django.contrib.auth.forms import (
    AuthenticationForm
)


class RedirectURLMixin:
    next_page = None
    redirect_field_name = REDIRECT_FIELD_NAME
    success_url_allowed_hosts = set



#VERY IMPORTANT allows for user to not have to be logged in to see the login page!
@method_decorator(login_not_required, name = "dispatch")
class LoginView(RedirectURLMixin, FormView):
    #form view handles forms while Redirect class handles redirects to other pages
    # Handles form class, can customize with authentication form

    form_class = AuthenticationForm
    authentication_form = None

    # gives template name
    # base set to not redirect user to main page, no additiona context data to page

    template_name = "registration/login.html"  

    # allows auth users to still access the login page
    redirect_authenticated_user = False
    extra_content = None

    # base decorators, making sure sensitive data is not cached
    # POST pass is never shown in error mess
    # csrf protection from forgery attacks

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache())
    @method_decorator(csrf_protect())


    # dispatch method checks for user already auth, if so redirects to home

    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            redirect_to = self.get_success_url()

            if redirect_to == self.request.path:
                # check for correct redirect
                raise ValueError(
                    "Redirect for auth user shown. Check LOGIN_REDIRECT does not point elsewhere"

                )
            
            return HttpResponseRedirect(redirect_to)
        # handles request logic, calls to loginview to handle POST,GET and differentiate
        return super().dispatch(request, *args, **kwargs)
    
    # determines default url to redirect to
    
    def get_default_redirect_url(self):
        #IF next page set, sends to next url
        if self.next_page:
            return resolve_url(self.next_page)
        else:
            return resolve_url(settings.LOGIN_REDIRECT_URL) #add ater to settings
    
    #returns the form to authenticate, defaults if auth form is not provided to form class
    def get_form_class(self):
        return self.authentication_form or self.form_class
    
    # preps kwards to pass to the FORMS, adds the REQUEST obj to the kwargs as django req
    def get_form_kwargs(self):
        kwargs = super().get_form_wargs()
        kwargs["request"] = self.request
        return kwargs
    
    # handles log after form is VALIDATED
    def form_valid(self, form):
        # LOGS IN user session then redirects to the url after
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())
    

    # adds to CONTEXT data for rendering in template 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)


        current_site = get_current_site(self.request)


        # updates to next redirect page 
        # holds info about CURRENT page

        context.update(
            {
                self.redirect_field_name: self.get_redirect_url(),
                "site": current_site,
                "site_name": current_site.name,
                **(self.extra_context or {})

            }
        )
        return context
    
    #LOGIN VIEW RECAP
    # dispatch redirects auth users to another page when they are auth
    # form valid actually logs in user when successful data passed
    # context data ensures correct rendering of auth page
    # method decs ensure that data is not shared 

        






# Create your views here.
