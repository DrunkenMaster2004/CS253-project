from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Item, ItemCategory, Profile, Wishlist, Chat, Message, ChatThread
from .forms import UserRegisterForm, ProfileForm, ItemForm, ItemImageFormSet
from .models import Cart
from django.shortcuts import render



def home(request):
    items = Item.objects.filter(is_available=True).order_by('-date_posted')[:12]
    categories = ItemCategory.objects.all()
    context = {
        'items': items,
        'categories': categories,
    }
    return render(request, 'marketplace/home.html', context)

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            username = user_form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! Now complete your profile.')
            return redirect('create_profile')
    else:
        user_form = UserRegisterForm()
    return render(request, 'marketplace/register.html', {'user_form': user_form})

@login_required
def create_profile(request):
    if hasattr(request.user, 'profile'):
        messages.info(request, 'You already have a profile.')
        return redirect('profile')
        
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.email_id = request.user.email
            profile.save()
            messages.success(request, 'Your profile has been created!')
            return redirect('marketplace_home')
    else:
        profile_form = ProfileForm()
    
    return render(request, 'marketplace/create_profile.html', {'profile_form': profile_form})

@login_required
@login_required
def profile(request):
    # Check if profile exists, redirect if not
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        messages.info(request, 'Please complete your profile first.')
        return redirect('create_profile')
    
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        profile_form = ProfileForm(instance=profile)
    
    selling_items = Item.objects.filter(seller=profile).order_by('-date_posted')
    wishlist_items = Wishlist.objects.filter(user=profile).select_related('item')
    
    context = {
        'profile': profile,
        'profile_form': profile_form,
        'selling_items': selling_items,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'marketplace/profile.html', context)

@login_required
def add_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            profile = Profile.objects.get(user=request.user)
            item.seller = profile
            item.save()
            
            image_formset = ItemImageFormSet(request.POST, request.FILES, instance=item)
            if image_formset.is_valid():
                image_formset.save()
                messages.success(request, f'Your item "{item.name}" has been listed!')
                return redirect('item_detail', item_id=item.id)
            else:
                item.delete()  
                messages.error(request, 'There was an error with the uploaded images.')
    else:
        form = ItemForm()
        image_formset = ItemImageFormSet()
    
    return render(request, 'marketplace/add_item.html', {
        'form': form,
        'image_formset': image_formset
    })

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    if item.seller.user != request.user:
        messages.error(request, 'You are not authorized to edit this item.')
        return redirect('item_detail', item_id=item.id)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            
            image_formset = ItemImageFormSet(request.POST, request.FILES, instance=item)
            if image_formset.is_valid():
                image_formset.save()
                messages.success(request, f'Your item "{item.name}" has been updated!')
                return redirect('item_detail', item_id=item.id)
    else:
        form = ItemForm(instance=item)
        image_formset = ItemImageFormSet(instance=item)
    
    return render(request, 'marketplace/edit_item.html', {
        'form': form,
        'image_formset': image_formset,
        'item': item
    })

@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    if item.seller.user != request.user:
        messages.error(request, 'You are not authorized to delete this item.')
        return redirect('item_detail', item_id=item.id)
    
    if request.method == 'POST':
        item_name = item.name
        item.delete()
        messages.success(request, f'Your item "{item_name}" has been deleted.')
        return redirect('profile')
    
    return render(request, 'marketplace/delete_item.html', {'item': item})

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    
    item.views += 1
    item.save()
    
    is_seller = False
    in_wishlist = False
    
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        is_seller = item.seller.user == request.user
        
        if not is_seller:
            in_wishlist = Wishlist.objects.filter(user=profile, item=item).exists()
    
    similar_items = Item.objects.filter(
        category=item.category, 
        is_available=True
    ).exclude(id=item.id).order_by('-date_posted')[:4]
    
    context = {
        'item': item,
        'similar_items': similar_items,
        'in_wishlist': in_wishlist,
        'is_seller': is_seller
    }
    return render(request, 'marketplace/item_detail.html', context)

def items_list(request):
    items = Item.objects.filter(is_available=True).order_by('-date_posted')
    categories = ItemCategory.objects.all()
    
    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)
    
    query = request.GET.get('q')
    if query:
        items = items.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    context = {
        'items': items,
        'categories': categories,
        'category_id': category_id if category_id else '',
        'min_price': min_price if min_price else '',
        'max_price': max_price if max_price else '',
        'query': query if query else '',
    }
    return render(request, 'marketplace/items_list.html', context)

@login_required
def toggle_wishlist(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    profile = Profile.objects.get(user=request.user)
    
    wishlist_item, created = Wishlist.objects.get_or_create(user=profile, item=item)
    
    if not created:
        wishlist_item.delete()
        return JsonResponse({'status': 'removed', 'message': 'Item removed from wishlist'})
    
    return JsonResponse({'status': 'added', 'message': 'Item added to wishlist'})

@login_required
def my_wishlist(request):
    profile = Profile.objects.get(user=request.user)
    wishlist_items = Wishlist.objects.filter(user=profile).select_related('item')
    
    return render(request, 'marketplace/my_wishlist.html', {
        'wishlist_items': wishlist_items
    })

@login_required
def start_chat(request, item_id=None, profile_id=None):
    sender_profile = Profile.objects.get(user=request.user)
    
    if item_id:
        item = get_object_or_404(Item, id=item_id)
        receiver_profile = item.seller
        
        if sender_profile == receiver_profile:
            messages.error(request, "You can't start a chat with yourself.")
            return redirect('item_detail', item_id=item.id)
        
        existing_chat = Chat.objects.filter(
            (Q(sender=sender_profile, receiver=receiver_profile) | 
             Q(sender=receiver_profile, receiver=sender_profile)),
            item=item
        ).first()
        
        if existing_chat:
            return redirect('chat_detail', chat_id=existing_chat.id)
        
        chat = Chat.objects.create(
            sender=sender_profile,
            receiver=receiver_profile,
            item=item
        )
        
        return redirect('chat_detail', chat_id=chat.id)
    
    elif profile_id:
        receiver_profile = get_object_or_404(Profile, id=profile_id)
        
        if sender_profile == receiver_profile:
            messages.error(request, "You can't start a chat with yourself.")
            return redirect('profile')
        
        existing_chat = Chat.objects.filter(
            (Q(sender=sender_profile, receiver=receiver_profile) | 
             Q(sender=receiver_profile, receiver=sender_profile)),
            item=None
        ).first()
        
        if existing_chat:
            return redirect('chat_detail', chat_id=existing_chat.id)
        
        chat = Chat.objects.create(
            sender=sender_profile,
            receiver=receiver_profile
        )
        
        return redirect('chat_detail', chat_id=chat.id)
    
    return redirect('marketplace_home')

# @login_required
# def chat_list(request):
#     profile = Profile.objects.get(user=request.user)
    
#     chats = Chat.objects.filter(
#         Q(sender=profile) | Q(receiver=profile)
#     ).order_by('-created_at')
    
#     return render(request, 'marketplace/chat_list.html', {'chats': chats})

# @login_required
# def chat_detail(request, chat_id):
#     chat = get_object_or_404(Chat, id=chat_id)
#     profile = Profile.objects.get(user=request.user)
    
#     if chat.sender != profile and chat.receiver != profile:
#         messages.error(request, "You don't have access to this conversation.")
#         return redirect('chat_list')
    
#     unread_messages = Message.objects.filter(chat=chat, sender=chat.sender if chat.receiver == profile else chat.receiver, is_read=False)
#     unread_messages.update(is_read=True)
    
#     if request.method == 'POST':
#         content = request.POST.get('content', '').strip()
#         if content:
#             Message.objects.create(
#                 chat=chat,
#                 sender=profile,
#                 content=content
#             )
#             return redirect('chat_detail', chat_id=chat.id)
    
#     messages_list = Message.objects.filter(chat=chat).order_by('timestamp')
    
#     context = {
#         'chat': chat,
#         'messages': messages_list,
#         'profile': profile
#     }
    
#     return render(request, 'marketplace/chat_detail.html', context)
@login_required
def chat_list(request):
    profile = Profile.objects.get(user=request.user)

    chats = Chat.objects.filter(
        Q(sender=profile) | Q(receiver=profile)
    ).order_by('-created_at')

    # Add last message to each chat
    for chat in chats:
        chat.last_message = chat.messages.order_by('-timestamp').first()

    return render(request, 'marketplace/chat_list.html', {'chats': chats})


# @login_required
# def chat_detail(request, chat_id):
#     chat = get_object_or_404(Chat, id=chat_id)
#     profile = Profile.objects.get(user=request.user)
    
#     if chat.sender != profile and chat.receiver != profile:
#         messages.error(request, "You don't have access to this conversation.")
#         return redirect('chat_list')
    
#     unread_messages = Message.objects.filter(chat=chat, sender=chat.sender if chat.receiver == profile else chat.receiver, is_read=False)
#     unread_messages.update(is_read=True)
    
#     if request.method == 'POST':
#         content = request.POST.get('content', '').strip()
#         if content:
#             Message.objects.create(
#                 chat=chat,
#                 sender=profile,
#                 content=content
#             )
#             return redirect('chat_detail', chat_id=chat.id)
    
#     messages_list = Message.objects.filter(chat=chat).order_by('timestamp')
    
#     context = {
#         'chat': chat,
#         'messages': messages_list,
#         'profile': profile
#     }
    
#     return render(request, 'marketplace/chat_detail.html', context)
@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    profile = Profile.objects.get(user=request.user)
    
    # Ensure user is part of the chat
    if chat.sender != profile and chat.receiver != profile:
        messages.error(request, "You don't have access to this conversation.")
        return redirect('chat_list')
    
    # Mark unread messages as read
    Message.objects.filter(chat=chat, is_read=False).exclude(sender=profile).update(is_read=True)
    
    # Handle new message submission
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            # Create the chat message
            Message.objects.create(chat=chat, sender=profile, content=content)
            
            # Don't create a notification for regular chat messages
            # The notification should only be created in a separate notification system
            # NOT here in the chat_detail view
            
            return redirect('chat_detail', chat_id=chat.id)
    
    messages_list = Message.objects.filter(chat=chat).order_by('timestamp')
    chats = Chat.objects.filter(Q(sender=profile) | Q(receiver=profile)).order_by('-created_at')
    
    return render(request, 'marketplace/chat_detail.html', {
        'chat': chat,
        'messages': messages_list,
        'profile': profile,
        'chats': chats,
    })


@login_required
def cart_view(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to log in to view your cart.")
        return redirect('login')  # Redirect to login page

    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)

    return render(request, 'marketplace/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, item=item)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f'{item.name} added to your cart!')
    return redirect('cart')


#@login_required
#def update_cart(request, cart_id):
 #   cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)

 #   if request.method == 'POST':
  #      new_quantity = max(int(request.POST.get('quantity', 1)), 1)  # Ensures quantity is at least 1
   #     if new_quantity > 0:
    #        cart_item.quantity = new_quantity
     #       cart_item.save()
      #      messages.success(request, 'Cart updated successfully!')

 #   return redirect('cart')


@login_required
def remove_from_cart(request, cart_id):
    cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')

@login_required
def checkout(request):
    return render(request, 'marketplace/checkout.html')

