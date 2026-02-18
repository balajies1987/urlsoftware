import json
import os
from django.shortcuts import render, redirect
from django.contrib import messages

# Hardcoded credentials
VALID_USERNAME = 'admin'
VALID_PASSWORD = 'admin123'


def login_view(request):
    """Login page - authenticates with hardcoded credentials."""
    # If already logged in, redirect to home
    if request.session.get('is_authenticated'):
        return redirect('skulookup:home')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            request.session['is_authenticated'] = True
            request.session['username'] = username
            return redirect('skulookup:home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'skulookup/login.html')


def home_view(request):
    """Home page - SKU lookup from JSON data."""
    # Check authentication
    if not request.session.get('is_authenticated'):
        return redirect('skulookup:login')

    product = None
    search_query = ''
    not_found = False

    if request.method == 'POST':
        search_query = request.POST.get('icode', '').strip()

        if search_query:
            # Load products from JSON
            json_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'data', 'products.json'
            )

            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # The JSON is a flat array of objects with
                # "Icode", "Description", "Image Url" fields
                products_list = data if isinstance(data, list) else data.get('products', [])

                # Search for matching SKU (case-insensitive)
                for item in products_list:
                    item_icode = str(item.get('Icode', item.get('icode', '')))
                    if item_icode.lower() == search_query.lower():
                        # Normalize field names for template use
                        product = {
                            'icode': item_icode,
                            'description': str(item.get('Description', item.get('description', ''))),
                            'image': str(item.get('Image Url', item.get('image', ''))),
                        }
                        break

                if not product:
                    not_found = True
            except FileNotFoundError:
                messages.error(request, 'Product data file not found.')
            except json.JSONDecodeError:
                messages.error(request, 'Error reading product data.')

    context = {
        'product': product,
        'search_query': search_query,
        'not_found': not_found,
    }
    return render(request, 'skulookup/home.html', context)


def logout_view(request):
    """Logout - clears session and redirects to login."""
    request.session.flush()
    return redirect('skulookup:login')
