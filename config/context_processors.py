import environ

env = environ.Env(
    DEBUG=(bool, False),
    GA_TRACKING_ID=(str, ''),
)


def is_debug(request):
    return {'is_debug': env('DEBUG')}


def ga_tracking_id(request):
    return {'ga_tracking_id': env('GA_TRACKING_ID')}
