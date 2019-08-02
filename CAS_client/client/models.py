from django.db import models

# Create your models here.

class SessionTicket(models.Model):
    session_key = models.CharField(max_length=255)
    ticket = models.CharField(max_length=255)

    @classmethod
    def clean_deleted_sessions(cls):
        for st in cls.objects.all():
            session = SessionStore(session_key=st.session_key)
            user = get_user_from_session(session)
            if not user.is_authenticated:
                st.delete()
