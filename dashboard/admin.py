# members/admin.py
from django.contrib import admin
from dashboard.models import ManageMember, BlockedConversation, Notification




@admin.register(ManageMember)
class ManageMemberAdmin(admin.ModelAdmin):
    list_display = ('member_id', 'member', 'profile_display', 'role', 'status', 'joined')
    search_fields = ('member__username', 'member__email')
    list_filter = ('status',)

    def profile_display(self, obj):
        return getattr(obj.profile, 'profile_picture', None) or "No Profile"
    profile_display.short_description = 'Profile'

    def member_id(self, obj):
        return obj.member.id
    member_id.short_description = 'Member ID'


@admin.register(BlockedConversation)
class BlockedConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'blocked_at')
    search_fields = ('user1__username', 'user2__username')
    list_filter = ('blocked_at',)   


#admin Notifications table
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'message', 'created_at', 'is_read')
    list_filter = ('read', 'created_at')
    search_fields = ('sender__username', 'message')
    readonly_fields = ('created_at',)

    def is_read(self, obj):
        return obj.read
    is_read.boolean = True  # shows a nice icon in admin
    is_read.admin_order_field = 'read'

