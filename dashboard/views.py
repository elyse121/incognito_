from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ManageMember

def dashindex(request):
    total_users = ManageMember.objects.count()

    return render(request, 'DASHBOARD/newcode/html/dashindex.html', {
        'total_users': total_users,
    })

@login_required
def allmembers_page(request):
    members = ManageMember.objects.select_related('member', 'profile').all()
    return render(request, 'DASHBOARD/newcode/html/allmembers.html', {'members': members})


from django.http import JsonResponse
from .models import ManageMember

def manage_members_api(request):
    members = ManageMember.objects.select_related('member', 'profile').all()

    # Stats
    total_members = members.count()
    banned_members = members.filter(status=False).count()
    active_members = members.filter(status=True).count()

    data = []
    for m in members:
        data.append({
            'id': m.id,
            'username': m.member.username,
            'email': m.member.email,
            'role': m.role,
            'joined': m.joined.isoformat(),
            'status': 'active' if m.status else 'banned',
            'avatar': m.profile.profile_picture.url if m.profile and m.profile.profile_picture else '/static/default-avatar.png',
        })

    return render(request, 'DASHBOARD/newcode/html/allmembers.html', {
        'members': data,
        'total_members': total_members,
        'banned_members': banned_members,
        'active_members': active_members
    })

def all_members_page(request):
    return render(request, 'DASHBOARD/newcode/html/allmembers.html')


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # for testing; replace with proper CSRF handling
@require_POST
def toggle_member_status(request, member_id):
    try:
        member = ManageMember.objects.get(id=member_id)
        member.status = not member.status
        member.save()
        return JsonResponse({'success': True})
    except ManageMember.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Member not found'}, status=404)

#prvt cht
from django.db.models import Q, Max
from django.shortcuts import render
from dashboard.models import ManageMember
from chat.models import Message

def users_with_chat_data(request):
    user_ids_with_msgs = Message.objects.values_list('sender_id', flat=True).union(
        Message.objects.values_list('receiver_id', flat=True)
    )
    members = ManageMember.objects.select_related('member', 'profile').filter(member_id__in=user_ids_with_msgs)

    table_data = []

    for mm in members:
        user_obj = mm.member

        partners = Message.objects.filter(
            Q(sender=user_obj) | Q(receiver=user_obj)
        ).values_list('sender_id', 'receiver_id')

        partner_ids = set()
        for sender_id, receiver_id in partners:
            if sender_id != user_obj.id:
                partner_ids.add(sender_id)
            if receiver_id != user_obj.id:
                partner_ids.add(receiver_id)

        chat_partners_count = len(partner_ids)

        last_active = Message.objects.filter(
            Q(sender=user_obj) | Q(receiver=user_obj)
        ).aggregate(last_time=Max('timestamp'))['last_time']

        # Get avatar URL or fallback
        avatar_url = ''
        if mm.profile and mm.profile.profile_picture:
            avatar_url = mm.profile.profile_picture.url
        else:
            avatar_url = '/static/default-avatar.png'  # or any default image you have

        table_data.append({
            'username': user_obj.username,
            'avatar': avatar_url,
            'chat_partners': chat_partners_count,
            'last_active': last_active,
            'status': "Active" if mm.status else "Banned",
        })

    return render(request, 'DASHBOARD/newcode/html/PrivateMessages.html', {
        'users': table_data
    })




from django.db.models import Q
from django.shortcuts import render
from dashboard.models import ManageMember
from chat.models import Message
from django.contrib.auth.models import User

def private_messages_admin(request):
    # Get all user IDs who sent or received messages
    user_ids_with_msgs = set(
        Message.objects.values_list('sender_id', flat=True)
        .union(Message.objects.values_list('receiver_id', flat=True))
    )

    members_data = []

    # Loop over all users who appear in messages
    users = User.objects.filter(id__in=user_ids_with_msgs)

    for user in users:
        # Get all messages where user is sender or receiver
        user_msgs = Message.objects.filter(Q(sender=user) | Q(receiver=user))

        # Get unique partner IDs (people who sent or received messages with this user, excluding self)
        senders = set(
            user_msgs.exclude(sender=user).values_list('sender_id', flat=True)
        )
        receivers = set(
            user_msgs.exclude(receiver=user).values_list('receiver_id', flat=True)
        )
        partner_ids = senders.union(receivers)

        partners = User.objects.filter(id__in=partner_ids)

        # Last active timestamp from messages
        last_active_msg = user_msgs.order_by('-timestamp').first()
        last_active = last_active_msg.timestamp if last_active_msg else None

        # ✅ Fetch status from ManageMember
        member_record = ManageMember.objects.filter(member=user).first()
        status = member_record.status if member_record else None

        members_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar_url': user.userprofile.profile_picture.url if hasattr(user, 'userprofile') and user.userprofile.profile_picture else 'https://via.placeholder.com/40',
            'partners_count': partners.count(),
            'last_active': last_active,
            'status': status,  # ✅ Corrected status here
            'partners': [
                {
                    'id': p.id,
                    'username': p.username,
                    'email': p.email,
                    'avatar_url': p.userprofile.profile_picture.url if hasattr(p, 'userprofile') and p.userprofile.profile_picture else 'https://via.placeholder.com/50',
                } for p in partners
            ]
        })

    return render(request, 'DASHBOARD/newcode/html/PrivateMessages.html', {
        'members_data': members_data
    })


"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from chat.models import Message
from django.contrib.auth.models import User

@login_required
def get_conversation(request):
    user_id = request.user.id
    partner_id = request.GET.get('partner_id')

    if not partner_id:
        return JsonResponse({'error': 'partner_id is required'}, status=400)

    try:
        partner = User.objects.get(id=partner_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Partner not found'}, status=404)

    # Fetch messages between the two users, ordered by timestamp ascending
    messages = Message.objects.filter(
        (Q(sender_id=user_id) & Q(receiver_id=partner_id)) |
        (Q(sender_id=partner_id) & Q(receiver_id=user_id))
    ).order_by('timestamp')

    # Serialize messages into a list of dicts
    messages_list = []
    for msg in messages:
        messages_list.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_username': msg.sender.username,
            'receiver_id': msg.receiver_id,
            'receiver_username': msg.receiver.username,
            'message': msg.message,
            'timestamp': msg.timestamp.isoformat(),
        })

    return JsonResponse({
        'partner': {
            'id': partner.id,
            'username': partner.username,
            # add avatar url if needed here
        },
        'messages': messages_list,
    })

"""    

import csv
from io import StringIO
from django.http import JsonResponse, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from chat.models import Message


@staff_member_required  # only admin/staff can use this
@require_GET
def conversation_view(request):
    """
    JSON API for messages between user_id and partner_id
    """
    user_id = request.GET.get("user_id")
    partner_id = request.GET.get("partner_id")

    if not user_id or not partner_id:
        return JsonResponse({"error": "user_id and partner_id are required"}, status=400)

    try:
        user_id = int(user_id)
        partner_id = int(partner_id)
    except ValueError:
        return JsonResponse({"error": "IDs must be integers"}, status=400)

    # Ensure users exist
    get_object_or_404(User, id=user_id)
    get_object_or_404(User, id=partner_id)

    qs = (
        Message.objects
        .filter(
            Q(sender_id=user_id, receiver_id=partner_id) |
            Q(sender_id=partner_id, receiver_id=user_id)
        )
        .select_related("sender", "receiver")
        .order_by("timestamp")
    )

    messages_data = [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_username": m.sender.username,
            "receiver_id": m.receiver_id,
            "message": m.content,
            "timestamp": m.timestamp.isoformat(),
        }
        for m in qs
    ]

    return JsonResponse({"messages": messages_data}, status=200)


@staff_member_required
@require_GET
def export_conversation_csv(request):
    """
    Exports conversation as CSV for given user_id + partner_id
    """
    user_id = request.GET.get("user_id")
    partner_id = request.GET.get("partner_id")

    if not user_id or not partner_id:
        return HttpResponse("Missing parameters", status=400)

    qs = (
        Message.objects
        .filter(
            Q(sender_id=user_id, receiver_id=partner_id) |
            Q(sender_id=partner_id, receiver_id=user_id)
        )
        .select_related("sender", "receiver")
        .order_by("timestamp")
    )

    # Prepare CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Sender", "Receiver", "Message"])

    for m in qs:
        writer.writerow([
            m.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            m.sender.username,
            m.receiver.username,
            m.content.replace("\n", " ")  # keep CSV one-line
        ])

    response = HttpResponse(output.getvalue(), content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="conversation_{user_id}_{partner_id}.csv"'
    return response


#forban

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.contrib.auth.models import User

from dashboard.models import BlockedConversation
from chat.models import Message


def is_blocked(user1, user2):
    """
    Returns True if user1 and user2 are blocked from chatting with each other.
    Checks both directions.
    """
    return BlockedConversation.objects.filter(
        (Q(user1=user1) & Q(user2=user2)) | (Q(user1=user2) & Q(user2=user1))
    ).exists()


@login_required
@require_POST
def toggle_block_conversation(request):
    """
    Toggle block/unblock between two users.
    """
    if not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)

    user1_id = request.POST.get("user1_id")
    user2_id = request.POST.get("user2_id")

    if not user1_id or not user2_id:
        return JsonResponse({"error": "Missing user ids"}, status=400)

    try:
        user1 = User.objects.get(id=int(user1_id))
        user2 = User.objects.get(id=int(user2_id))

        # Check if already blocked
        blocked = BlockedConversation.objects.filter(
            (Q(user1=user1) & Q(user2=user2)) | (Q(user1=user2) & Q(user2=user1))
        ).first()

        if blocked:
            # Unblock
            blocked.delete()
            action = "unblocked"
            blocked_status = False
        else:
            # Block conversation
            BlockedConversation.objects.create(user1=user1, user2=user2)
            action = "blocked"
            blocked_status = True

            # Send emails to both users
            subject = "Chat Restriction Notice"
            from_email = "elyseniyonzima202@gmail.com"
            send_mail(subject, f"You are not allowed to chat with {user2.username} anymore.", from_email, [user1.email], fail_silently=False)
            send_mail(subject, f"You are not allowed to chat with {user1.username} anymore.", from_email, [user2.email], fail_silently=False)

        return JsonResponse({
            "success": True,
            "blocked": blocked_status,
            "message": f"Conversation between {user1.username} and {user2.username} is now {action}."
        })

    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_POST
def send_message(request):
    """
    Save a message if the conversation is not blocked.
    """
    receiver_id = request.POST.get("receiver_id")
    content = request.POST.get("content")

    if not receiver_id or not content:
        return JsonResponse({"error": "Missing receiver or content"}, status=400)

    try:
        receiver = User.objects.get(id=int(receiver_id))

        # Check if conversation is blocked
        if is_blocked(request.user, receiver):
            return JsonResponse({"error": "You are not allowed to chat with this user."}, status=403)

        # Save message
        msg = Message.objects.create(sender=request.user, receiver=receiver, content=content)
        return JsonResponse({"success": True, "message": msg.content})

    except User.DoesNotExist:
        return JsonResponse({"error": "Receiver not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


#save Notification messages from contact admin form(BannedAccounts)
"""from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from dashboard.forms import NotificationForm
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
"""





def privatemessages(request):
    return render(request, 'DASHBOARD/newcode/html/PrivateMessages.html')

def groupchats(request):
    return render(request, 'DASHBOARD/newcode/html/GroupMessages.html')

def darkmessages(request):
    return render(request, 'DASHBOARD/newcode/html/DarkMessages.html')

def reportemessages(request):
    return render(request, 'DASHBOARD/newcode/html/ReportedMessages.html')

def privacydash(request):
    return render(request, 'DASHBOARD/newcode/html/PrivacyDash.html')

def manageposts(request):
    return render(request, 'DASHBOARD/newcode/html/ManagePost.html')

def useractivity(request):
    return render(request, 'DASHBOARD/newcode/html/UserActivity.html')
