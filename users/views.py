from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Post, Like, Comment, UserProfile, Memory

# --- CHAT REDIRECT ---
@login_required
def go_to_chat_with_user5(request):
    user5 = get_object_or_404(User, id=5)
    return redirect('chat', room_name=user5.username)

@login_required
def redirect_to_user5_chat(request):
    user = get_object_or_404(User, id=5)
    return redirect('chat', room_name=user.username)

# --- POST LIKES ---
@require_POST
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like_obj, created = Like.objects.get_or_create(post=post, user=request.user)

    if not created:
        like_obj.delete()
        liked = False
    else:
        liked = True

    like_count = post.likes.count()
    return JsonResponse({'liked': liked, 'like_count': like_count})

# --- COMMENTS ---
@login_required
def comment_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        comment_content = request.POST.get('comment')
        if comment_content:
            Comment.objects.create(post=post, content=comment_content, user=request.user)
        return redirect('posts')

# --- CREATE POST ---
@login_required
def new_post_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        photo = request.FILES.get('photo')

        if photo:
            fs = FileSystemStorage()
            filename = fs.save(photo.name, photo)
            Post.objects.create(author=request.user, title=title, content=content, photo=filename)
        else:
            Post.objects.create(author=request.user, title=title, content=content)

        return redirect('posts')

    return render(request, 'new_post.html')

# --- DISPLAY POSTS ---
@login_required
def posts_page(request):
    posts = Post.objects.all().order_by('-created_at')
    user_liked_post_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)

    return render(request, 'posts.html', {
        'posts': posts,
        'user_liked_post_ids': user_liked_post_ids,
    })

# --- HOMEPAGE ---
@login_required
def home_page(request):
    return render(request, 'chat.html')

# --- INDEX PAGE ---
def index_page(request):
    return render(request, 'index.html')

from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            # Check if user is banned
            if hasattr(user, 'is_banned') and user.is_banned:  # assuming you have is_banned field
                return redirect('banned_account_page')

            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('posts')
        else:
            messages.error(request, 'Invalid username or password.')

    # If already logged in, redirect
    if request.user.is_authenticated:
        # Optional: check banned status even for logged-in users
        if hasattr(request.user, 'is_banned') and request.user.is_banned:
            return redirect(request, 'BannedAccount.html')
        return redirect('posts')

    return render(request, 'login.html')


# --- LOGOUT ---
@login_required
def logout_page(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')

# --- SIGNUP ---
def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')

        if password1 != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
            return render(request, 'signup.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user_profile = UserProfile.objects.get(user=user)
        if profile_picture:
            user_profile.profile_picture = profile_picture
            user_profile.save()

        messages.success(request, 'Signup successful! You can now log in.')
        return redirect('login')

    if request.user.is_authenticated:
        return redirect('posts')
    return render(request, 'signup.html')

# --- SOULS (MEMORY WALL) ---

@login_required
def souls_tunnel(request):
    # ✅ UPDATED: fetch all memories from all users, not just the current user
    memories = Memory.objects.all().order_by('-created_at')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        memories_data = [{
            'id': memory.id,
            'name': memory.name,
            'image_url': memory.image.url,
            'caption': memory.caption,
            'created_at': memory.created_at.strftime("%b %d, %Y %I:%M %p")
        } for memory in memories]
        return JsonResponse({'memories': memories_data})

    return render(request, 'souls.html', {'memories': memories})

@login_required
@require_POST
def add_memory(request):
    name = request.POST.get('name')
    caption = request.POST.get('caption')
    image = request.FILES.get('image')

    if not all([name, caption, image]):
        return JsonResponse({'status': 'error', 'message': 'All fields are required'})

    memory = Memory.objects.create(
        user=request.user,
        name=name,
        caption=caption,
        image=image
    )

    return JsonResponse({
        'status': 'success',
        'memory': {
            'id': memory.id,
            'name': memory.name,
            'image_url': memory.image.url,
            'caption': memory.caption,
            'created_at': memory.created_at.strftime("%b %d, %Y %I:%M %p")
        }
    })

@login_required
def go_to_souls(request):
    return redirect('souls-tunnel')



#banned accounts
def banned_account_page(request):
    return render(request, "BannedAccount.html")

def unbann_accounts(request):
    return render(request, 'account_unbanned.html')

def account_banned(request):
    return render(request, 'account_banned.html')






from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.shortcuts import get_object_or_404
from dashboard.models import ManageMember

@require_POST
def ban_user(request, member_id):
    member = get_object_or_404(ManageMember, id=member_id)
    user = member.member

    member.status = False
    member.save(update_fields=["status"])

    # Kill active sessions
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in sessions:
        data = session.get_decoded()
        if str(user.id) == str(data.get('_auth_user_id')):
            session.delete()

    # Email notification
    subject = "Your Account Has Been Banned"
    html_message = render_to_string('account_banned.html', {'user': user})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email],
              html_message=html_message)

    return JsonResponse({"success": True, "new_status": member.status})


@require_POST
def unban_user(request, member_id):
    member = get_object_or_404(ManageMember, id=member_id)
    user = member.member

    member.status = True
    member.save(update_fields=["status"])

    subject = "Your Account Has Been Reactivated"
    html_message = render_to_string('account_unbanned.html', {'user': user})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email],
              html_message=html_message)

    return JsonResponse({"success": True, "new_status": member.status})


"""def banned_page(request):
    return render(request, 'BannedAccount.html')"""


"""def contact_admin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message = request.POST.get('message')
        admin_email = settings.DEFAULT_FROM_EMAIL

        full_message = f"Message from {email}:\n\n{message}"

        send_mail(
            subject='Account Ban Appeal Message',
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
        )
        # For non-AJAX pages you can still use messages framework if desired,
        # but it's unrelated to the toggle button flow now.
        return render(request, 'BannedAccount.html', {
            "sent": True
        })

    return render(request, 'BannedAccount.html')"""


#admin contact form for banned users
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from dashboard.models import Notification

@login_required
def banned_page_contact_admin(request):
    # Only banned users should see this page
    if not request.user.is_banned:  # assuming you have a field on User
        return redirect('dashindex')      # redirect normal users

    if request.method == "POST":
        email = request.POST.get('email')
        message_text = request.POST.get('message')

        # Save notification
        Notification.objects.create(
            sender=request.user,
            message=f"{email}: {message_text}"
        )
        messages.success(request, "Your message has been sent to the admin!")
        return redirect('posts')

    return render(request, 'BannedAccount.html')

#contact admin form for banned users
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from users.forms import NotificationForm
from dashboard.models import Notification

@login_required  # Ensure the user is logged in
def banned_account_page_contact_admin(request):
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            # Save the form data and assign the sender
            notification = form.save(commit=False)  # Don't save yet
            notification.sender = request.user  # Set the sender as the logged-in user
            notification.save()  # Save to the database
            
            messages.success(request, "Your message has been sent to the admin.")
            return redirect('posts')  # Redirect after successful submission
        else:
            messages.error(request, "There was an error submitting your message.")
    else:
        form = NotificationForm()

    return render(request, 'BannedAccount.html', {'form': form})

