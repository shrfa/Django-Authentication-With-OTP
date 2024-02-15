from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, is_admin=False, is_staff=False, is_active=True):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        if not username:
            username = email.split('@')[0]
        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password) 
        user.is_staff = is_staff
        user.is_active = is_active
        user.save(using=self._db)
        return user
    
    def get_by_natural_key(self, username): 
        return self.model.objects.get(username=username)

    def create_superuser(self, email=None, username=None, password=None, **extra_fields):
        if not email and not username:
            raise ValueError("At least one of the username or email values is required")
        if not email:
            email = f"{username}@gmail.com"
        if not password:
            raise ValueError("User must have a password")
        if not username:
            username = email.split('@')[0]
        user = self.model(
            username=username,
            email=self.normalize_email(email)
        )
        
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user