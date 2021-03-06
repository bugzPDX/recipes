from datetime import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from recipes.models import Category, Recipe, UserProfile, Ingredient
from recipes.forms import CategoryForm, RecipeForm, UserForm, UserProfileForm, IngredientForm, RecipeIngredientForm
from recipes.bing_search import run_query


# I definitely want the ability to log in and out so this should stay
# Use the login_required() decorator to ensure only those logged in can access the view
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out
    logout(request)

    #Take the user back to the homepage
    return HttpResponseRedirect(reverse('index'))


# I don't think I need a restricted page for anything
@login_required
def restricted(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}

    return render_to_response('recipes/restricted.html', context_dict, context)

# I don't think I need a profile page 
@login_required
def profile(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}
    u = User.objects.get(username=request.user)

    try:
        up = UserProfile.objects.get(user=u)
    except:
        up = None

    context_dict['user'] = u
    context_dict['userprofile'] = up
    return render_to_response('recipes/profile.html', context_dict, context)

# I was thinking this would be a good place for recipe ratings instead of likes
@login_required
def like_category(request):
    # context = RequestContext(request)
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']

    likes = 0
    if cat_id:
        category = Category.objects.get(id=int(cat_id))
        if category:
            likes = category.likes + 1
            category.likes = likes
            category.save()

    return HttpResponse(likes)

# I definitely want to be able to add recipes with title, ingredients,
# directions, source, notes and possibly other stuff.
@login_required
def auto_add_recipe(request):
    context = RequestContext(request)
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            Recipe.objects.get_or_create(category=category, title=title, url=url)

            recipes = Recipe.objects.filter(category=category).order_by('-views')

            # Adds our results list to the template context under name pages.
            context_dict['recipes_list'] = recipes

    return render_to_response('recipes/recipe_list.html', context_dict, context)

# I want to be able to search the recipes and have web results returned
# in addition to local recipes.
def search(request):
    context = RequestContext(request)
    cat_list = get_category_list()
    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            # Run our Bing function to get the results list
            result_list = run_query(query)

    context_dict = {'cat_list': cat_list, 'result_list': result_list}

    return render_to_response('recipes/search.html', context_dict, context)

# I don't really remember what this was for
def track_url(request):
    # context = RequestContext(request)
    recipe_id = None
    url = reverse('index')
    if request.method == 'GET':
        if 'recipe_id' in request.GET:
            recipe_id = request.GET['recipe_id']
            try:
                recipe = Recipe.objects.get(id=recipe_id)
                recipe.views = recipe.views + 1
                recipe.save()
                url = recipe.url
            except:
                pass

    return redirect(url)


# I don't really need to list categories by most popular but I guess it wouldn't hurt
def get_category_list(max_results=0, starts_with=''):
        cat_list = []
        if starts_with:
                cat_list = Category.objects.filter(name__istartswith=starts_with)
        else:
                cat_list = Category.objects.all()

        if max_results > 0:
                if len(cat_list) > max_results:
                        cat_list = cat_list[:max_results]

        for cat in cat_list:
                cat.url = encode_url(cat.name)

        return cat_list

# I don't think I need this unless it matters for adding categories
def suggest_category(request):
        context = RequestContext(request)
        cat_list = []
        starts_with = ''
        if request.method == 'GET':
                starts_with = request.GET['suggestion']

        cat_list = get_category_list(8, starts_with)

        return render_to_response('recipes/category_list.html', {'cat_list': cat_list }, context)

def get_recipe_list(max_results=0, is_in='', category_id=None):
        recipe_list = []

        if category_id:
            recipe_list = Recipe.objects.filter(category=category_id)
        else:
            recipe_list = Recipe.objects.all()

        if is_in:
            recipe_list = recipe_list.filter(title__icontains=is_in)

        if max_results > 0:
                if len(recipe_list) > max_results:
                        recipe_list = recipe_list[:max_results]

        return recipe_list

  # I don't think I need this unless it matters for adding categories
def suggest_recipe(request):
        context = RequestContext(request)
        recipe_list = []
        is_in = ''
        category_id = None 
        if request.method == 'GET':
                is_in = request.GET['recipe_suggest']
                try:
                    category_id = request.GET['category_id']
                except:
                    pass

        recipe_list = get_recipe_list(8, is_in, category_id)

        return render_to_response('recipes/recipe_list.html', {'recipe_list': recipe_list }, context)


# Definitely want log in access for add, modify, delete rights
def user_login(request):
    # Like before, obtain the context for the user's request
    context = RequestContext(request)
    cat_list = get_category_list()
    context_dict = {'cat_list': cat_list}

    # If the request is a HTTP POST, try to pull out the relevant info
    if request.method == 'POST':
        # Gather the username and password provided by the user
        # This information is obtained from the login form
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the usernam/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found
        if user is not None:
            # Is the account active? It could have been disabled
            if user.is_active:
                # If the account is valid and active, we can log the user in
                # We'll send the user back to the homepage
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Recipes account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in
            print "Invalid login details: {0}, {1}".format(username, password)
            return HttpResponseRedirect(reverse('login'))

    # The request is not a HTTP POST, so display the login form
    # This scenario would most likely be a HTTP GET
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return render_to_response('recipes/login.html', context_dict, context)

# I don't want/need people to be able to register
def register(request):
    #Like before, get the request's context
    context = RequestContext(request)
    cat_list = get_category_list()

    # A boolean value for telling the template whether the registration was successful
    # Set to False initiall. Code changes value to True when registration succeeds
    registered = False

    # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information
        # Note that we make use of both UserForm and UserProfileForm
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid...
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Now sort out the UserProfile instance
            # Since we need to set the user attribute ourselves, we set commit=False
            # This delays saving the model until we're ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user

            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model
            if 'picture' in request.FILES:
                profile.picture - request.FILES['picture']

            # Now we save the UserProfile model instance
            profile.save()

            # Update our variable to tell the template registration was successful
            registered = True

        # Invalid form or forms - mistakes or somethign else?
        # Print problems to the terminal
        # They'll also be shown to the user
        else:
            print user_form.errors, profile_form.errors

    # Not a HTTP POST, so we render our form using to ModelForm instances
    # These forms will be blank, ready for user input
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict = {'user_form': user_form, 'profile_form': profile_form,
                    'registered': registered, 'cat_list': cat_list}

    # Render the template depending on the context
    return render_to_response('recipes/register.html', context_dict, context)

def add_recipe_ingredient(request, recipe_id):
    context = RequestContext(request)

    recipe = Recipe.objects.get(pk=recipe_id)
    context_dict = {'recipe': recipe}

    if request.method == 'POST':
        form = RecipeIngredientForm(request.POST)

        if form.is_valid():
            recipe_ingredients = form.save(commit=False)
            recipe_ingredients.recipe = recipe
            recipe_ingredients.save()
            form = RecipeIngredientForm()
        else:
            print form.errors
    else:
        form = RecipeIngredientForm()

    context_dict['form'] = form

    return render_to_response('recipes/add_recipe_ingredient.html', context_dict, context)


def add_ingredient(request):
    context = RequestContext(request)
  #  ing_list = get_category_list()

      # A HTTP POST?
    if request.method == 'POST':
        form = IngredientForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage
            form = IngredientForm()
        else:
    # The supplied form contained errors - just print them to the termina  l
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details
        form = IngredientForm()
    context_dict = {'form': form}

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('recipes/add_ingredient.html', context_dict, context)


# I will want to add recipe pages
def add_recipe(request, recipe_id=None):
    context = RequestContext(request)
    cat_list = get_category_list()
    recipe = None
    editing = False
    my_title = "Add a Recipe"

    if recipe_id:
        try:
            recipe = Recipe.objects.get(pk=recipe_id)
            editing = True
            my_title = "Edit a recipe"
        except Recipe.DoesNotExist:
            pass

    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)

        if form.is_valid():
            # This time we cannot commit straight away
            # Not all fields are automatically populated!
            recipe = form.save(commit=False)

            # Also, create a default value for the number of views
            recipe.views = 0

            # With this, we can then save our new model instance.
            recipe.save()

            # Now that the recipe is saved, display the category instead.
            return show_recipe(request, recipe.id)
        else:
            print form.errors
    else:
        form = RecipeForm(instance=recipe)
        context_dict = {'editing': editing, 'form': form,
                        'cat_list': cat_list, 'my_title': my_title}


    return render_to_response('recipes/add_recipe.html', context_dict, context)

# I will want to add categories and possibly have recipes in more than one
# category. Not sure yet.
def add_category(request):
    # Get the context from the request
    context = RequestContext(request)
    cat_list = get_category_list()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details
        form = CategoryForm()
        context_dict = {'cat_list': cat_list, 'form': form}
    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render_to_response('recipes/add_category.html', context_dict, context)

# I need categories for sure
def category(request, category_name_url):
    # Request our context from the request passed to us.
    context = RequestContext(request)
    cat_list = get_category_list()

    # Change underscores in the category name to spaces.
    category_name = decode_url(category_name_url)

    # Create a context dictionary which we can pass to the template rendering engine
    # We start by containing the name of the category passed by the user
    context_dict = {'category_name': category_name, 'cat_list': cat_list,
                    'category_name_url': category_name_url}

    try:
        # Can we find a category with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance of raises an exception.
        # We also do a case insensitive match
        category = Category.objects.get(name__iexact=category_name)
        context_dict['category'] = category

        # Adds our results list to the template context under name pages.
        context_dict['recipe_list'] = get_recipe_list(category_id=category.id).order_by('-views')

    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    if request.method == 'POST':
        query = request.POST.get('query')
        if query:
            query = query.strip()
            result_list = run_query(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list

    # Go render the response and return it to the client.
    return render_to_response('recipes/category.html', context_dict, context)

def show_recipe(request, recipe_id):
    context = RequestContext(request)
    context_dict = {}
    try:
        context_dict['recipe'] = Recipe.objects.get(pk=recipe_id)
    except Recipe.DoesNotExist:
        pass

    return render_to_response('recipes/recipe.html', context_dict, context)


# I'll want an index page of course
def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)
    cat_list = get_category_list()

    # Query the databas for a list of ALL categories currently stored
    # Order the categories by no. likes in descending order
    # Retrieve the top 5 only - or all if less than 5
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    # Construct a dictionary to pass to the template engine as its context.
    category_list = Category.objects.order_by('-likes')[:5]
    context_dict = {'categories': category_list}
    context_dict['cat_list'] = cat_list 

    # We loop through each category returned, and create a URL attribute
    # This attribute stores an encoded URL (e.g. spaces replaced with underscores)
    for category in category_list:
       # category.url = category.name.replace(' ', '_')
       category.url = encode_url(category.name)

    recipe_list = Recipe.objects.order_by('-views')[:5]
    context_dict['recipes'] = recipe_list

    default_category = Category.objects.get(name='Unfiled')
    context_dict['category'] = default_category

    # Does the cookie last_visit exist?
    if request.session.get('last_visit'):
        # The session has a value for the last visit
        last_visit = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        # If it's been more than a day since the last visit...
        if (datetime.now() - last_visit_time).days > 0:
            # ....reassign the value of the cookie to +1 of what it was before...
            request.session['visits'] = visits + 1
            #...and update the last visit cookie, too.
            request.session['last_visit'] = str(datetime.now())
    else:
        # The get returns None, and the session does not have a value for the last visit 
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1

    if request.method == 'POST':
        query = request.POST.get('query')
        if query:
            query = query.strip()
            result_list = run_query(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list

    # Return a rendered response to send to the client.
    # We make use of the shortcut function to make our lives easier.
    # Note that the first parameter is the template we wish to use.
    return render_to_response('recipes/index.html', context_dict, context)

# I will keep both encode and decode url
def encode_url(str):
    return str.replace(' ', '_')

def decode_url(str):
    return str.replace('_', ' ')

# I suppose I can have an about page that explains the purpose
# of the recipe site along with some contact info just in case.
def about(request):
    context = RequestContext(request)
    cat_list = get_category_list()

    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0
    context_dict = {'boldmessage': "Welcome visitor  ", 'visits': count,
                    'cat_list': cat_list}

    return render_to_response('recipes/about.html', context_dict, context)
