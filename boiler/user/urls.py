from boiler.routes.route import route

"""
User URLs
This is a set of urls that provide user registration and management
functionality. You can import them all at once and attach to your app
urls file like this:

    > from boiler.user.urls import user_urls
    > urls = dict()
    > urls.update(user_urls)

"""

user_urls = dict()

# user generic
user_urls['/login-password/'] = route('boiler.user.views.Login', 'user.login', ['GET', 'POST'])
user_urls['/login/'] = route('boiler.user.views.SocialLogin', 'user.social_login')
user_urls['/logout/'] = route('boiler.user.views.Logout', 'user.logout')
user_urls['/register/'] = route('boiler.user.views.Register', 'user.register', ['GET', 'POST'])
user_urls['/register/success/'] = route('boiler.user.views.RegisterSuccess', 'user.register.success')
user_urls['/register/fail/'] = route('boiler.user.views.RegisterFail', 'user.register.fail')

# confirm email
user_urls['/user/confirm-email/'] = route('boiler.user.views.ConfirmEmailRequest', 'user.confirm.email.request', ['GET', 'POST'])
user_urls['/user/confirm-email/unconfirmed/'] = route('boiler.user.views.ConfirmEmailUnconfirmed', 'user.confirm.email.unconfirmed')
user_urls['/user/confirm-email/resent/'] = route('boiler.user.views.ConfirmEmailResendOk', 'user.confirm.email.resend.ok')
user_urls['/user/confirm-email/already-confirmed/'] = route('boiler.user.views.ConfirmEmailResendAlreadyConfirmed', 'user.confirm.email.resend.already_confirmed')
user_urls['/user/confirm-email/expired/'] = route('boiler.user.views.ConfirmEmailExpired', 'user.confirm.email.expired')
user_urls['/user/confirm-email/<link>/'] = route('boiler.user.views.ConfirmEmail', 'user.confirm.email.link')

# recover password
user_urls['/user/recover-password/'] = route('boiler.user.views.RecoverPasswordRequest', 'user.recover.password.request', ['GET', 'POST'])
user_urls['/user/recover-password/sent/'] = route('boiler.user.views.RecoverPasswordRequestOk', 'user.recover.password.sent')
user_urls['/user/recover-password/expired/'] = route('boiler.user.views.RecoverPasswordExpired', 'user.recover.password.expired')
user_urls['/user/recover-password/<link>/'] = route('boiler.user.views.RecoverPassword', 'user.recover.password.link', ['GET', 'POST'])

# social
user_urls['/login/social/facebook/auth/'] = route('boiler.user.views_social.FacebookAuthorize', 'social.facebook.auth')
user_urls['/login/social/facebook/'] = route('boiler.user.views_social.FacebookHandle', 'social.facebook.handle')
user_urls['/login/social/vk/auth/'] = route('boiler.user.views_social.VkontakteAuthorize', 'social.vkontakte.auth')
user_urls['/login/social/vk/'] = route('boiler.user.views_social.VkontakteHandle', 'social.vkontakte.handle')
user_urls['/login/social/google/auth/'] = route('boiler.user.views_social.GoogleAuthorize', 'social.google.auth')
user_urls['/login/social/google/'] = route('boiler.user.views_social.GoogleHandle', 'social.google.handle')
user_urls['/login/social/twitter/auth/'] = route('boiler.user.views_social.TwitterAuthorize', 'social.twitter.auth')
user_urls['/login/social/twitter/'] = route('boiler.user.views_social.TwitterHandle', 'social.twitter.handle')
user_urls['/login/social/instagram/auth'] = route('boiler.user.views_social.InstagramAuthorize', 'social.instagram.auth')
user_urls['/login/social/instagram/'] = route('boiler.user.views_social.InstagramHandle', 'social.instagram.handle')
user_urls['/login/social/finalize/'] = route('boiler.user.views_social.FinalizeSocial', 'social.finalize', ['GET', 'POST'])

# profile
user_urls['/me/'] = route('boiler.user.views_profile.Me', 'user.me')
user_urls['/user/<int:id>/'] = route('boiler.user.views_profile.ProfileHome', 'user.profile.home')
user_urls['/user/<int:id>/email/'] = route('boiler.user.views_profile.ProfileEmailChange', 'user.profile.email', ['GET', 'POST'])
user_urls['/user/<int:id>/email/resend/'] = route('boiler.user.views_profile.ProfileConfirmEmailResend', 'user.profile.email.confirm.resend')
user_urls['/user/<int:id>/password/'] = route('boiler.user.views_profile.ProfilePasswordChange', 'user.profile.password', ['GET', 'POST'])
user_urls['/user/<int:id>/social/'] = route('boiler.user.views_profile.ProfileSocial', 'user.profile.social')
user_urls['/user/social/connect-facebook/'] = route('boiler.user.views_profile.ProfileSocialConnectFacebook', 'user.social.connect.facebook')
user_urls['/user/social/connect-google/'] = route('boiler.user.views_profile.ProfileSocialConnectGoogle', 'user.social.connect.google')
user_urls['/user/social/connect-twitter/'] = route('boiler.user.views_profile.ProfileSocialConnectTwitter', 'user.social.connect.twitter')
user_urls['/user/social/connect-vkontakte/'] = route('boiler.user.views_profile.ProfileSocialConnectVkontakte', 'user.social.connect.vkontakte')
user_urls['/user/social/connect-instagram/'] = route('boiler.user.views_profile.ProfileSocialConnectInstagram', 'user.social.connect.instagram')