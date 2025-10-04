# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone
import random
import string

from .models import Post, Like, Comment, UserProfile, Memory
from dashboard.models import ManageMember, Notification

# --------------------
# HELPER
# --------------------
def generate_profile_code():
    return (
        random.choice(string.ascii_uppercase) +
        str(random.randint(1, 9)) +
        '-' +
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=2)) +
        '-' +
        ''.join(random.choices(string.ascii_uppercase + string.digits, k=2))
    )

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

# --- LOGIN ---
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            user_profile = UserProfile.objects.get(user=user)
            if not user_profile.is_verified:
                messages.error(request, 'Please verify your email before logging in.')
                return render(request, 'login.html')

            # Check if user is banned
            if hasattr(user, 'is_banned') and user.is_banned:  # optional field
                messages.error(request, "Your account is banned.")
                return redirect('banned_account_page')  # your banned page

            if user.is_active:
                login(request, user)
                messages.success(request, 'Login successful!')

                # Admin check: active + staff + superuser
                if user.is_staff and user.is_superuser:
                    return redirect('dashindex')  # admin dashboard
                else:
                    return redirect('posts')      # normal active user page
            else:
                messages.error(request, "This account is inactive. Please contact admin.")
        else:
            messages.error(request, 'Invalid username or password.')

    # If already logged in, redirect accordingly
    if request.user.is_authenticated:
        if hasattr(request.user, 'is_banned') and request.user.is_banned:
            messages.error(request, "Your account is banned.")
            return redirect('banned_account_page')

        if request.user.is_active:
            if request.user.is_staff and request.user.is_superuser:
                return redirect('dashindex')
            else:
                return redirect('index')
        else:
            messages.error(request, "Your account is inactive. Please contact admin.")

    return render(request, 'login.html')

# --- LOGOUT ---
@login_required
def logout_page(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('/')

# --------------------
# SIGNUP + VERIFICATION
# --------------------
def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_picture = request.FILES.get('profile_picture')

        # Password check
        if password1 != confirm_password:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": "Passwords do not match"})
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        # Email uniqueness check
        if User.objects.filter(email=email).exists():
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": "Email is already in use"})
            messages.error(request, 'Email is already in use.')
            return render(request, 'signup.html')

        # Create user + profile
        user = User.objects.create_user(username=username, email=email, password=password1)
        user_profile, created = UserProfile.objects.get_or_create(user=user)
        user_profile.profile_code = generate_profile_code()
        user_profile.verification_token = user_profile.generate_verification_token()
        if profile_picture:
            user_profile.profile_picture = profile_picture
        user_profile.save()

        # Build verification link
        verification_link = f"http://127.0.0.1:8000/verify/?token={user_profile.verification_token}"

        # Send email
        send_mail(
            subject="Verify Your Best Friends Portal Account",
            message=(
                f"Hello {username},\n\n"
                f"Your profile code is: {user_profile.profile_code}\n\n"
                f"Please verify your email by clicking this link: {verification_link}\n"
                f"This link expires in 30 minutes."
            ),
            from_email="elyseniyonzima202@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )

        # Response (Ajax vs normal form)
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({'success': True, 'message': 'Please check your email to verify your account.'})

        messages.success(request, 'Signup successful! Please check your email to verify your account.')
        return redirect('login')

    if request.user.is_authenticated:
        return redirect('posts')
    return render(request, 'signup.html')


def verify_email(request):
    """Handle email verification"""
    token = request.GET.get('token')
    if not token:
        messages.error(request, 'Invalid verification link.')
        return render(request, 'verify.html')

    try:
        user_profile = UserProfile.objects.get(verification_token=token, is_verified=False)
        user_profile.is_verified = True
        user_profile.verification_token = None  # expire token
        user_profile.save()
        messages.success(request, 'Email verified! You can now log in.')
        return render(request, 'verify.html')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return render(request, 'verify.html')

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
def unbann_accounts(request):
    return render(request, 'account_unbanned.html')

def account_banned(request):
    return render(request, 'account_banned.html')

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

def banned_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        message_content = request.POST.get('message')
        
        # Get the banned user (you might need to adjust this logic)
        # This assumes the user is logged in even when banned
        if request.user.is_authenticated:
            sender = request.user
        else:
            # If user is not logged in, you might need to get the user by email
            # or create a placeholder user. Adjust based on your needs.
            try:
                sender = User.objects.get(email=email)
            except User.DoesNotExist:
                # Create a notification without a user if needed
                sender = None
        
        # Create the notification
        if sender:
            Notification.objects.create(
                sender=sender,
                message=message_content,
                email=email
            )
            messages.success(request, 'Your message has been sent to the admin.')
        else:
            # Handle case where we can't find a user
            # You might want to log this or handle differently
            messages.error(request, 'There was an error sending your message.')
        
        return redirect('thank_you')
    
    return render(request, 'BannedAccount.html')


def thank_you(request):
    return render(request, 'thank_you.html')