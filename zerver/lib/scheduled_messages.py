from django.utils.translation import gettext as _

from zerver.lib.exceptions import ResourceNotFoundError
from zerver.models import ScheduledMessage, UserProfile
from zerver.models.scheduled_jobs import (
    APIReminderDirectMessageDict,
    APIScheduledDirectMessageDict,
    APIScheduledStreamMessageDict,
)


def access_scheduled_message(
    user_profile: UserProfile, scheduled_message_id: int
) -> ScheduledMessage:
    try:
        return ScheduledMessage.objects.get(
            id=scheduled_message_id, sender=user_profile, delivery_type=ScheduledMessage.SEND_LATER
        )
    except ScheduledMessage.DoesNotExist:
        raise ResourceNotFoundError(_("Scheduled message does not exist"))


def get_undelivered_scheduled_messages(
    user_profile: UserProfile,
) -> list[APIScheduledDirectMessageDict | APIScheduledStreamMessageDict]:
    scheduled_messages = ScheduledMessage.objects.filter(
        realm_id=user_profile.realm_id,
        sender=user_profile,
        # Notably, we don't require failed=False, since we will want
        # to display those to users.
        delivered=False,
        delivery_type=ScheduledMessage.SEND_LATER,
    ).order_by("scheduled_timestamp")
    scheduled_message_dicts: list[APIScheduledDirectMessageDict | APIScheduledStreamMessageDict] = [
        scheduled_message.to_dict() for scheduled_message in scheduled_messages
    ]
    return scheduled_message_dicts


def get_undelivered_reminders(
    user_profile: UserProfile,
) -> list[APIReminderDirectMessageDict]:
    reminders = ScheduledMessage.objects.filter(
        realm_id=user_profile.realm_id,
        sender=user_profile,
        # Notably, we don't require failed=False, since we will want
        # to display those to users.
        delivered=False,
        delivery_type=ScheduledMessage.REMIND,
    ).order_by("scheduled_timestamp")
    reminder_dicts: list[APIReminderDirectMessageDict] = [
        reminder.to_reminder_dict() for reminder in reminders
    ]
    return reminder_dicts
