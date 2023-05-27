from necrotopia_project.settings import GLOBAL_SITE_NAME


def get_common_context(request):
    return {
        'app_name': GLOBAL_SITE_NAME
    }
