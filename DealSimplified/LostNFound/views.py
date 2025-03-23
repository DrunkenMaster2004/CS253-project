from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from marketplace.models import Profile
from .models import LostItem, FoundItem, LostFoundCategory, Claim, Match, ItemImage
from .forms import LostItemForm, FoundItemForm, LostItemImageFormSet, FoundItemImageFormSet, ClaimForm

def home(request):
    lost_items = LostItem.objects.filter(status='open').order_by('-date_reported')[:5]
    found_items = FoundItem.objects.filter(status='open').order_by('-date_reported')[:5]
    categories = LostFoundCategory.objects.all()
    
    context = {
        'lost_items': lost_items,
        'found_items': found_items,
        'categories': categories,
    }
    return render(request, 'LostNFound/home.html', context)

@login_required
def report_lost_item(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST)
        if form.is_valid():
            lost_item = form.save(commit=False)
            profile = Profile.objects.get(user=request.user)
            lost_item.reporter = profile
            lost_item.save()
            
            image_formset = LostItemImageFormSet(request.POST, request.FILES, instance=lost_item)
            if image_formset.is_valid():
                image_formset.save()
                
                find_potential_matches(lost_item)
                
                messages.success(request, 'Your lost item has been reported!')
                return redirect('lost_item_detail', item_id=lost_item.id)
            else:
                lost_item.delete()
                messages.error(request, 'There was an error with the uploaded images.')
    else:
        form = LostItemForm()
        image_formset = LostItemImageFormSet()
    
    return render(request, 'LostNFound/report_lost_item.html', {
        'form': form,
        'image_formset': image_formset
    })

@login_required
def report_found_item(request):
    if request.method == 'POST':
        form = FoundItemForm(request.POST)
        if form.is_valid():
            found_item = form.save(commit=False)
            profile = Profile.objects.get(user=request.user)
            found_item.reporter = profile
            found_item.save()
            
            image_formset = FoundItemImageFormSet(request.POST, request.FILES, instance=found_item)
            if image_formset.is_valid():
                image_formset.save()
                
                find_potential_matches_for_found(found_item)
                
                messages.success(request, 'Your found item has been reported!')
                return redirect('found_item_detail', item_id=found_item.id)
            else:
                found_item.delete()
                messages.error(request, 'There was an error with the uploaded images.')
    else:
        form = FoundItemForm()
        image_formset = FoundItemImageFormSet()
    
    return render(request, 'LostNFound/report_found_item.html', {
        'form': form,
        'image_formset': image_formset
    })

def lost_item_detail(request, item_id):
    lost_item = get_object_or_404(LostItem, id=item_id)
    matches = Match.objects.filter(lost_item=lost_item).order_by('-match_percentage')
    
    context = {
        'item': lost_item,
        'matches': matches,
    }
    return render(request, 'LostNFound/lost_item_detail.html', context)

def found_item_detail(request, item_id):
    found_item = get_object_or_404(FoundItem, id=item_id)
    matches = Match.objects.filter(found_item=found_item).order_by('-match_percentage')
    claims = Claim.objects.filter(found_item=found_item)
    
    user_has_claimed = False
    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        user_has_claimed = Claim.objects.filter(found_item=found_item, claimant=profile).exists()
    
    context = {
        'item': found_item,
        'matches': matches,
        'claims': claims,
        'user_has_claimed': user_has_claimed,
    }
    return render(request, 'LostNFound/found_item_detail.html', context)

@login_required
def claim_found_item(request, item_id):
    found_item = get_object_or_404(FoundItem, id=item_id)
    profile = Profile.objects.get(user=request.user)
    
    if Claim.objects.filter(found_item=found_item, claimant=profile).exists():
        messages.info(request, 'You have already claimed this item.')
        return redirect('found_item_detail', item_id=found_item.id)
    
    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.found_item = found_item
            claim.claimant = profile
            claim.save()
            
            messages.success(request, 'Your claim has been submitted. The finder will review your claim.')
            return redirect('found_item_detail', item_id=found_item.id)
    else:
        form = ClaimForm()
    
    return render(request, 'LostNFound/claim_item.html', {
        'form': form,
        'item': found_item
    })

@login_required
def review_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    
    if claim.found_item.reporter.user != request.user:
        messages.error(request, 'You are not authorized to review this claim.')
        return redirect('found_item_detail', item_id=claim.found_item.id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            claim.status = 'approved'
            claim.save()
            
            claim.found_item.status = 'claimed'
            claim.found_item.save()
            
            other_claims = Claim.objects.filter(found_item=claim.found_item).exclude(id=claim.id)
            other_claims.update(status='rejected')
            
            messages.success(request, 'You have approved this claim. The item has been marked as claimed.')
        
        elif action == 'reject':
            claim.status = 'rejected'
            claim.save()
            messages.success(request, 'You have rejected this claim.')
        
        return redirect('found_item_detail', item_id=claim.found_item.id)
    
    return render(request, 'LostNFound/review_claim.html', {'claim': claim})

def lost_items_list(request):
    items = LostItem.objects.all().order_by('-date_reported')
    categories = LostFoundCategory.objects.all()
    
    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)
    
    status = request.GET.get('status')
    if status:
        items = items.filter(status=status)
    
    days = request.GET.get('days')
    if days:
        from datetime import timedelta
        from django.utils import timezone
        items = items.filter(date_reported__gte=timezone.now() - timedelta(days=int(days)))
    
    query = request.GET.get('q')
    if query:
        items = items.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(lost_location__icontains=query) |
            Q(color__icontains=query)
        )
    
    context = {
        'items': items,
        'categories': categories,
        'category_id': category_id if category_id else '',
        'status': status if status else '',
        'days': days if days else '',
        'query': query if query else '',
    }
    return render(request, 'LostNFound/lost_items_list.html', context)

def found_items_list(request):
    items = FoundItem.objects.all().order_by('-date_reported')
    categories = LostFoundCategory.objects.all()
    
    category_id = request.GET.get('category')
    if category_id:
        items = items.filter(category_id=category_id)
    
    status = request.GET.get('status')
    if status:
        items = items.filter(status=status)
    
    days = request.GET.get('days')
    if days:
        from datetime import timedelta
        from django.utils import timezone
        items = items.filter(date_reported__gte=timezone.now() - timedelta(days=int(days)))
    
    query = request.GET.get('q')
    if query:
        items = items.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(found_location__icontains=query) |
            Q(color__icontains=query)
        )
    
    context = {
        'items': items,
        'categories': categories,
        'category_id': category_id if category_id else '',
        'status': status if status else '',
        'days': days if days else '',
        'query': query if query else '',
    }
    return render(request, 'LostNFound/found_items_list.html', context)

@login_required
def my_lost_items(request):
    profile = Profile.objects.get(user=request.user)
    my_items = LostItem.objects.filter(reporter=profile).order_by('-date_reported')
    
    return render(request, 'LostNFound/my_lost_items.html', {'items': my_items})

@login_required
def my_found_items(request):
    profile = Profile.objects.get(user=request.user)
    my_items = FoundItem.objects.filter(reporter=profile).order_by('-date_reported')
    
    return render(request, 'LostNFound/my_found_items.html', {'items': my_items})

@login_required
def edit_lost_item(request, item_id):
    lost_item = get_object_or_404(LostItem, id=item_id)
    
    if lost_item.reporter.user != request.user:
        messages.error(request, 'You are not authorized to edit this item.')
        return redirect('lost_item_detail', item_id=lost_item.id)
    
    if request.method == 'POST':
        form = LostItemForm(request.POST, instance=lost_item)
        if form.is_valid():
            form.save()
            
            image_formset = LostItemImageFormSet(request.POST, request.FILES, instance=lost_item)
            if image_formset.is_valid():
                image_formset.save()
                
                find_potential_matches(lost_item)
                
                messages.success(request, 'Your lost item has been updated!')
                return redirect('lost_item_detail', item_id=lost_item.id)
    else:
        form = LostItemForm(instance=lost_item)
        image_formset = LostItemImageFormSet(instance=lost_item)
    
    return render(request, 'LostNFound/edit_lost_item.html', {
        'form': form,
        'image_formset': image_formset,
        'item': lost_item
    })

@login_required
def edit_found_item(request, item_id):
    found_item = get_object_or_404(FoundItem, id=item_id)
    
    if found_item.reporter.user != request.user:
        messages.error(request, 'You are not authorized to edit this item.')
        return redirect('found_item_detail', item_id=found_item.id)
    
    if request.method == 'POST':
        form = FoundItemForm(request.POST, instance=found_item)
        if form.is_valid():
            form.save()
            
            image_formset = FoundItemImageFormSet(request.POST, request.FILES, instance=found_item)
            if image_formset.is_valid():
                image_formset.save()
                
                find_potential_matches_for_found(found_item)
                
                messages.success(request, 'Your found item has been updated!')
                return redirect('found_item_detail', item_id=found_item.id)
    else:
        form = FoundItemForm(instance=found_item)
        image_formset = FoundItemImageFormSet(instance=found_item)
    
    return render(request, 'LostNFound/edit_found_item.html', {
        'form': form,
        'image_formset': image_formset,
        'item': found_item
    })

@login_required
def close_lost_item(request, item_id):
    lost_item = get_object_or_404(LostItem, id=item_id)
    
    if lost_item.reporter.user != request.user:
        messages.error(request, 'You are not authorized to close this item.')
        return redirect('lost_item_detail', item_id=lost_item.id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'close':
            lost_item.status = 'closed'
            lost_item.save()
            messages.success(request, 'Your lost item has been closed.')
            return redirect('my_lost_items')
        
        elif action == 'reopen':
            lost_item.status = 'open'
            lost_item.save()
            messages.success(request, 'Your lost item has been reopened.')
            return redirect('lost_item_detail', item_id=lost_item.id)
    
    return render(request, 'LostNFound/close_lost_item.html', {'item': lost_item})

@login_required
def close_found_item(request, item_id):
    found_item = get_object_or_404(FoundItem, id=item_id)
    
    if found_item.reporter.user != request.user:
        messages.error(request, 'You are not authorized to close this item.')
        return redirect('found_item_detail', item_id=found_item.id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'close':
            found_item.status = 'closed'
            found_item.save()
            messages.success(request, 'Your found item has been closed.')
            return redirect('my_found_items')
        
        elif action == 'reopen':
            found_item.status = 'open'
            found_item.save()
            messages.success(request, 'Your found item has been reopened.')
            return redirect('found_item_detail', item_id=found_item.id)
    
    return render(request, 'LostNFound/close_found_item.html', {'item': found_item})

def confirm_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    
    if not (request.user == match.lost_item.reporter.user or request.user == match.found_item.reporter.user):
        messages.error(request, 'You are not authorized to confirm this match.')
        return redirect('lost_item_detail', item_id=match.lost_item.id)
    
    if request.method == 'POST':
        match.is_confirmed = True
        match.save()
        
        match.lost_item.status = 'found'
        match.lost_item.save()
        
        match.found_item.status = 'claimed'
        match.found_item.save()
        
        messages.success(request, 'Match confirmed! The items have been updated.')
        
        if request.user == match.lost_item.reporter.user:
            return redirect('lost_item_detail', item_id=match.lost_item.id)
        else:
            return redirect('found_item_detail', item_id=match.found_item.id)
    
    return render(request, 'LostNFound/confirm_match.html', {'match': match})

def find_potential_matches(lost_item):
    potential_matches = FoundItem.objects.filter(
        status='open',
        category=lost_item.category
    )
    
    for found_item in potential_matches:
        match_score = 0
        total_attributes = 5  
        
        if lost_item.name.lower() in found_item.name.lower() or found_item.name.lower() in lost_item.name.lower():
            match_score += 1
        
        if lost_item.color.lower() == found_item.color.lower():
            match_score += 1
        
        lost_words = set(lost_item.description.lower().split())
        found_words = set(found_item.description.lower().split())
        common_words = lost_words.intersection(found_words)
        if len(common_words) > 2:  # If they share more than 2 words
            match_score += 1
        
        if lost_item.lost_location.lower() in found_item.found_location.lower() or found_item.found_location.lower() in lost_item.lost_location.lower():
            match_score += 1
        
        import datetime
        date_diff = abs((found_item.found_date - lost_item.lost_date).days)
        if date_diff <= 3:
            match_score += 1
        
        match_percentage = (match_score / total_attributes) * 100
        
        if match_percentage >= 40:
            Match.objects.update_or_create(
                lost_item=lost_item,
                found_item=found_item,
                defaults={'match_percentage': match_percentage}
            )

def find_potential_matches_for_found(found_item):
    potential_matches = LostItem.objects.filter(
        status='open',
        category=found_item.category
    )
    
    for lost_item in potential_matches:

        match_score = 0
        total_attributes = 5  
        

        if lost_item.name.lower() in found_item.name.lower() or found_item.name.lower() in lost_item.name.lower():
            match_score += 1
        
 
        if lost_item.color.lower() == found_item.color.lower():
            match_score += 1
        

        lost_words = set(lost_item.description.lower().split())
        found_words = set(found_item.description.lower().split())
        common_words = lost_words.intersection(found_words)
        if len(common_words) > 2: 
            match_score += 1
        

        if lost_item.lost_location.lower() in found_item.found_location.lower() or found_item.found_location.lower() in lost_item.lost_location.lower():
            match_score += 1
        

        import datetime
        date_diff = abs((found_item.found_date - lost_item.lost_date).days)
        if date_diff <= 3:
            match_score += 1

        match_percentage = (match_score / total_attributes) * 100
        

        if match_percentage >= 40:
            Match.objects.update_or_create(
                lost_item=lost_item,
                found_item=found_item,
                defaults={'match_percentage': match_percentage}
            )